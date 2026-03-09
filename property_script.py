import json
import urllib.request
import ssl

# --- Bypass SSL certificate verification ---
ssl_context = ssl._create_unverified_context()

# 1. Fetch the JSON data from the URL
url = "https://www.cc.puv.fi/~jd/databases/data/properties.json"
with urllib.request.urlopen(url, context=ssl_context) as response:
    properties = json.loads(response.read())

# 2. Generate SQL INSERT statements
sql_file = "insert_properties.sql"
with open(sql_file, "w") as f:
    f.write("INSERT INTO property (code, name, location) VALUES\n")
    values = []
    for p in properties:
        # Handle None values by converting to empty string
        code = p['propertyCode'] if p['propertyCode'] is not None else ''
        name = p['propertyName'] if p['propertyName'] is not None else ''
        location = p['locationName'] if p['locationName'] is not None else ''
        
        # Escape single quotes by doubling them
        code = str(code).replace("'", "''")
        name = str(name).replace("'", "''")
        location = str(location).replace("'", "''")
        
        values.append(f"('{code}', '{name}', '{location}')")
    
    f.write(",\n".join(values) + ";\n")

print(f"✅ SQL file '{sql_file}' generated successfully!")