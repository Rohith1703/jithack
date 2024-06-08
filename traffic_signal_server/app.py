from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from cryptography.fernet import Fernet
from twilio.rest import Client
import os
import random
import pandas as pd

app = Flask(__name__)
app.secret_key = os.urandom(24) 

TWILIO_ACCOUNT_SID = 'AC3df27566758dddaf7ce4a1d41d3bddc1'
TWILIO_AUTH_TOKEN = 'a41fd26f28c164752d0ce4bf05afc19d'
TWILIO_PHONE_NUMBER = '+13613094502'

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

key = Fernet.generate_key()
cipher_suite = Fernet(key)


data = {
    "patient": {
        "name": "John Doe",
        "age": 30,
        "condition": "Stable",
        "details": "Minor injuries, conscious",
        "emergencyTime": "2024-05-26T14:30:00Z"
    },
    "status": "Green",
    "emergencyLatitude": 37.7749,
    "emergencyLongitude": -122.4194
}

def encrypt_data(data):
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(data):
    return cipher_suite.decrypt(data.encode()).decode()

def save_to_excel(data):
    df = pd.DataFrame([data])
    df.to_excel('patient_data.xlsx', index=False)

def generate_otp():
    return str(random.randint(100000, 999999))

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/sendOTP', methods=['POST'])
def send_otp():
    phone_number = request.form['phone']

   
    otp = generate_otp()
    session['otp'] = otp

  
    message = client.messages.create(
        body=f'Your OTP for patient data edit is: {otp}',
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )

    return render_template('verify_otp.html')

@app.route('/verifyOTP', methods=['POST'])
def verify_otp():
    user_otp = request.form['otp']
    stored_otp = session.get('otp')

    if user_otp == stored_otp:
        return redirect(url_for('edit_patient'))
    else:
        return jsonify({"error": "Invalid OTP. Please try again."})

@app.route('/editPatient', methods=['GET', 'POST'])
def edit_patient():
    if request.method == 'POST':
        
        data['patient']['name'] = request.form['name']
        data['patient']['age'] = int(request.form['age'])
        data['patient']['condition'] = request.form['condition']
        data['patient']['details'] = request.form['details']
        data['patient']['emergencyTime'] = request.form['emergencyTime']
        
        
        save_to_excel(data['patient'])

        return redirect(url_for('thank_you'))
    
    
    return render_template('edit_patient.html', patient=data['patient'])

@app.route('/thankYou', methods=['GET'])
def thank_you():
    return render_template('thank_you.html')

@app.route('/viewPatient', methods=['GET'])
def view_patient():
    encrypted_data = {
        "name": encrypt_data(data['patient']['name']),
        "age": encrypt_data(str(data['patient']['age'])),
        "condition": encrypt_data(data['patient']['condition']),
        "details": encrypt_data(data['patient']['details']),
        "emergencyTime": encrypt_data(data['patient']['emergencyTime'])
    }
    return render_template('view_patient.html', patient=encrypted_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
