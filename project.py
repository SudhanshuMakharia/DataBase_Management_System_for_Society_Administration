import streamlit as st
import pandas as pd
import streamlit_lottie
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("Mongo_URI")
db = client["society_db"]
residents_collection = db["residents"]

# Set a default common due date (can be updated)
due_date = "2024-06-30"

#Set page configuration
layout = "wide"
page_title = "Society Management System"
st.set_page_config(page_title=page_title, layout=layout)
    
# Streamlit app
st.title(page_title)
st.lottie("https://lottie.host/b57c5aaa-dc66-4d89-abf5-12106d11f403/jR5wNvEHmz.json", width=450, height=450)

# Sidebar navigation menu
menu_option = st.sidebar.selectbox("Menu", ["Add Residents", "View Residential Info", "View Maintenance Due"])

# Edit Info section
if menu_option == "Add Residents":
    st.sidebar.header("Add Resident Info")
    name = st.sidebar.text_input("Resident Name")
    apartment_number = st.sidebar.text_input("Apartment Number")
    contact_number = st.sidebar.text_input("Contact Number")
    email = st.sidebar.text_input("Email")
    maintenance_fee = st.sidebar.number_input("Maintenance Fee", value=0)

    if st.sidebar.button("Save"):
        if name and apartment_number and contact_number:
            resident_data = {
                "name": name,
                "apartment_number": apartment_number,
                "contact_number": contact_number,
                "email": email,
                "maintenance_fee": maintenance_fee
            }
            residents_collection.update_one(
                {"name": name},
                {"$set": resident_data},
                upsert=True
            )
            st.sidebar.success("Resident information updated successfully!")
        else:
            st.sidebar.error("Please fill in all details.")

# View Residential Info section
elif menu_option == "View Residential Info":
    st.title("Society Residents")
    residents = residents_collection.find()
    
    # Prepare data for DataFrame
    data = []
    for resident in residents:
        if 'maintenance_fee' in resident:
            data.append([resident['name'], resident['apartment_number'], resident['contact_number'], resident.get('email', 'N/A')])
    
    # Display table using DataFrame
    if data:
        df = pd.DataFrame(data, columns=["Resident Name", "Flat No.", "Contact No.", "Email ID"])
        st.table(df)
    else:
        st.write("No residential information available.")

# View Maintenance Due section
elif menu_option == "View Maintenance Due":
    st.title("Maintenance Due")
    # Show the common due date and provide an option to update it
    due_date = st.text_input("Due Date (YYYY-MM-DD)", due_date)
    if st.button("Update Due Date"):
        due_date = due_date.strip()
        if due_date:
            # Update the common due date in the database or wherever you store it
            st.success(f"Due Date updated to: {due_date}")
        else:
            st.error("Please provide a valid due date.")

    st.write(f"Due Date for Maintenance Fees: {due_date}")
    
    # Fetch maintenance due data from MongoDB
    maintenance_due_data = []
    residents_with_fees = residents_collection.find({"maintenance_fee": {"$exists": True}})
    for resident in residents_with_fees:
        maintenance_due_data.append([resident['name'], resident['maintenance_fee']])
    
    # Display maintenance due table using pandas and st.table
    if maintenance_due_data:
        df_maintenance_due = pd.DataFrame(maintenance_due_data, columns=["Resident Name", "Maintenance Due"])
        st.table(df_maintenance_due)
    else:
        st.write("No maintenance due information available.")
