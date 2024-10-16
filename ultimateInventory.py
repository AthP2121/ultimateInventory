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

# Function to search components with prioritized fields
def search_components():
    keyword = input("Enter keyword to search for: ")
    found = False  # Track if any results are found

    # Search by name
    cursor.execute('SELECT * FROM components WHERE name LIKE ?', (f'%{keyword}%',))
    name_results = cursor.fetchall()
    if name_results:
        print("\nSearch Results for Name:")
        for row in name_results:
            print(f"ID: {row[0]}, Name: {row[1]}, Quantity: {row[2]}, Location: {row[3]}, Category: {row[4]}")
        found = True
    else:
        print("No results found for Name search.")

    # Search by category if no results found for name
    if not found:
        cursor.execute('SELECT * FROM components WHERE category LIKE ?', (f'%{keyword}%',))
        category_results = cursor.fetchall()
        if category_results:
            print("\nSearch Results for Category:")
            for row in category_results:
                print(f"ID: {row[0]}, Name: {row[1]}, Quantity: {row[2]}, Location: {row[3]}, Category: {row[4]}")
            found = True
        else:
            print("No results found for Category search.")

    # Search by location if no results found for name or category
    if not found:
        cursor.execute('SELECT * FROM components WHERE location LIKE ?', (f'%{keyword}%',))
        location_results = cursor.fetchall()
        if location_results:
            print("\nSearch Results for Location:")
            for row in location_results:
                print(f"ID: {row[0]}, Name: {row[1]}, Quantity: {row[2]}, Location: {row[3]}, Category: {row[4]}")
            found = True
        else:
            print("No results found for Location search.")

    # Search by quantity if no results found and keyword is a number
    if not found:
        try:
            quantity = int(keyword)
            cursor.execute('SELECT * FROM components WHERE quantity = ?', (quantity,))
            quantity_results = cursor.fetchall()
            if quantity_results:
                print("\nSearch Results for Quantity:")
                for row in quantity_results:
                    print(f"ID: {row[0]}, Name: {row[1]}, Quantity: {row[2]}, Location: {row[3]}, Category: {row[4]}")
                found = True
            else:
                print("No results found for Quantity search.")
        except ValueError:
            # Skip quantity search if keyword is not a number
            print("Skipping Quantity search because the keyword is not a number.")

    if not found:
        print("\nNo results found in any field.\n")
    else:
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
