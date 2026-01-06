import sqlite3
import json
import os
import sys

def parse_entitlements_db(db_file):
    output_dir = "./outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    games_list = []
    themes_list = []

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Find all tables that look like 'entitlement_%'
        # The database could have many tables, which all begin with entitlement_ and an number
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
                    if not json_content:
                        continue

                    try:
                        data = json.loads(json_content)
                    except json.JSONDecodeError:
                        continue

                    # Extract metadata
                    game_meta = data.get('game_meta', {})
                    pkg_type = game_meta.get('type') or game_meta.get('package_type')
                    sub_type = game_meta.get('package_sub_type')
                    
                    # Extract download details
                    pkg_url = None
                    pkg_size = 0
                    
                    attributes = data.get('entitlement_attributes')
                    if attributes and isinstance(attributes, list) and len(attributes) > 0:
                        pkg_url = attributes[0].get('reference_package_url')
                        pkg_size = attributes[0].get('package_file_size', 0)

                    # Make an entry object
                    entry = {
                        "name": game_meta.get('name', 'Unknown'),
                        "id": data.get('id'),
                        "active": data.get('active_flag', False),
                        "size_gb": round(pkg_size / (1024**3), 2) if pkg_size else 0,
                        "pkg_url": pkg_url,
                        "license_expired": True if data.get('inactive_date') else False,
                        "is_ps_plus": data.get('freePsPlusContent', False)
                    }
                    
                    # Themes
                    if sub_type == 'MISC_THEME':
                        themes_list.append(entry)
                    
                    # Games (PS4GD = Game Digital)
                    elif pkg_type == 'PS4GD':
                        games_list.append(entry)
                    
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

    # Write Outputs
    write_json(os.path.join(output_dir, 'games.json'), games_list)
    write_json(os.path.join(output_dir, 'themes.json'), themes_list)

    print(f"Done! Processed {total_rows} entries")
    print(f"Found {len(games_list)} games")
    print(f"Found {len(themes_list)} themes")
    print(f"Files saved in {output_dir}/")

def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

parse_entitlements_db(sys.argv[1])
