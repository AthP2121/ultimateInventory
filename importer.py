import sqlite3
import os
import csv
import sys

# Define paths for the database and import file
base_dir = os.path.dirname(os.path.abspath(sys.executable))  # For the compiled .exe
db_path = os.path.join(base_dir, 'stocktake.db')
csv_path = os.path.join(base_dir, 'components_import.csv')

# Debugging: Print paths to ensure correctness
print(f"Database path: {db_path}")
print(f"CSV path: {csv_path}")

# Connect to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the components table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    location TEXT,
    category TEXT
)
''')
conn.commit()

# Function to create a template CSV file
def create_template_csv():
    print("Template CSV file not found. Creating a new template...")
    with open(csv_path, 'w', newline='') as file:
        writer = csv.writer(file)
        # Write the headers
        writer.writerow(['name', 'quantity', 'location', 'category'])
    print(f"Template CSV file created at {csv_path}.")
    print("Please fill it with your component data and run this program again.")
    print("Each row should contain the component's name, quantity (as a whole number), location, and category.")

# Function to import data from CSV file
def import_from_csv():
    if not os.path.exists(csv_path):
        create_template_csv()
        return

    print("Found CSV file. Starting import...")
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        # Check for correct headers
        if reader.fieldnames != ['name', 'quantity', 'location', 'category']:
            print("Error: CSV file headers are incorrect.")
            print("Headers should be: name, quantity, location, category.")
            return

        # Import each row from the CSV file into the database
        for row in reader:
            try:
                name = row['name']
                quantity = int(row['quantity'])  # Convert quantity to integer
                location = row['location']
                category = row['category']

                cursor.execute('''
                INSERT INTO components (name, quantity, location, category)
                VALUES (?, ?, ?, ?)
                ''', (name, quantity, location, category))
                conn.commit()
                print(f"Imported component '{name}' successfully.")
            except ValueError:
                print(f"Error: Quantity for component '{row['name']}' must be a whole number.")
            except KeyError:
                print("Error: Missing required data in CSV file. Please check the format.")
    print("Import completed.")

# Main function to execute the importer
def main():
    print("Starting the Inventory Importer...")
    import_from_csv()
    conn.close()
    print("All tasks completed. Press any key to exit.")
    input()  # Keep the terminal open until a key is pressed

if __name__ == '__main__':
    main()
