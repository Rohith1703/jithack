import pandas as pd
from flask import request

def save_to_excel(data):
    ip_address = request.remote_addr
    
    try:
        # Load the existing Excel file if it exists, or create a new DataFrame
        df = pd.read_excel('patient_data.xlsx')
    except FileNotFoundError:
        df = pd.DataFrame()

    # Check if the patient already exists in the DataFrame
    existing_patient = df[df['IP Address'] == ip_address]
    if not existing_patient.empty:
        print("Patient already exists for this IP address. Skipping...")
        return

    # Add IP Address to the data before appending
    data['IP Address'] = ip_address
    
    # Append the patient data to the DataFrame
    df = df.append(data, ignore_index=True)

    # Save the DataFrame to the Excel file
    df.to_excel('patient_data.xlsx', index=False)
