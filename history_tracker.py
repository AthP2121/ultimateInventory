# history_tracker.py
import sqlite3
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama for cross-platform color support
init(autoreset=True)

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
        # Print a styled header
        print(Fore.CYAN + Style.BRIGHT + "\nComponent History:")
        print(Fore.GREEN + Style.BRIGHT + f"{'ID':<5} {'Component ID':<15} {'Action':<15} {'Timestamp':<20} {'Old Quantity':<15} {'New Quantity':<15}")
        print(Fore.GREEN + "═" * 80)
        
        # Print each row in a formatted manner
        for row in rows:
            row_id, comp_id, action, timestamp, old_qty, new_qty = row
            print(Fore.YELLOW + f"{row_id:<5} {comp_id:<15} {action:<15} {timestamp:<20} {str(old_qty):<15} {str(new_qty):<15}")
        
        # Print a separator line at the end
        print(Fore.CYAN + "─" * 80)
    else:
        print(Fore.RED + "\nNo history found for this component.")
