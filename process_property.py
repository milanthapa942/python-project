#!/usr/bin/env python3
import json
import urllib.request
import ssl
import mariadb
import sys

# Configuration
DB_USER = "e2501621"
DB_PASSWORD = "dYPXDAnuaw8"
DB_HOST = "mariadb.vamk.fi"
DB_PORT = 3306
DB_NAME = "e2501621_database"

# The property code from the filename
property_code = "091-038-9904-0001"
json_url = f"https://www.cc.puv.fi/~jd/databases/data/{property_code}.json"

ssl_context = ssl._create_unverified_context()

def get_connection():
    try:
        return mariadb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
    except mariadb.Error as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

def main():
    print(f"🔍 Processing property code: {property_code}")
    
    # 1. Fetch JSON data
    try:
        with urllib.request.urlopen(json_url, context=ssl_context) as response:
            data = json.loads(response.read())
        print(f"✅ Fetched {len(data)} readings")
    except Exception as e:
        print(f"❌ Failed to fetch JSON: {e}")
        sys.exit(1)
    
    # Get property name from first record
    property_name = data[0]['locationName']
    print(f"📋 Property name: {property_name}")
    
    # 2. Connect to database
    conn = get_connection()
    cursor = conn.cursor()
    
    # 3. Check if property exists
    cursor.execute("SELECT id FROM property WHERE code = ?", (property_code,))
    result = cursor.fetchone()
    
    if result:
        property_id = result[0]
        print(f"✅ Property already exists with ID: {property_id}")
    else:
        print(f"❌ Property not found. Inserting new property...")
        cursor.execute(
            "INSERT INTO property (code, name, location) VALUES (?, ?, ?)",
            (property_code, property_name, property_name)
        )
        conn.commit()
        property_id = cursor.lastrowid
        print(f"✅ Inserted new property with ID: {property_id}")
    
    # 4. Insert electricity readings
    print(f"📊 Inserting electricity readings...")
    inserted = 0
    for record in data:
        timestamp = record['timestamp'].replace('T', ' ')
        value = record['value']
        try:
            cursor.execute(
                "INSERT INTO electricity (property, timestamp, value) VALUES (?, ?, ?)",
                (property_id, timestamp, value)
            )
            inserted += 1
        except mariadb.IntegrityError:
            print(f"⚠️ Duplicate: {timestamp} already exists")
    
    conn.commit()
    print(f"✅ Successfully inserted {inserted} new readings")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
