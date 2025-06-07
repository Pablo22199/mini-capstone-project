from flask import Flask, render_template, request, redirect, url_for
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import mysql.connector

app = Flask(__name__)

# Encryption key (32 bytes for AES256)
key = b'ThisIsA32ByteKeyForAES256Enc!'

# Function to encrypt data
def encrypt_data(data):
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv  # Initialization vector
    encrypted_data = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    return base64.b64encode(iv + encrypted_data).decode('utf-8')

# Function to decrypt data
def decrypt_data(encrypted_data):
    encrypted_data = base64.b64decode(encrypted_data)
    iv = encrypted_data[:16]
    encrypted_data = encrypted_data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(encrypted_data), AES.block_size).decode('utf-8')

# Connect to MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sochosocho",
        database="ComplianceDB"
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    full_name = request.form['full_name']
    dob = request.form['dob']
    ssn = encrypt_data(request.form['ssn'])
    driver_license = encrypt_data(request.form['driver_license'])
    home_address = request.form['home_address']
    phone_number = request.form['phone_number']
    email = request.form['email']
    bank_account = encrypt_data(request.form['bank_account'])
    credit_card = encrypt_data(request.form['credit_card'])

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert into Personal_Info table
        cursor.execute(
            "INSERT INTO Personal_Info (Full_Name, Date_of_Birth, SSN, Driver_License) VALUES (%s, %s, %s, %s)",
            (full_name, dob, ssn, driver_license)
        )
        personal_info_id = cursor.lastrowid  # Get the auto-generated ID

        # Insert into Contact_Info table
        cursor.execute(
            "INSERT INTO Contact_Info (id, Home_Address, Phone_Number, Email) VALUES (%s, %s, %s, %s)",
            (personal_info_id, home_address, phone_number, email)
        )

        # Insert into Financial_Info table
        cursor.execute(
            "INSERT INTO Financial_Info (id, Bank_Account, Credit_Card) VALUES (%s, %s, %s)",
            (personal_info_id, bank_account, credit_card)
        )

        conn.commit()
    except Exception as e:
        conn.rollback()
        return f"An error occurred: {e}"
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
