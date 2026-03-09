#!/usr/bin/env python3
# property.py - Manage properties in MariaDB (list/add/delete).
# Commands: L (list), A (add), D (delete), Q (quit)

import mariadb
import sys

# === CONFIGURATION – change if needed ===
DB_USER = "e2501621"
DB_PASSWORD = "D3JbX2zyp2N"
DB_HOST = "mariadb.vamk.fi"
DB_PORT = 3306
DB_NAME = "e2501621_database"          # or "e2501621_database"
# ========================================

def get_connection():
    try:
        conn = mariadb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        return conn
    except mariadb.Error as e:
        print(f"Database connection failed: {e}")
        sys.exit(1)

def ensure_table(conn):
    """Create the property table if it does not exist."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS property (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            location VARCHAR(255) NOT NULL
        )
    """)
    conn.commit()
    cursor.close()

def list_properties(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT code, name, location FROM property ORDER BY code")
    rows = cursor.fetchall()
    cursor.close()
    if not rows:
        print("\nNo properties found.")
    else:
        print("\nCurrent properties:")
        for code, name, location in rows:
            print(f"  Code: {code}, Name: {name}, Location: {location}")
    print()

def add_property(conn):
    code = input("Enter property code: ").strip()
    if not code:
        print("Error: Code cannot be empty.\n")
        return
    name = input("Enter property name: ").strip()
    if not name:
        print("Error: Name cannot be empty.\n")
        return
    location = input("Enter location: ").strip()
    if not location:
        print("Error: Location cannot be empty.\n")
        return

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO property (code, name, location) VALUES (?, ?, ?)",
            (code, name, location)
        )
        conn.commit()
        print(f"Property with code '{code}' added.\n")
    except mariadb.IntegrityError:
        print(f"Error: Code '{code}' already exists.\n")
    except mariadb.Error as e:
        print(f"Database error: {e}\n")
    finally:
        cursor.close()

def delete_property(conn):
    code = input("Enter property code to delete: ").strip()
    if not code:
        print("Error: Code cannot be empty.\n")
        return

    cursor = conn.cursor()
    cursor.execute("DELETE FROM property WHERE code = ?", (code,))
    deleted = cursor.rowcount
    conn.commit()
    cursor.close()

    if deleted:
        print(f"Property with code '{code}' deleted.\n")
    else:
        print(f"Error: Code '{code}' not found.\n")

def main():
    conn = get_connection()
    ensure_table(conn)

    print("=== Property Manager (Database version) ===\n")
    while True:
        print("Commands: (L)ist, (A)dd, (D)elete, (Q)uit")
        cmd = input("Enter command: ").strip().upper()
        if cmd == 'L':
            list_properties(conn)
        elif cmd == 'A':
            add_property(conn)
        elif cmd == 'D':
            delete_property(conn)
        elif cmd == 'Q':
            print("Goodbye!")
            break
        else:
            print("Invalid command. Please try again.\n")

    conn.close()

if __name__ == "__main__":
    main()