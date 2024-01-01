import sqlite3

# Connect to SQLite database (this will create the database file if it doesn't exist)
conn = sqlite3.connect('database/transactions.db')

# Create a cursor object using the cursor method
cursor = conn.cursor()

# Create table with the necessary columns
cursor.execute('''
CREATE TABLE transactions (
    date TEXT,
    id INTEGER PRIMARY KEY,
    "transaction" TEXT,  -- Enclosed in double quotes
    category TEXT,
    amount REAL,
    tax REAL,
    shipping REAL,
    fees REAL,
    net_amount REAL,
    description TEXT,
    remarks TEXT
)
''')


# Commit the transaction
conn.commit()

# Close the connection
conn.close()
