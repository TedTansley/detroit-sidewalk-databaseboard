import sqlite3

# Connect to the SQLite database
database_name = 'sidewalk_data.sqlite'
conn = sqlite3.connect(database_name)
cursor = conn.cursor()

# Function to fetch all tables in the database
def fetch_tables():
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    return tables

# Function to fetch column names and types of a table
def fetch_table_columns(table_name):
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    return columns

# Function to fetch a summary of the table data (e.g., number of rows)
def fetch_table_summary(table_name):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    return count

def main():
    tables = fetch_tables()
    if tables:
        print("Summary of Tables in the database:\n")
        for table in tables:
            table_name = table[0]
            print(f"Table: {table_name}")
            
            # Get column information
            columns = fetch_table_columns(table_name)
            print("Columns and Types:")
            for col in columns:
                print(f"- {col[1]} ({col[2]})")
            
            # Get row count
            row_count = fetch_table_summary(table_name)
            print(f"Number of rows: {row_count}\n")
    else:
        print("No tables found in the database.")
    
    # Close the connection
    conn.close()

if __name__ == "__main__":
    main()
