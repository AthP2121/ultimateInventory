import sqlite3
import os
import sys
import signal
from colorama import Fore, Style, init

# Initialize colorama for Windows compatibility
init(autoreset=True)

# Define the path relative to the executable's directory
base_dir = os.path.dirname(os.path.abspath(sys.executable))
db_path = os.path.join(base_dir, 'stocktake.db')

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
    category TEXT,
    value TEXT
)
''')
conn.commit()

# Helper function to get terminal width, refreshed each time called
def get_terminal_width():
    return os.get_terminal_size().columns

# Signal handler for window resize to dynamically update terminal width
current_width = get_terminal_width()

def handle_resize(signum, frame):
    global current_width
    current_width = get_terminal_width()

signal.signal(signal.SIGWINCH, handle_resize)

def print_header(title):
    print(Fore.CYAN + Style.BRIGHT + f"\n{'─' * current_width}")
    print(f"{title.center(current_width)}")
    print(f"{'─' * current_width}")

def print_separator():
    print(Fore.CYAN + "─" * current_width)

def print_table_header():
    col_width = max(8, (current_width - 4) // 5)  # Adjust column width
    print(Fore.GREEN + Style.BRIGHT + f"{'ID':<{col_width}} {'Name':<{col_width}} {'Qty':<{col_width}} {'Location':<{col_width}} {'Category':<{col_width}} {'Value':<{col_width}}")
    print(Fore.GREEN + Style.BRIGHT + "═" * current_width)

def print_component(row):
    col_width = max(8, (current_width - 4) // 5)  # Adjust column width
    print(Fore.YELLOW + f"{row[0]:<{col_width}} {row[1]:<{col_width}} {row[2]:<{col_width}} {row[3]:<{col_width}} {row[4]:<{col_width}} {row[5]:<{col_width}}")

# Function to add a new component
def add_component():
    print_header("Add New Component")
    name = input(Fore.CYAN + "Enter component name: ")
    while True:
        try:
            quantity = int(input(Fore.CYAN + "Enter quantity (whole number): "))
            break
        except ValueError:
            print(Fore.RED + "Error: Quantity must be a whole number. Please try again.")
    location = input(Fore.CYAN + "Enter location: ")
    category = input(Fore.CYAN + "Enter category: ")
    value = input(Fore.CYAN + "Enter value (e.g., resistance, capacitance, etc.): ")
    
    cursor.execute('''
    INSERT INTO components (name, quantity, location, category, value)
    VALUES (?, ?, ?, ?, ?)
    ''', (name, quantity, location, category, value))
    conn.commit()
    print(Fore.GREEN + f"\nComponent '{name}' with value '{value}' added successfully!\n")

# Function to remove a component by name
def remove_component():
    print_header("Remove Component")
    name = input(Fore.CYAN + "Enter component name to remove: ")
    cursor.execute('''
    DELETE FROM components
    WHERE name = ?
    ''', (name,))
    conn.commit()
    print(Fore.GREEN + f"\nComponent '{name}' removed successfully!\n")

# Function to update the quantity of a component
def update_component():
    print_header("Update Component Quantity")
    name = input(Fore.CYAN + "Enter component name to update: ")
    while True:
        try:
            quantity = int(input(Fore.CYAN + "Enter new quantity (whole number): "))
            break
        except ValueError:
            print(Fore.RED + "Error: Quantity must be a whole number. Please try again.")
    
    cursor.execute('''
    UPDATE components
    SET quantity = ?
    WHERE name = ?
    ''', (quantity, name))
    conn.commit()
    print(Fore.GREEN + f"\nComponent '{name}' updated successfully!\n")

# Function to view all components
def view_components():
    print_header("Inventory List")
    cursor.execute('SELECT * FROM components')
    rows = cursor.fetchall()
    print_table_header()
    for row in rows:
        print_component(row)
    print()

# Function to search components with prioritized fields
def search_components():
    print_header("Search Components")
    keyword = input(Fore.CYAN + "Enter keyword to search for: ")
    found = False

    # Search by name
    cursor.execute('SELECT * FROM components WHERE name LIKE ?', (f'%{keyword}%',))
    name_results = cursor.fetchall()
    if name_results:
        print_header("Results - Name")
        print_table_header()
        for row in name_results:
            print_component(row)
        found = True

    # Search by category if no results found for name
    if not found:
        cursor.execute('SELECT * FROM components WHERE category LIKE ?', (f'%{keyword}%',))
        category_results = cursor.fetchall()
        if category_results:
            print_header("Results - Category")
            print_table_header()
            for row in category_results:
                print_component(row)
            found = True

    # Search by location if no results found for name or category
    if not found:
        cursor.execute('SELECT * FROM components WHERE location LIKE ?', (f'%{keyword}%',))
        location_results = cursor.fetchall()
        if location_results:
            print_header("Results - Location")
            print_table_header()
            for row in location_results:
                print_component(row)
            found = True

    # Search by quantity if no results found and keyword is a number
    if not found:
        try:
            quantity = int(keyword)
            cursor.execute('SELECT * FROM components WHERE quantity = ?', (quantity,))
            quantity_results = cursor.fetchall()
            if quantity_results:
                print_header("Results - Quantity")
                print_table_header()
                for row in quantity_results:
                    print_component(row)
                found = True
        except ValueError:
            print(Fore.RED + "Skipping Quantity search because the keyword is not a number.")

    if not found:
        print(Fore.RED + "\nNo results found in any field.\n")

# Main loop to run the terminal application
def main():
    while True:
        print_header("Stocktake Inventory Management")
        print(Fore.CYAN + "1. Add Component")
        print(Fore.CYAN + "2. Remove Component")
        print(Fore.CYAN + "3. Update Component")
        print(Fore.CYAN + "4. View Components")
        print(Fore.CYAN + "5. Search Components")
        print(Fore.CYAN + "6. Exit")
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
            break
        else:
            print(Fore.RED + "Invalid choice. Please select a valid option (1-6).\n")

    conn.close()
    print(Fore.GREEN + "Exiting the application.")

if __name__ == '__main__':
    main()
