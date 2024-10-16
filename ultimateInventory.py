import sqlite3
import os
import sys
from colorama import Fore, Style, init
import getpass

# Import functions
from history_tracker import log_component_history, view_component_history
from importer import import_from_csv


# Initialize colorama for cross-platform color support
init(autoreset=True)

# Define the path relative to the executable's directory
base_dir = os.path.dirname(os.path.abspath(sys.executable))
db_path = os.path.join(base_dir, 'stocktake.db')

# Connect to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Password for accessing advanced options
ADVANCED_PASSWORD = "YourSecurePasswordHere"  # Replace with a strong password

# Create the components table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    location TEXT,
    category TEXT,
    value TEXT
)
''')
conn.commit()

# Helper function to get the current terminal width
def get_terminal_width():
    try:
        return os.get_terminal_size().columns
    except OSError:
        # Default width if terminal size can't be determined (e.g., in some IDEs or Windows versions)
        return 80

def print_header(title):
    width = get_terminal_width()
    print(Fore.CYAN + Style.BRIGHT + f"\n{'─' * width}")
    print(f"{title.center(width)}")
    print(f"{'─' * width}")

def print_separator():
    width = get_terminal_width()
    print(Fore.CYAN + "─" * width)

def print_table_header():
    width = get_terminal_width()
    col_width = max(10, width // 6)  # Adjust column width
    print(Fore.GREEN + Style.BRIGHT + f"{'ID':<{col_width}} {'Name':<{col_width}} {'Qty':<{col_width}} {'Location':<{col_width}} {'Category':<{col_width}} {'Value':<{col_width}}")
    print(Fore.GREEN + Style.BRIGHT + "═" * width)

def print_component(row):
    width = get_terminal_width()
    col_width = max(10, width // 6)  # Adjust column width
    print(Fore.YELLOW + f"{row[0]:<{col_width}} {row[1]:<{col_width}} {row[2]:<{col_width}} {row[3]:<{col_width}} {row[4]:<{col_width}} {row[5]:<{col_width}}")

# Function to add a new component
def add_component():
    print_header("Add New Component")
    name = input(Fore.CYAN + "Enter component name: ")
    quantity = int(input(Fore.CYAN + "Enter quantity (whole number): "))
    location = input(Fore.CYAN + "Enter location: ")
    category = input(Fore.CYAN + "Enter category: ")
    value = input(Fore.CYAN + "Enter value (e.g., resistance, capacitance, etc.): ")
    
    cursor.execute('''
    INSERT INTO components (name, quantity, location, category, value)
    VALUES (?, ?, ?, ?, ?)
    ''', (name, quantity, location, category, value))
    conn.commit()

    # Log the addition in the history
    component_id = cursor.lastrowid
    log_component_history(conn, component_id, "Added", None, quantity)

    print(Fore.GREEN + f"\nComponent '{name}' with value '{value}' added successfully!\n")

# Function to remove a component by name
def remove_component():
    print_header("Remove Component")
    name = input(Fore.CYAN + "Enter component name to remove: ")
    cursor.execute('SELECT id, quantity FROM components WHERE name = ?', (name,))
    result = cursor.fetchone()

    if result:
        component_id, old_quantity = result

        cursor.execute('''
        DELETE FROM components
        WHERE id = ?
        ''', (component_id,))
        conn.commit()

        # Log the deletion in the history
        log_component_history(conn, component_id, "Removed", old_quantity, None)

        print(Fore.GREEN + f"\nComponent '{name}' removed successfully!\n")
    else:
        print(Fore.RED + f"\nComponent '{name}' not found.\n")

# Function to update the quantity of a component
def update_component():
    print_header("Update Component Quantity")
    name = input(Fore.CYAN + "Enter component name to update: ")
    cursor.execute('SELECT id, quantity FROM components WHERE name = ?', (name,))
    result = cursor.fetchone()

    if result:
        component_id, old_quantity = result
        new_quantity = int(input(Fore.CYAN + "Enter new quantity (whole number): "))

        cursor.execute('''
        UPDATE components
        SET quantity = ?
        WHERE id = ?
        ''', (new_quantity, component_id))
        conn.commit()

        # Log the update in the history
        log_component_history(conn, component_id, "Updated", old_quantity, new_quantity)

        print(Fore.GREEN + f"\nComponent '{name}' updated successfully!\n")
    else:
        print(Fore.RED + f"\nComponent '{name}' not found.\n")

# Function to view the history of a component
def view_history():
    print_header("View Component History")
    component_id = int(input(Fore.CYAN + "Enter component ID to view history: "))
    view_component_history(conn, component_id)

# Function to view all components
def view_components():
    print_header("Inventory List")
    cursor.execute('SELECT * FROM components')
    rows = cursor.fetchall()
    print_table_header()
    for row in rows:
        print_component(row)
    print()

def search_components():
    print_header("Search Components")
    print(Fore.CYAN + "Search by specific field:")
    print(Fore.CYAN + "1. ID")
    print(Fore.CYAN + "2. Name")
    print(Fore.CYAN + "3. Category")
    print(Fore.CYAN + "4. Location")
    print(Fore.CYAN + "5. Quantity")
    print(Fore.CYAN + "Leave blank or press Enter to search all fields")
    
    choice = input(Fore.YELLOW + "Choose an option (1-5) or press Enter for all: ")
    keyword = input(Fore.CYAN + "Enter keyword to search for: ")
    found = False

    # Search by ID if chosen
    if choice == '1':
        try:
            item_id = int(keyword)
            cursor.execute('SELECT * FROM components WHERE id = ?', (item_id,))
            results = cursor.fetchall()
            if results:
                print_header("Results - ID")
                print_table_header()
                for row in results:
                    print_component(row)
                found = True
        except ValueError:
            print(Fore.RED + "Error: ID search requires a numeric keyword.")
    
    # Search by Name if chosen
    elif choice == '2':
        cursor.execute('SELECT * FROM components WHERE name LIKE ?', (f'%{keyword}%',))
        results = cursor.fetchall()
        if results:
            print_header("Results - Name")
            print_table_header()
            for row in results:
                print_component(row)
            found = True

    # Search by Category if chosen
    elif choice == '3':
        cursor.execute('SELECT * FROM components WHERE category LIKE ?', (f'%{keyword}%',))
        results = cursor.fetchall()
        if results:
            print_header("Results - Category")
            print_table_header()
            for row in results:
                print_component(row)
            found = True

    # Search by Location if chosen
    elif choice == '4':
        cursor.execute('SELECT * FROM components WHERE location LIKE ?', (f'%{keyword}%',))
        results = cursor.fetchall()
        if results:
            print_header("Results - Location")
            print_table_header()
            for row in results:
                print_component(row)
            found = True

    # Search by Quantity if chosen
    elif choice == '5':
        try:
            quantity = int(keyword)
            cursor.execute('SELECT * FROM components WHERE quantity = ?', (quantity,))
            results = cursor.fetchall()
            if results:
                print_header("Results - Quantity")
                print_table_header()
                for row in results:
                    print_component(row)
                found = True
        except ValueError:
            print(Fore.RED + "Error: Quantity search requires a numeric keyword.")

    # If no specific field was chosen, perform a search across all fields
    else:
        # General search logic as before
        # Search by ID (assuming the keyword is numeric)
        try:
            item_id = int(keyword)
            cursor.execute('SELECT * FROM components WHERE id = ?', (item_id,))
            results = cursor.fetchall()
            if results:
                print_header("Results - ID")
                print_table_header()
                for row in results:
                    print_component(row)
                found = True
        except ValueError:
            pass  # Skip if keyword is not numeric

        # Search by Name if not found
        if not found:
            cursor.execute('SELECT * FROM components WHERE name LIKE ?', (f'%{keyword}%',))
            results = cursor.fetchall()
            if results:
                print_header("Results - Name")
                print_table_header()
                for row in results:
                    print_component(row)
                found = True

        # Search by Category if not found
        if not found:
            cursor.execute('SELECT * FROM components WHERE category LIKE ?', (f'%{keyword}%',))
            results = cursor.fetchall()
            if results:
                print_header("Results - Category")
                print_table



# Advanced option: Direct SQL access with password protection
def advanced_options():
    password = getpass.getpass(Fore.YELLOW + "Enter password for advanced options: ")
    if password != ADVANCED_PASSWORD:
        print(Fore.RED + "Incorrect password. Access denied.")
        return
    
    print(Fore.GREEN + "Access granted to advanced options.")
    
    while True:
        print_header("Advanced Database Access")
        print(Fore.CYAN + "Type 'exit' to return to the main menu.")
        query = input(Fore.YELLOW + "Enter SQL command: ")
        
        if query.lower() == 'exit':
            break

        try:
            cursor.execute(query)
            conn.commit()
            results = cursor.fetchall()
            if results:
                print_separator()
                for row in results:
                    print(row)
                print_separator()
            else:
                print(Fore.GREEN + "Command executed successfully.")
        except sqlite3.Error as e:
            print(Fore.RED + f"An error occurred: {e}")

# Main loop to run the terminal application
def main():
    while True:
        print_header("Stocktake Inventory Management")
        print(Fore.CYAN + "1. Add Component")
        print(Fore.CYAN + "2. Remove Component")
        print(Fore.CYAN + "3. Update Component")
        print(Fore.CYAN + "4. View Components")
        print(Fore.CYAN + "5. Search Components")
        print(Fore.CYAN + "6. View Component History")
        print(Fore.CYAN + "7. Import Components from CSV")  # New option for import
        print(Fore.CYAN + "8. Advanced Options")
        print(Fore.CYAN + "9. Exit")
        choice = input(Fore.YELLOW + "Select an option: ")

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
            view_history()
        elif choice == '7':
            import_from_csv()  # Call the import function
        elif choice == '8':
            advanced_options()
        elif choice == '9':
            break
        else:
            print(Fore.RED + "Invalid choice. Please select a valid option (1-9).\n")

    conn.close()
    print(Fore.GREEN + "Exiting the application.")

    conn.close()
    print(Fore.GREEN + "Exiting the application.")

if __name__ == '__main__':
    main()
