import sqlite3
import json
import os
import sys


def parse_entitlements_db(db_file):
    output_dir = "./outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    games_list = {
        "active": [],
        "inactive": []
    }

    themes_list = {
        "active": [],
        "inactive": []
    }

    additional_content = {
        "active": [],
        "inactive": []
    }

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'entitlement_%'")
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            print("No entitlement tables found in the database.")
            conn.close()
            return

        total_rows = 0

        for table in tables:
            try:
                cursor.execute(f"SELECT JSON FROM {table}")
                rows = cursor.fetchall()

                for row in rows:
                    json_content = row[0]
                    data = json.loads(json_content)

                    # Extract metadata
                    game_meta = data.get('game_meta', {})
                    pkg_type = game_meta.get('type') or game_meta.get('package_type')
                    sub_type = game_meta.get('package_sub_type')

                    # Extract details
                    pkg_url = None
                    pkg_size = 0

                    attributes = data.get('entitlement_attributes')
                    if attributes and isinstance(attributes, list) and len(attributes) > 0:
                        pkg_url = attributes[0].get('reference_package_url')
                        pkg_size = attributes[0].get('package_file_size', 0)

                    entry = {
                        "name": game_meta.get('name', 'Unknown'),
                        "icon": game_meta.get('icon_url','Not Found'),
                        "id": data.get('id'),
                        "active": data.get('active_flag', False),
                        "hasRif": data.get('hasRif', None),
                        "size": round(pkg_size / (1024 ** 3), 2) if pkg_size else 0,
                        "pkg_url": pkg_url,
                        "license_expired": True if data.get('inactive_date') else False,
                        "is_ps_plus": data.get('freePsPlusContent', False)
                    }

                    # Themes
                    if sub_type == 'MISC_THEME':
                        if entry["active"]:
                            themes_list["active"].append(entry)
                        else:
                            themes_list["inactive"].append(entry)

                    # Games (PS4GD = Game Digital)
                    elif pkg_type == 'PS4GD':
                        if entry["active"]:
                            games_list["active"].append(entry)
                        else:
                            games_list["inactive"].append(entry)

                    elif pkg_type == 'PS4AC':
                        if entry["active"]:
                            additional_content["active"].append(entry)
                        else:
                            additional_content["inactive"].append(entry)

                    total_rows += 1
            except sqlite3.OperationalError as e:
                print(f"Skipping table {table}: {e}")

        conn.close()

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return

    write_json(os.path.join(output_dir, 'games.json'), games_list)
    write_json(os.path.join(output_dir, 'themes.json'), themes_list)
    write_json(os.path.join(output_dir, 'additional_content.json'), additional_content)

    total_games = len(games_list["active"]) + len(games_list["inactive"])
    total_themes = len(themes_list["active"]) + len(themes_list["inactive"])
    total_additional_content = len(additional_content["active"]) + len(additional_content["inactive"])

    print(f"Done! Processed {total_rows} entries.")
    print(f"Found {total_games} games ({len(games_list['active'])} active)")
    print(f"Found {total_themes} themes ({len(themes_list['active'])} active)")
    print(f"Found {total_additional_content} additional content")
    print(f"Files saved in {output_dir}/")

def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_db>")
    else:
        parse_entitlements_db(sys.argv[1])