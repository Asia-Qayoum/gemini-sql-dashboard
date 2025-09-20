# cl.py
import sqlite3

DB_PATH = "sql_agent_class.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
tables = [row[0] for row in cursor.fetchall()]

if not tables:
    print("No tables found in the database.")
else:
    for table in tables:
        print(f"\n=== Table: {table} ===")
        cursor.execute(f"PRAGMA table_info({table});")
        cols = cursor.fetchall()
        for col in cols:
            print(f"  - {col[1]} ({col[2]})")
        # show 5 rows
        cursor.execute(f"SELECT * FROM {table} LIMIT 5;")
        rows = cursor.fetchall()
        if rows:
            print("  Sample rows:")
            for r in rows:
                print("   ", r)
        else:
            print("  (no data)")
conn.close()
