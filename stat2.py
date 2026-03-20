import mariadb
import sys
import argparse

# ===== CONFIGURATION =====
DB_USER = "e2501621"
DB_PASSWORD = "dYPXDAnuaw8"
DB_HOST = "mariadb.vamk.fi"
DB_PORT = 3306
DB_NAME = "e2501621_database"
# =========================

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
        print(f"❌ Cannot connect to database: {e}")
        sys.exit(1)

def get_property_id_from_code(conn, code):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM property WHERE code = ?", (code,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

def main():
    parser = argparse.ArgumentParser(description="Electricity statistics (min, max, sum)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--property", type=int, help="Property ID")
    group.add_argument("--code", type=str, help="Property code (e.g., 091-038-9904-0001)")
    parser.add_argument("--group", choices=["day", "month", "year"], default="day",
                        help="Group by day, month, or year (default: day). Ignored if --overall is used.")
    parser.add_argument("--overall", action="store_true",
                        help="Show overall statistics (one row) without grouping.")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    args = parser.parse_args()

    conn = get_connection()

    # Determine property ID
    property_id = args.property
    if args.code:
        fetched_id = get_property_id_from_code(conn, args.code)
        if not fetched_id:
            print(f"❌ Property with code '{args.code}' not found.")
            sys.exit(1)
        property_id = fetched_id
        print(f"ℹ️  Using property ID {property_id} for code '{args.code}'")
    elif property_id is None:
        property_id = 858  # default fallback (you can change or remove)
        print(f"ℹ️  Using default property ID {property_id}")

    cursor = conn.cursor()

    if args.overall:
        # Overall statistics: only min, max, sum
        query = """
            SELECT
                MIN(value) AS min_value,
                MAX(value) AS max_value,
                SUM(value) AS total_value
            FROM electricity
            WHERE property = ?
        """
    else:
        # Grouped statistics (including average)
        if args.group == "day":
            group_expr = "DATE(timestamp)"
        elif args.group == "month":
            group_expr = "DATE_FORMAT(timestamp, '%Y-%m')"
        else:  # year
            group_expr = "YEAR(timestamp)"

        query = f"""
            SELECT
                {group_expr} AS period,
                MIN(value) AS min_value,
                MAX(value) AS max_value,
                AVG(value) AS avg_value,
                SUM(value) AS total_value
            FROM electricity
            WHERE property = ?
            GROUP BY period
            ORDER BY period
        """

    params = [property_id]

    if args.start:
        query += " AND timestamp >= ?"
        params.append(args.start)
    if args.end:
        query += " AND timestamp < DATE_ADD(?, INTERVAL 1 DAY)"
        params.append(args.end)

    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
    except mariadb.Error as e:
        print(f"❌ Query failed: {e}")
        sys.exit(1)

    if not rows:
        print("⚠️  No data found for the given criteria.")
    else:
        if args.overall:
            # Single row with min, max, sum
            min_val, max_val, total_val = rows[0]
            print(f"\n📊 Overall statistics for property {property_id}:")
            print("-" * 50)
            print(f"Minimum: {min_val:.2f}")
            print(f"Maximum: {max_val:.2f}")
            print(f"Sum:     {total_val:.2f}")
            print("-" * 50)
        else:
            # Grouped output (with average)
            print(f"\n📊 Statistics for property {property_id} (grouped by {args.group}):")
            print("-" * 70)
            print(f"{'Period':<15} {'Min':>10} {'Max':>10} {'Avg':>10} {'Sum':>12}")
            print("-" * 70)
            for row in rows:
                period = row[0]
                min_val = row[1]
                max_val = row[2]
                avg_val = row[3]
                total_val = row[4]
                print(f"{period:<15} {min_val:>10.2f} {max_val:>10.2f} {avg_val:>10.2f} {total_val:>12.2f}")
            print("-" * 70)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
