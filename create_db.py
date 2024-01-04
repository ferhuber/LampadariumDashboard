import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('quickbooks.db')

# Create a cursor object
cursor = conn.cursor()

# Create a new table for QuickBooks transactions with the updated column names
cursor.execute('''
CREATE TABLE IF NOT EXISTS quickbooks_transactions (
    date TEXT,
    transaction_type TEXT,
    number TEXT,
    posting TEXT,
    name TEXT,
    location TEXT,
    description TEXT,
    account TEXT,
    related_account TEXT,
    amount REAL
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
