#!/usr/bin/env python3
"""
Enhanced Property Manager – Check existence, create property, add electricity data.
Options: Check, Create, Add Data, Exit.
"""

import mariadb
import sys
import json
import urllib.request
import ssl
from datetime import datetime

# ===== CONFIGURATION =====
DB_USER = "e2501621"
DB_PASSWORD = "dYPXDAnuaw8"
DB_HOST = "mariadb.vamk.fi"
DB_PORT = 3306
DB_NAME = "e2501621_database"
BASE_URL = "https://www.cc.puv.fi/~jd/databases/data/"
# =========================

ssl_context = ssl._create_unverified_context()

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
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

def property_exists(conn, code):
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, location FROM property WHERE code = ?", (code,))
    result = cursor.fetchone()
    cursor.close()
    return result  # (id, name, location) or None

def create_property(conn, code, name, location):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO property (code, name, location) VALUES (?, ?, ?)",
            (code, name, location)
        )
        conn.commit()
        new_id = cursor.lastrowid
        print(f"✅ Property '{code}' created with ID {new_id}.")
        return new_id
    except mariadb.IntegrityError:
        print(f"❌ Property code '{code}' already exists.")
        return None
    except mariadb.Error as e:
        print(f"❌ Database error: {e}")
        return None
    finally:
        cursor.close()

def fetch_json_data(property_code):
    url = BASE_URL + property_code + ".json"
    try:
        with urllib.request.urlopen(url, context=ssl_context) as response:
            data = json.loads(response.read())
        print(f"✅ Fetched {len(data)} readings from {url}")
        return data
    except Exception as e:
        print(f"❌ Failed to fetch JSON data: {e}")
        return None

def add_electricity_data(conn, property_id, readings):
    cursor = conn.cursor()
    inserted = 0
    for r in readings:
        timestamp = r['timestamp'].replace('T', ' ')
        value = r['value'] if r['value'] is not None else 0.0
        try:
            cursor.execute(
                "INSERT INTO electricity (property, timestamp, value) VALUES (?, ?, ?)",
                (property_id, timestamp, value)
            )
            inserted += 1
        except mariadb.IntegrityError:
            print(f"⚠️ Duplicate entry for {timestamp}, skipping.")
        except mariadb.Error as e:
            print(f"❌ Error inserting at {timestamp}: {e}")
            conn.rollback()
            cursor.close()
            return 0
    conn.commit()
    cursor.close()
    return inserted

def main():
    conn = get_connection()
    print("\n=== ENHANCED PROPERTY MANAGER ===\n")

    while True:
        print("Options:")
        print("  1. Check if a property exists")
        print("  2. Create a new property")
        print("  3. Add electricity data for a property")
        print("  4. Exit")
        choice = input("Enter your choice (1-4): ").strip()

        if choice == '1':
            code = input("Enter property code to check: ").strip()
            result = property_exists(conn, code)
            if result:
                prop_id, name, location = result
                print(f"✅ Property EXISTS!")
                print(f"   ID: {prop_id}, Code: {code}, Name: {name}, Location: {location}")
            else:
                print(f"❌ Property '{code}' NOT found.")

        elif choice == '2':
            code = input("Enter new property code: ").strip()
            if property_exists(conn, code):
                print(f"❌ Property '{code}' already exists. Cannot create duplicate.")
                continue
            name = input("Enter property name: ").strip()
            location = input("Enter location: ").strip()
            if not name or not location:
                print("❌ Name and location cannot be empty.")
                continue
            create_property(conn, code, name, location)

        elif choice == '3':
            code = input("Enter property code to add electricity data: ").strip()
            result = property_exists(conn, code)
            if not result:
                print(f"❌ Property '{code}' does not exist. Please create it first (option 2).")
                continue
            prop_id, name, location = result
            print(f"ℹ️  Using property: {name} (ID: {prop_id})")
            data = fetch_json_data(code)
            if data:
                print(f"Inserting {len(data)} readings...")
                inserted = add_electricity_data(conn, prop_id, data)
                print(f"✅ Successfully inserted {inserted} new readings.")
            else:
                print("❌ Could not fetch data. Aborting.")

        elif choice == '4':
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter 1-4.")

    conn.close()

if __name__ == "__main__":
    main()
