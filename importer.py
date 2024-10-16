# importer.py
import sqlite3
import os
import csv
import sys
from history_tracker import log_component_history

# Define paths for the database and import file
base_dir = os.path.dirname(os.path.abspath(sys.executable))  # Path relative to this script's directory
db_path = os.path.join(base_dir, 'stocktake.db')
csv_path = os.path.join(base_dir, 'components_import.csv')

# Function to create a template CSV file
def create_template_csv():
    print("Template CSV file not found. Creating a new template...")
    with open(csv_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['name', 'quantity', 'location', 'category', 'value'])
    print(f"Template CSV file created at {csv_path}. Please fill it and run the import again.")

# Function to import data from CSV file
def import_from_csv():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if not os.path.exists(csv_path):
        create_template_csv()
        conn.close()
        return

    print("Found CSV file. Starting import...")
    imported, updated, errors = 0, 0, 0

    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != ['name', 'quantity', 'location', 'category', 'value']:
            print("Error: CSV headers are incorrect. Should be: name, quantity, location, category, value.")
            conn.close()
            return

        for row in reader:
            try:
                name = row['name']
                quantity = int(row['quantity'])
                location = row['location']
                category = row['category']
                value = row['value']

                cursor.execute('SELECT id, quantity FROM components WHERE name = ? AND value = ? AND location = ?', 
                               (name, value, location))
                result = cursor.fetchone()

                if result:
                    component_id, old_quantity = result
                    new_quantity = old_quantity + quantity
                    cursor.execute('UPDATE components SET quantity = ? WHERE id = ?', (new_quantity, component_id))
                    log_component_history(conn, component_id, "Updated by import", old_quantity, new_quantity)
                    updated += 1
                else:
                    cursor.execute('INSERT INTO components (name, quantity, location, category, value) VALUES (?, ?, ?, ?, ?)', 
                                   (name, quantity, location, category, value))
                    component_id = cursor.lastrowid
                    log_component_history(conn, component_id, "Added by import", None, quantity)
                    imported += 1

                conn.commit()
                print(f"Processed component '{name}' with value '{value}' successfully.")
            except ValueError:
                print(f"Error: Quantity for component '{row.get('name', 'Unknown')}' must be a whole number.")
                errors += 1
            except KeyError:
                print("Error: Missing required data in CSV file. Please check the format.")
                errors += 1
            except sqlite3.IntegrityError:
                print(f"Error: Database integrity issue with component '{name}'.")
                errors += 1

    conn.close()
    print(f"Import completed. {imported} components added, {updated} components updated, {errors} errors encountered.")
