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

# Define the table name
table_name = "account_holders"

# Define the column names and their data types
columns = [
    "id serial primary key",
    "first_name VARCHAR(255)",
    "last_name VARCHAR(255)",
    "mobile_number VARCHAR(20)",
    "date_of_birth varchar(255)",
    "aadhar_number VARCHAR(20)",
    "pan_number VARCHAR(20)",
    "nationality VARCHAR(255)",
    "state VARCHAR(255)",
    "gender VARCHAR(10)",
    "branch_code VARCHAR(10)",
    "account_type VARCHAR(255)",
    "balance VARCHAR(255)",
    "created_at TIMESTAMP DEFAULT current_timestamp",
    "account_number VARCHAR(255)",
    "IFSC VARCHAR(255)"
]

# Construct the CREATE TABLE query
create_table_query = f"CREATE TABLE {table_name} ({', '.join(columns)})"

# Execute the CREATE TABLE query
cursor.execute(create_table_query)

print("table created")

# Commit the changes to the database
conn.commit()

# Close the cursor and database connection
cursor.close()
conn.close()
