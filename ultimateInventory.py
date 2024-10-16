import sqlite3
import os
import sys

# Define the path relative to the executable's directory
base_dir = os.path.dirname(os.path.abspath(sys.executable))
db_path = os.path.join(base_dir, 'stocktake.db')

# Connect to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Ensure the components table exists
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

# Function to add a new component
def add_component():
    name = input("Enter component name: ")
    while True:
        try:
            quantity = int(input("Enter quantity (whole number): "))
            break
        except ValueError:
            print("Error: Quantity must be a whole number (integer). Please try again.")
    location = input("Enter location: ")
    category = input("Enter category: ")
    cursor.execute('''
    INSERT INTO components (name, quantity, location, category)
    VALUES (?, ?, ?, ?)
    ''', (name, quantity, location, category))
    conn.commit()
    print(f"Component '{name}' added successfully.\n")

# Function to remove a component by name
def remove_component():
    name = input("Enter component name to remove: ")
    cursor.execute('''
    DELETE FROM components
    WHERE name = ?
    ''', (name,))
    conn.commit()
    print(f"Component '{name}' removed successfully.\n")

# Function to update the quantity of a component
def update_component():
    name = input("Enter component name to update: ")
    while True:
        try:
            quantity = int(input("Enter new quantity (whole number): "))
            break
        except ValueError:
            print("Error: Quantity must be a whole number (integer). Please try again.")
    cursor.execute('''
    UPDATE components
    SET quantity = ?
    WHERE name = ?
    ''', (quantity, name))
    conn.commit()
    print(f"Component '{name}' updated successfully.\n")

# Function to view all components
def view_components():
    cursor.execute('SELECT * FROM components')
    rows = cursor.fetchall()
    print("\nStocktake Inventory:")
    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]}, Quantity: {row[2]}, Location: {row[3]}, Category: {row[4]}")
    print()

# Function to search components with a wildcard
def search_components():
    keyword = input("Enter keyword to search for (partial matches allowed): ")
    # Wildcard search with % for any match before/after the keyword
    cursor.execute('''
    SELECT * FROM components
    WHERE name LIKE ? OR location LIKE ? OR category LIKE ?
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
    results = cursor.fetchall()
    if results:
        print("\nSearch Results:")
        for row in results:
            print(f"ID: {row[0]}, Name: {row[1]}, Quantity: {row[2]}, Location: {row[3]}, Category: {row[4]}")
    else:
        print("No matching components found.")
    print()

# Main loop to run the terminal application
def main():
    while True:
        print("Stocktake Inventory Management")
        print("1. Add Component")
        print("2. Remove Component")
        print("3. Update Component")
        print("4. View Components")
        print("5. Search Components")
        print("6. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            add_component()
        elif choice == '2':
            remove_component()
        elif choice == '3':
            update_component()
        elif choice == '4':
            view_components()
        elif choice == '5':
            search_components()
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please select a valid option (1-6).\n")

    # Close the connection when exiting the application
    conn.close()
    print("Exiting the application.")

if __name__ == '__main__':
    main()
