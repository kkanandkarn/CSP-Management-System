import psycopg2
from flask import Flask, render_template, request, redirect, url_for, jsonify
import random
import json
from psycopg2 import Error
from flask import Flask, render_template, request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client


app = Flask(__name__)

account_holder_data = ""
transactions = []
transaction_account_number = ""
transaction_ifsc_code = ""
account_opening_otp = ""

account_sid = 'ACcfa7ed97949bb58abe841bfea67f1bc6'
auth_token = '3cff29f4b95cb7155ce10594a6c46be0'

# Create a Twilio client
client = Client(account_sid, auth_token)


# Configure PostgreSQL connection

def insert_data_into_table(data):
    conn = psycopg2.connect(
        host="localhost",
        database="su_db",
        user="postgres",
        password="admin"
    )
    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Construct the INSERT query
    insert_query = """
    INSERT INTO account_holders (
        first_name, last_name, mobile_number, date_of_birth, aadhar_number, pan_number,
        nationality, state, gender, branch_code, account_type, balance, account_number, IFSC
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Execute the INSERT query with the data
    cursor.execute(insert_query, data)

    # Commit the changes to the database
    conn.commit()

@app.route('/', methods=['GET'])
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    entered_username = data['username']
    entered_password = data['password']

    print("received username:", entered_username)
    print("received password:", entered_password)

    conn = psycopg2.connect(
    host="localhost",
    database="su_db",
    user="postgres",
    password="admin"
    )

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # SQL query to retrieve login credentials from the database
    select_query = "SELECT username, password FROM login_credentials WHERE username = %s AND password = %s"

    # Execute the SQL query with the entered username and password
    cursor.execute(select_query, (entered_username, entered_password))

    # Fetch the first row from the result
    result = cursor.fetchone()
    

    if result is not None:
        print("Entered Username:", entered_username)
        print("Entered Password:", entered_password)
        insert_query = "INSERT INTO session (user_name, login_time) VALUES (%s, CURRENT_TIMESTAMP);"
        cursor.execute(insert_query, (entered_username,))
        conn.commit()
        select_query = "SELECT user_name FROM session ORDER BY login_time DESC LIMIT 1;"
        cursor.execute(select_query)
        last_username = cursor.fetchone()[0]  # Fetch the first column of the first result
        return jsonify({'message': 'Login Successfull', 'username': last_username})
    elif entered_username == 'admin' and entered_password=='admin@csp0623':
        return jsonify({'message': 'Admin Login'})
    else:
        print("Entered Username:", entered_username)
        print("Entered Password:", entered_password)
        print("Login failed")
        return jsonify({'message': 'Invalid credentials'})
    
@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    username = request.args.get('username')  # Get the username from the query parameter

    try:
        connection = psycopg2.connect(
          host="localhost",
          database="su_db",
          user="postgres",
          password="admin"
        )
        cursor = connection.cursor()

        # Insert the username into the session table

        # Fetch the last username
        select_query = "SELECT user_name FROM session ORDER BY login_time DESC LIMIT 1;"
        cursor.execute(select_query)
        last_username = cursor.fetchone()[0]  # Fetch the first column of the first result
        print("Last username fetched:", last_username)

        return render_template('dashboard.html', username=last_username)

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)

    
@app.route('/operations')
def operations():
    return render_template('operations.html')

@app.route('/accountopening')
def account_opening():
    return render_template('accountopening.html')

@app.route('/submit', methods=['POST'])
def submit_form():
    global account_holder_data, account_opening_otp
   # Retrieve the form data
    first_name = request.form.get('first-name')
    last_name = request.form.get('last-name')
    mobile_number = request.form.get('mobile-number')
    date_of_birth = request.form.get('date-of-birth')
    aadhar_number = request.form.get('aadhar-number')
    pan_number = request.form.get('pan-number')
    nationality = request.form.get('nationality')
    state = request.form.get('state')
    gender = request.form.get('gender')
    branch_code = request.form.get('branch-code')
    account_type = request.form.get('account-type')
    opening_balance = request.form.get('opening-balance')

    if not mobile_number.startswith("+91"):
        mobile_number = "+91" + mobile_number

    account_number = random.randint(10**11, (10**12)-1)
    IFSC_code = random.randint(10**5, (10**6)-1)
    IFSC = 'SBIN808840'

    account_opening_otp = str(random.randint(1000, 9999))

    print("account_opening_otp: ",account_opening_otp)

    
    message = client.messages.create(
        from_='+13613493910',
        body='Your OTP to open account in CSP is: ' + account_opening_otp,
        to='+919262261560'
    )


    print(f"SMS sent successfully. SID: {message.sid}")
    

    account_holder_data = (
        first_name, last_name, mobile_number, date_of_birth, aadhar_number, pan_number,
        nationality, state, gender, branch_code, account_type, opening_balance,
        account_number, IFSC
    )
    return redirect(url_for('kyc'))

@app.route('/kyc')
def kyc():
    return render_template('kyc.html')

@app.route('/validate-otp', methods=['POST'])
def validate_otp():
    global account_holder_data, account_opening_otp
    data = request.get_json()
    otp = data.get('otp')

    print("otp received:", otp)    


    if otp == account_opening_otp:
        response = 'Account created Successfully' 
        
        print(response)
        insert_data_into_table(account_holder_data)
        return response
        
    else:
        response = 'Invalid otp' 
        print(response)
    return jsonify(response)

@app.route('/depositamount')
def deposit_amount():
    return render_template("deposit_amount.html")

@app.route('/submit-deposit', methods=['POST'])
def submit_deposit():
    # Receive form data
    account_number = request.form.get('accountNumber')
    ifsc_code = request.form.get('ifscCode')
    account_holder_name = request.form.get('accountHolderName')
    amount = request.form.get('amount')
    otp = request.form.get('otp')
    transaction_type = 'Deposit'

    conn = psycopg2.connect(
    host="localhost",
    database="su_db",
    user="postgres",
    password="admin"
    )

    # Verify the OTP here
    if otp == 'confirm': 

        # Check if account number and IFSC code exist in the table
        cursor = conn.cursor()
        query = "SELECT balance FROM account_holders WHERE account_number = %s AND IFSC = %s"
        cursor.execute(query, (account_number, ifsc_code))
        result = cursor.fetchone()

        if result is None:
            # Account doesn't exist
            return 'Account doesnt exist'

        # Calculate new balance
        old_balance = result[0]
        new_balance = float(old_balance) + float(amount)

        # Update the balance in the database
        update_query = "UPDATE account_holders SET balance = %s WHERE account_number = %s AND IFSC = %s"
        cursor.execute(update_query, (str(new_balance), account_number, ifsc_code))

         # Insert the transaction into the statement table
        insert_query = "INSERT INTO statement (account_number, IFSC, transaction_type, amount) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (account_number, ifsc_code, transaction_type, amount))

        conn.commit()
        cursor.close()

        # Return a success response
        return 'success'

    else:
        # Return an error response for invalid OTP
        return 'invalid'
    
@app.route('/withdrawamount')
def withdraw_amount():
    return render_template("withdrawl_amount.html")

@app.route('/submit-withdraw', methods=['POST'])
def submit_withdraw():
    # Receive form data
    account_number = request.form.get('accountNumber')
    ifsc_code = request.form.get('ifscCode')
    account_holder_name = request.form.get('accountHolderName')
    amount = float(request.form.get('amount'))
    otp = request.form.get('otp')
    transaction_type = 'Withdraw'

    conn = psycopg2.connect(
    host="localhost",
    database="su_db",
    user="postgres",
    password="admin"
    )

    # Verify the OTP here
    if otp == '123456':  # Replace '123456' with your actual OTP verification logic

        # Check if account number and IFSC code exist in the table
        cursor = conn.cursor()
        query = "SELECT balance FROM account_holders WHERE account_number = %s AND ifsc = %s"
        cursor.execute(query, (account_number, ifsc_code))
        result = cursor.fetchone()

        if result is None:
            # Account doesn't exist
            return 'Account not found'

        balance = result[0]

        if float(amount) > float(balance):
            # Insufficient balance
            return 'Insufficient balance'

        # Calculate new balance
        new_balance = float(balance) - float(amount)

        # Update the balance in the database
        update_query = "UPDATE account_holders SET balance = %s WHERE account_number = %s AND ifsc = %s"
        cursor.execute(update_query, (new_balance, account_number, ifsc_code))

         # Insert the transaction into the statement table
        insert_query = "INSERT INTO statement (account_number, IFSC, transaction_type, amount) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (account_number, ifsc_code, transaction_type, amount))

        conn.commit()
        cursor.close()

        # Return a success response
        return 'success'

    else:
        # Return an error response for invalid OTP
        return 'Invalid OTP'

@app.route('/checkbalance')
def check_balance():
    return render_template("check_balance.html")

@app.route('/submit-balance', methods=['POST'])
def submit_balance():
    # Retrieve the form data including the OTP
    account_number = request.form.get('accountNumber')
    ifsc_code = request.form.get('ifscCode')
    account_holder_name = request.form.get('accountHolderName')
    otp = request.form.get('otp')

    conn = psycopg2.connect(
    host="localhost",
    database="su_db",
    user="postgres",
    password="admin"
    )

    # Perform verification logic here
    # Example: Check if the OTP is valid
    if otp == "1234":
        # Verification successful

        # Create a cursor to execute SQL queries
        cursor = conn.cursor()

        # Fetch the balance from the account_holders table based on account number and IFSC code
        query = "SELECT balance FROM account_holders WHERE account_number = %s AND ifsc = %s"
        cursor.execute(query, (account_number, ifsc_code))
        balance = cursor.fetchone()

        cursor.close()
        conn.close()

        

        if balance is None:
            # Perform balance enquiry logic here
            # Return the balance as a JSON response
            return jsonify(error='Account not found')
        else:
            return jsonify(balance=balance[0])
        
            # Close the cursor and connection
      
        

            

    else:
        return jsonify(error='An error occured check the form.')
    
@app.route('/moneytransfer')
def money_transfer():
    return render_template("money_transfer.html") 

@app.route('/submit-transfer', methods=['POST'])
def submit_transfer():
    form_data = request.get_json()
     # Extract the form data into separate variables
    sender_account_number = form_data.get('senderAccountNumber')
    receiver_account_number = form_data.get('receiverAccountNumber')
    sender_ifsc_code = form_data.get('senderIFSCCode')
    receiver_ifsc_code = form_data.get('receiverIFSCCode')
    sender_name = form_data.get('senderName')
    receiver_name = form_data.get('receiverName')
    otp = form_data.get('otp')
    amount = form_data.get('amount')

    print("Sender Account Number:", sender_account_number)
    print("Receiver Account Number:", receiver_account_number)
    print("Sender IFSC Code:", sender_ifsc_code)
    print("Receiver IFSC Code:", receiver_ifsc_code)
    print("Sender Name:", sender_name)
    print("Receiver Name:", receiver_name)
    print("OTP:", otp)
    print("Amount:", amount)

    if otp != "1234":  # Replace "1234" with the actual correct OTP
        return jsonify(error="Invalid OTP."), 401
    
    sender_exists = check_account_exists(sender_account_number, sender_ifsc_code)
    if not sender_exists:
        return jsonify(error="Sender does not exist."), 400

    # Check if the receiver exists
    receiver_exists = check_account_exists(receiver_account_number, receiver_ifsc_code)
    if not receiver_exists:
        return jsonify(error="Receiver does not exist."), 400
    
    # Retrieve the sender's balance from the database
    sender_balance = retrieve_sender_balance(sender_account_number, sender_ifsc_code)

    if sender_balance is None:
        # Sender does not exist
        return jsonify(error='Sender does not exist.'), 400

    # Check if sender has sufficient balance
    if float(sender_balance) < float(amount):
        return jsonify(error='Insufficient balance.'), 400
    
      # Subtract the amount from the sender's balance
    updated_sender_balance = float(sender_balance) - float(amount)

    # Update the sender's balance in the database
    update_sender_balance(sender_account_number, sender_ifsc_code, updated_sender_balance, amount)

    # Add the amount to the receiver's balance
    receiver_balance = retrieve_receiver_balance(receiver_account_number, receiver_ifsc_code)
    if receiver_balance is None:
        # Receiver does not exist
        return jsonify(error='Receiver does not exist.'), 400

    updated_receiver_balance = float(receiver_balance) + float(amount)

    # Update the receiver's balance in the database
    update_receiver_balance(receiver_account_number, receiver_ifsc_code, updated_receiver_balance, amount)

    
    

    # Return a response to the client
    return 'Money Transfer Successfull'

def check_account_exists(account_number, ifsc_code):
    try:
        conn = psycopg2.connect(
        host="localhost",
        database="su_db",
        user="postgres",
        password="admin"
        )

        # Create a cursor object to interact with the database
        cursor = conn.cursor()

        # Prepare the SQL query
        query = "SELECT * FROM account_holders WHERE account_number = %s AND ifsc = %s"

        # Execute the query with the provided account number and IFSC code
        cursor.execute(query, (account_number, ifsc_code))

        # Fetch the result
        result = cursor.fetchone()

        # Check if a row is returned
        if result is None:
            return False
        else:
            return True

    except (Exception, psycopg2.Error) as error:
        print("Error retrieving account details:", error)
        return False

    finally:
        # Close the cursor and database connection
        cursor.close()
        conn.close()


def retrieve_sender_balance(sender_account_number, sender_ifsc_code):
    # Establish a connection to the PostgreSQL database
    connection = psycopg2.connect(
        host="localhost",
        database="su_db",
        user="postgres",
        password="admin"
    )

    try:
        # Create a cursor to interact with the database
        cursor = connection.cursor()

        # Execute the query to retrieve the sender's balance
        query = "SELECT balance FROM account_holders WHERE account_number = %s AND ifsc = %s"
        cursor.execute(query, (sender_account_number, sender_ifsc_code))

        # Fetch the balance value
        balance = cursor.fetchone()

        if balance:
            return balance[0]  # Return the balance value
        else:
            return None  # Sender account not found

    except (psycopg2.Error, psycopg2.DatabaseError) as error:
        print("Error retrieving sender balance:", error)
        return None

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()


def update_sender_balance(sender_account_number, sender_ifsc_code, updated_sender_balance, amount):
    transaction_type = 'Withdraw'
    # Establish a connection to the PostgreSQL database
    connection = psycopg2.connect(
        host="localhost",
        database="su_db",
        user="postgres",
        password="admin"
    )

    try:
        # Create a cursor to interact with the database
        cursor = connection.cursor()

        # Execute the query to update the sender's balance
        query = "UPDATE account_holders SET balance = %s WHERE account_number = %s AND ifsc = %s"
        cursor.execute(query, (updated_sender_balance, sender_account_number, sender_ifsc_code))

         # Insert the transaction into the statement table
        insert_query = "INSERT INTO statement (account_number, IFSC, transaction_type, amount) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (sender_account_number, sender_ifsc_code, transaction_type, amount))

        # Commit the changes to the database
        connection.commit()

    except (psycopg2.Error, psycopg2.DatabaseError) as error:
        # Rollback the transaction in case of an error
        connection.rollback()
        print("Error updating sender balance:", error)

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()

def retrieve_receiver_balance(receiver_account_number, receiver_ifsc_code):
    # Establish a connection to the PostgreSQL database
    connection = psycopg2.connect(
        host="localhost",
        database="su_db",
        user="postgres",
        password="admin"
    )

    try:
        # Create a cursor to interact with the database
        cursor = connection.cursor()

        # Execute the query to retrieve the receiver's balance
        query = "SELECT balance FROM account_holders WHERE account_number = %s AND ifsc = %s"
        cursor.execute(query, (receiver_account_number,receiver_ifsc_code))
        balance = cursor.fetchone()

        # Check if the balance exists
        if balance:
            receiver_balance = balance[0]
            return receiver_balance
        else:
            return None

    except (psycopg2.Error, psycopg2.DatabaseError) as error:
        print("Error retrieving receiver balance:", error)

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()

def update_receiver_balance(receiver_account_number, receiver_ifsc_code, updated_receiver_balance, amount):
    transaction_type = "Deposit"
    # Establish a connection to the PostgreSQL database
    connection = psycopg2.connect(
        host="localhost",
        database="su_db",
        user="postgres",
        password="admin"
    )

    try:
        # Create a cursor to interact with the database
        cursor = connection.cursor()

        # Execute the query to update the receiver's balance
        query = "UPDATE account_holders SET balance = %s WHERE account_number = %s AND ifsc = %s"
        cursor.execute(query, (updated_receiver_balance, receiver_account_number, receiver_ifsc_code))

         # Insert the transaction into the statement table
        insert_query = "INSERT INTO statement (account_number, IFSC, transaction_type, amount) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (receiver_account_number, receiver_ifsc_code, transaction_type, amount))


        # Commit the changes to the database
        connection.commit()

    except (psycopg2.Error, psycopg2.DatabaseError) as error:
        # Rollback the transaction in case of an error
        connection.rollback()
        print("Error updating receiver balance:", error)

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()

@app.route('/ministatement')
def mini_statement():
    return render_template("ministatement.html") 

@app.route('/submit-statement', methods=['POST'])
def handle_form_submission():
    global transactions, transaction_account_number, transaction_ifsc_code
    account_number = request.form.get('accountNo')
    ifsc_code = request.form.get('ifscCode')
    account_holder = request.form.get('accountHolder')
    otp = request.form.get('otp')

    transaction_account_number = account_number
    transaction_ifsc_code = ifsc_code

    if otp == '1234':  # Replace '1234' with the correct OTP
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            host="localhost",
            database="su_db",
            user="postgres",
            password="admin"
        )
        
        # Create a cursor object to interact with the database
        cursor = connection.cursor()
        
        # Query the database to check if the account holder exists
        query = "SELECT * FROM account_holders WHERE account_number = %s AND ifsc = %s"
        cursor.execute(query, (account_number, ifsc_code))
        account_holder_exists = cursor.fetchone() is not None
        
        if account_holder_exists:
            # Account holder exists
            # Query the statement table to check if transactions exist
            query = "SELECT * FROM statement WHERE account_number = %s AND ifsc = %s"
            cursor.execute(query, (account_number, ifsc_code))
            transactions_exist = cursor.fetchone() is not None
            
            
            
            if transactions_exist:
                # Transactions exist
                # Process the form data or perform any desired actions
                # You can print or manipulate the form data as needed
                print(f"Account No: {account_number}")
                print(f"IFSC Code: {ifsc_code}")
                print(f"Account Holder: {account_holder}")
                print(f"OTP: {otp}")


        # Fetch the transaction history from the database
                cursor.execute(
                    "SELECT transaction_type, amount, transaction_time "
                    "FROM statement "
                    "WHERE account_number = %s AND IFSC = %s "
                    "ORDER BY transaction_time DESC LIMIT 5",
                    (account_number, ifsc_code)
                )
                rows = cursor.fetchall()

                # Prepare the transaction history data
               
                for row in rows:
                    transaction = {
                        'transaction_type': row[0],
                        'amount': row[1],
                        'transaction_time': row[2].strftime("%Y-%m-%d %H:%M:%S")
                    }
                    transactions.append(transaction)
                print(transaction)

                
                cursor = connection.cursor()

                # Return success message
                return json.dumps({'status': 'success', 'message': 'Successful submission'})
            else:
                # No transactions found
                # Return error message for no transactions
                return json.dumps({'status': 'error', 'message': 'No transactions found'})
        else:
            # Account holder does not exist
            # Close the cursor and connection
            cursor.close()
            connection.close()

            # Return error message for account not found
            return json.dumps({'status': 'error', 'message': 'Account holder not found'})
    else:
        # Return error message for invalid OTP
        return json.dumps({'status': 'error', 'message': 'Invalid OTP'})
    
@app.route('/mini-statement')
def display_statement():
    global transactions, transaction_account_number, transaction_ifsc_code
    return render_template('transaction_history.html', transactions=transactions, transaction_account_number=transaction_account_number, transaction_ifsc_code=transaction_ifsc_code)

# Define the route to fetch and display account holder data
@app.route('/account_holders')
def account_holders():
    # Connect to the database
    conn = psycopg2.connect(
        host='localhost',
        database='su_db',
        user='postgres',
        password='admin'
    )
    
    # Create a cursor object to interact with the database
    cursor = conn.cursor()
    
    # Execute the query to fetch account holder data
    query = "SELECT * FROM account_holders order by id asc"
    cursor.execute(query)
    
    # Fetch all rows of the result
    rows = cursor.fetchall()
    
    # Close the cursor and database connection
    cursor.close()
    conn.close()
    
    # Render the template with the account holder data
    return render_template('account_holders.html', rows=rows)

@app.route('/login-credentials')
def display_credentials():
    # Connect to the PostgreSQL database
    connection = psycopg2.connect(
         host='localhost',
        database='su_db',
        user='postgres',
        password='admin'
    )
    
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Fetch data from the login_credentials table
    cursor.execute('SELECT * FROM login_credentials order by id asc')
    data = cursor.fetchall()

    # Close the cursor and database connection
    cursor.close()
    connection.close()

    # Render the HTML template and pass the data to it
    return render_template('credentials.html', data=data)



@app.route('/insert-credentials', methods=['POST'])
def insert_credentials():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Check if username already exists in the database
    connection = psycopg2.connect(
        host='localhost',
        database='su_db',
        user='postgres',
        password='admin'
    )
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM login_credentials WHERE username = %s", (username,))
    existing_credentials = cursor.fetchone()

    if existing_credentials:
        # Username already exists, reuse the ID
        existing_id = existing_credentials[0]
        cursor.execute("UPDATE login_credentials SET username = %s, password = %s WHERE id = %s",
                       (username, password, existing_id))
        connection.commit()
        connection.close()

        # Credentials updated successfully
        response = {
            'message': 'Credentials updated.'
        }
        return jsonify(response), 200

    # Insert the username and password into the database
    cursor.execute("INSERT INTO login_credentials (username, password) VALUES (%s, %s)", (username, password))
    connection.commit()
    connection.close()

    # Credentials inserted successfully
    response = {
        'message': 'Credentials inserted.'
    }
    return jsonify(response), 200

@app.route('/edit-credentials', methods=['POST'])
def edit_credentials():
    data = request.get_json()
    username = data['username']
    new_username = data['new_username']
    new_password = data['new_password']

    # Update the username and password in the database
    connection = psycopg2.connect(
        host='localhost',
        database='su_db',
        user='postgres',
        password='admin'
    )
    cursor = connection.cursor()
    cursor.execute("UPDATE login_credentials SET username = %s, password = %s WHERE username = %s",
                   (new_username, new_password, username))
    connection.commit()
    connection.close()

    # Credentials updated successfully
    response = {
        'message': 'Credentials updated.'
    }
    return jsonify(response), 200


@app.route('/delete-user', methods=['POST'])
def delete_user():
    data = request.get_json()
    username = data['username']

    # Delete the username from the database
    connection = psycopg2.connect(
        host='localhost',
        database='su_db',
        user='postgres',
        password='admin'
    )
    cursor = connection.cursor()
    cursor.execute("DELETE FROM login_credentials WHERE username = %s", (username,))
    connection.commit()
    connection.close()

    # User deleted successfully
    response = {
        'message': 'User deleted.'
    }
    return jsonify(response), 200

@app.route('/transactions')
def fetch_transactions():
    # Establish a connection to the database
    conn = psycopg2.connect(
        host='localhost',
        dbname='su_db',
        user='postgres',
        password='admin'
    )
    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute the query to fetch transactions
    cursor.execute("SELECT * FROM statement")

    # Fetch all the rows returned by the query
    rows = cursor.fetchall()

    # Close the cursor and the database connection
    cursor.close()
    conn.close()

    # Pass the fetched data to the HTML template
    return render_template('display_transaction.html', rows=rows)

@app.route('/help')
def help():
    return render_template('contact.html')

@app.route('/send_email', methods=['POST'])
def send_email():
    # Get the form data
    name = request.form['name']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']
    
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = 'anandairesearcher@gmail.com'  # Replace with your email ID
    msg['Subject'] = subject
    
    body = f"Name: {name}\nEmail: {email}\n\n{message}"
    msg.attach(MIMEText(body, 'plain'))
    
    # Send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('anandairesearcher@gmail.com', 'jmybhqbpippqiukk')  # Replace with your email ID and password
        smtp.send_message(msg)
    
    return 'Email sent successfully!'


@app.route('/demo')
def demo():
    return render_template('demo.html')

@app.route('/index')
def index1():
    return render_template('index.html')




if __name__ == '__main__':
    app.run(debug=True)
