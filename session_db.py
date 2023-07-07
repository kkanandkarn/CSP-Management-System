import psycopg2
from psycopg2 import Error

try:
    connection = psycopg2.connect(
         host="localhost",
        database="su_db",
        user="postgres",
        password="admin"
    )
    cursor = connection.cursor()

    create_table_query = '''
    CREATE TABLE session (
        id serial primary key,
        user_name VARCHAR(50) NOT NULL,
        login_time TIMESTAMP NOT NULL
    );
    '''
    cursor.execute(create_table_query)
    connection.commit()
    print("Table 'session' created successfully.")

except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)

finally:
    if connection:
        cursor.close()
        connection.close()
