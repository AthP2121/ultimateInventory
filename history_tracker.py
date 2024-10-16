# history_tracker.py
import sqlite3
from datetime import datetime

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
        print("\nComponent History:")
        print("ID | Component ID | Action | Timestamp | Old Quantity | New Quantity")
        print("-" * 60)
        for row in rows:
            print(row)
    else:
        print("\nNo history found for this component.")
