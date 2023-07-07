import psycopg2

# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(
     host="localhost",
    database="su_db",
    user="postgres",
    password="admin"
)

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# SQL query to create the table
create_table_query = '''
    CREATE TABLE login_credentials (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL
    )
'''

# Execute the SQL query
cursor.execute(create_table_query)

# Commit the changes to the database
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()
