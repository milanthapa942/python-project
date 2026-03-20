#!/usr/bin/env python3
import mariadb
import sys

# Database credentials
DB_USER = "e2501621"
DB_PASSWORD = "dYPXDAnuaw8"   # <-- Updated password
DB_HOST = "mariadb.vamk.fi"
DB_PORT = 3306
DB_NAME = "e2501621_database"

def get_property_code():
    """Return property code from command line or prompt user."""
    if len(sys.argv) == 2:
        return sys.argv[1]
    elif len(sys.argv) > 2:
        print("❌ Too many arguments.")
        print("Usage: python check_property.py [property_code]")
        sys.exit(1)
    else:
        # No argument given – ask user
        code = input("Enter property code to check: ").strip()
        if not code:
            print("❌ No code entered.")
            sys.exit(1)
        return code

try:
    # Connect to database
    conn = mariadb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )
    cursor = conn.cursor()

    # Get property code
    property_code = get_property_code()

    # Check if property exists
    cursor.execute("SELECT id, name, location FROM property WHERE code = ?", (property_code,))
    result = cursor.fetchone()

    if result:
        prop_id, prop_name, prop_location = result
        print(f"✅ PROPERTY EXISTS!")
        print(f"   ID:       {prop_id}")
        print(f"   Code:     {property_code}")
        print(f"   Name:     {prop_name}")
        print(f"   Location: {prop_location}")
    else:
        print(f"❌ Property '{property_code}' NOT found in database.")

    cursor.close()
    conn.close()

except mariadb.Error as e:
    print(f"Database error: {e}")
