import sqlite3
import json
import os
import sys


def parse_entitlements_db(db_file):
    output_dir = "./outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    games_list = {}
    themes_list = {}
    additional_content = {}
    additional_license = {}
    broken = {}

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
                number = int(table.split("_")[1])
                user_id = f"{number:x}"

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
                        if user_id not in themes_list:
                            themes_list[user_id] = {"active": [], "inactive": []}
                        if entry["active"]:
                            themes_list[user_id]["active"].append(entry)
                        else:
                            themes_list[user_id]["inactive"].append(entry)

                    # Games (PS4GD = Game Digital)
                    elif pkg_type == 'PS4GD':
                        if user_id not in games_list:
                            games_list[user_id] = {"active": [], "inactive": []}
                        if entry["active"]:
                            games_list[user_id]["active"].append(entry)
                        else:
                            games_list[user_id]["inactive"].append(entry)

                    # Additional Content
                    elif pkg_type == 'PS4AC':
                        if user_id not in additional_content:
                            additional_content[user_id] = {"active": [], "inactive": []}
                        if entry["active"]:
                            additional_content[user_id]["active"].append(entry)
                        else:
                            additional_content[user_id]["inactive"].append(entry)

                    # Additional License
                    elif pkg_type == 'PS4AL':
                        if user_id not in additional_license:
                            additional_license[user_id] = {"active": [], "inactive": []}
                        if entry["active"]:
                            additional_license[user_id]["active"].append(entry)
                        else:
                            additional_license[user_id]["inactive"].append(entry)

                    else:
                        if user_id not in broken:
                            broken[user_id] = {"active": [], "inactive": []}
                        if entry["active"]:
                            broken[user_id]["active"].append(entry)
                        else:
                            broken[user_id]["inactive"].append(entry)
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
    write_json(os.path.join(output_dir, 'additional_license.json'), additional_license)
    write_json(os.path.join(output_dir, 'broken.json'), broken)

    total_games = {
        "total_users": len(games_list),
        "total_active": sum(len(user["active"]) for user in games_list.values()),
        "total_inactive": sum(len(user["inactive"]) for user in games_list.values())
    }
    total_themes = {
        "total_users": len(themes_list),
        "total_active": sum(len(theme["active"]) for theme in themes_list.values()),
        "total_inactive": sum(len(theme["inactive"]) for theme in themes_list.values())
    }
    total_additional_content = {
        "total_users": len(additional_content),
        "total_active": sum(len(ac["active"]) for ac in additional_content.values()),
        "total_inactive": sum(len(ac["inactive"]) for ac in additional_content.values())
    }
    total_additional_license = {
        "total_users": len(additional_license),
        "total_active": sum(len(al["active"]) for al in additional_license.values()),
        "total_inactive": sum(len(al["inactive"]) for al in additional_license.values())
    }
    total_broken = {
        "total_users": len(broken),
        "total_active": sum(len(b["active"]) for b in broken.values()),
        "total_inactive": sum(len(b["inactive"]) for b in broken.values())
    }

    print(f"Done! Processed {total_rows} entries")
    print(f"Found {total_games['total_users']} user(s) with Game titles, and in total {total_games['total_active']} active and {total_games['total_inactive']} inactive games.")
    print(f"Found {total_themes['total_users']} user(s) with Theme titles, and in total {total_themes['total_active']} active and {total_themes['total_inactive']} inactive games.")
    print(f"Found {total_additional_content['total_users']} user(s) with Additional Content titles, and in total {total_additional_content['total_active']} active and {total_additional_content['total_inactive']} inactive games.")
    print(f"Found {total_additional_license['total_users']} user(s) with Additional License titles, and in total {total_additional_license['total_active']} active and {total_additional_license['total_inactive']} inactive games.")
    print(f"Found {total_broken['total_users']} user(s) with Broken titles, and in total {total_broken['total_active']} active and {total_broken['total_inactive']} inactive games.")
    print(f"Files saved in {output_dir}/")

def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_db>")
    else:
        parse_entitlements_db(sys.argv[1])