import sqlite3

# read SQL file
with open("sql_agent_seed.sql", "r", encoding="utf-8") as f:
    sql_script = f.read()


# create the database
conn = sqlite3.connect("sql_agent_class.db")
conn.executescript(sql_script)
conn.commit()
conn.close()

print("Database seeded successfully!")
