import psycopg2

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    database="su_db",
    user="postgres",
    password="admin"
)

# Create a cursor object to interact with the database
cursor = conn.cursor()

# SQL statement to create the table
create_table_query = """
CREATE TABLE statement (
    id SERIAL PRIMARY KEY,
    account_number VARCHAR(255),
    IFSC VARCHAR(255),
    transaction_type VARCHAR(255),
    amount VARCHAR(255),
    transaction_time TIMESTAMP DEFAULT current_timestamp
)
"""

# Execute the CREATE TABLE query
cursor.execute(create_table_query)

# Commit the changes to the database
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()
