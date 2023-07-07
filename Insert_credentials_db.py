import psycopg2

def insert_credentials(username, password):
    # Establish a connection to the PostgreSQL database
    conn = psycopg2.connect(
        host="localhost",
        database="su_db",
        user="postgres",
        password="admin"
    )

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # SQL query to insert data into the login_credentials table
    insert_query = "INSERT INTO login_credentials (username, password) VALUES (%s, %s)"

    # Execute the SQL query with the provided username and password
    cursor.execute(insert_query, (username, password))


    # Commit the changes to the database
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

username = input("Enter User name: ")
password = input("Enter Password: ")

insert_credentials(username, password)
