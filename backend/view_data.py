import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('banking.db')
cursor = conn.cursor()

def print_table(table_name):
    print(f"\n--- {table_name.upper()} ---")
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        if not rows:
            print("(No records found)")
            return

        # Get column names
        names = [description[0] for description in cursor.description]
        print(f"{' | '.join(names)}")
        print("-" * 50)
        
        for row in rows:
            print(row)
    except Exception as e:
        print(f"Error reading {table_name}: {e}")

print_table("users")
print_table("documents")

conn.close()
