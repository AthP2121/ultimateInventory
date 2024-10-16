# history_tracker.py
import sqlite3
from datetime import datetime
from colorama import Fore, Style, init
import os

# Initialize colorama for cross-platform color support
init(autoreset=True)

# Helper function to get the current terminal width
def get_terminal_width():
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80  # Default width if unable to get terminal size

# Function to log changes in component history
def log_component_history(conn, component_id, action, old_quantity=None, new_quantity=None):
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS component_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        component_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        old_quantity INTEGER,
        new_quantity INTEGER,
        FOREIGN KEY (component_id) REFERENCES components(id)
    )
    ''')
    cursor.execute('''
    INSERT INTO component_history (component_id, action, timestamp, old_quantity, new_quantity)
    VALUES (?, ?, ?, ?, ?)
    ''', (component_id, action, timestamp, old_quantity, new_quantity))
    conn.commit()

# Function to retrieve and display component history
def view_component_history(conn, component_id):
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, component_id, action, timestamp, old_quantity, new_quantity
    FROM component_history
    WHERE component_id = ?
    ORDER BY timestamp DESC
    ''', (component_id,))
    rows = cursor.fetchall()

    if rows:
        # Get the terminal width and calculate column widths
        width = get_terminal_width()
        col_width = max(10, width // 6)

        # Print the header with adaptive width
        print(Fore.CYAN + Style.BRIGHT + "\nComponent History:")
        print(Fore.GREEN + Style.BRIGHT + f"{'ID':<{col_width}} {'Component ID':<{col_width}} {'Action':<{col_width}} {'Timestamp':<{col_width}} {'Old Quantity':<{col_width}} {'New Quantity':<{col_width}}")
        print(Fore.GREEN + "═" * width)
        
        # Print each row with adaptive width
        for row in rows:
            row_id, comp_id, action, timestamp, old_qty, new_qty = row
            print(Fore.YELLOW + f"{row_id:<{col_width}} {comp_id:<{col_width}} {action:<{col_width}} {timestamp:<{col_width}} {str(old_qty):<{col_width}} {str(new_qty):<{col_width}}")
        
        # Print a separator line at the end
        print(Fore.CYAN + "─" * width)
    else:
        print(Fore.RED + "\nNo history found for this component.")
