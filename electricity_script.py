import json
import urllib.request
import ssl

# --- IMPORTANT: REPLACE 1234 WITH THE PROPERTY ID YOU FOUND ---
PROPERTY_ID = 858   # <--- CHANGE THIS TO THE ACTUAL ID

# --- Bypass SSL certificate verification (if needed) ---
ssl_context = ssl._create_unverified_context()

# 1. Fetch the electricity JSON data from the URL
url = "https://www.cc.puv.fi/~jd/databases/data/091-010-0669-0001.json"
with urllib.request.urlopen(url, context=ssl_context) as response:
    readings = json.loads(response.read())

# 2. Generate SQL INSERT statements
sql_file = "insert_electricity.sql"
with open(sql_file, "w") as f:
    f.write(f"INSERT INTO electricity (property, timestamp, value) VALUES\n")
    values = []
    for r in readings:
        # Convert timestamp from "2025-01-01T00:00:00" to "2025-01-01 00:00:00"
        timestamp = r['timestamp'].replace('T', ' ')
        value = r['value'] if r['value'] is not None else 0  # handle possible nulls
        values.append(f"({PROPERTY_ID}, '{timestamp}', {value})")
    f.write(",\n".join(values) + ";\n")

print(f"✅ SQL file '{sql_file}' generated successfully with {len(readings)} readings!")