import sqlite3
import streamlit as st
import pandas as pd
import requests
from streamlit_lottie import st_lottie
from datetime import datetime

def loti(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    else:
        return r.json()

def create_connection():
    """Create a connection to the SQLite database."""
    return sqlite3.connect('userdb.db')

def create_database(con):
    """Create the 'userdb' database if it doesn't exist."""
    cursor = con.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS userdb")
    cursor.close()

def create_patients_table(con):
    """Create the patients table in the database."""
    cursor = con.cursor()
    
    create_patients_table_query = """
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        contact_number TEXT,
        address TEXT,
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        email TEXT
    )
    """

    cursor.execute(create_patients_table_query)
    con.commit()
    st.write("Patients table created successfully.")

def modify_patients_table(con):
    cursor = con.cursor()

    alter_table_query = """
    ALTER TABLE patients
    ADD COLUMN doctor_name VARCHAR(255),
    ADD COLUMN disease VARCHAR(255),
    ADD COLUMN fee INTEGER(5),
    ADD COLUMN tests VARCHAR(255),
    ADD COLUMN cnic VARCHAR(20)
    """

    cursor.execute(alter_table_query)
    con.commit()
    st.write("Patients table modified successfully.")

def create_appointments_table(con):
    """Create the appointments table in the database."""
    cursor = con.cursor()

    create_appointments_table_query = """
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        appointment_date DATE,
        appointment_time TIME,
        doctor_name TEXT,
        notes TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients(id)
    )
    """

    cursor.execute(create_appointments_table_query)
    con.commit()
    st.write("Appointments table created successfully.")

def insert_patient_record(con, name, age, contact_number, email, address):
    """Insert a new patient record into the 'patients' table."""
    cursor = con.cursor()

    insert_patient_query = """
    INSERT INTO patients (name, age, contact_number, email, address, date_added)
    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """

    patient_data = (name, age, contact_number, email, address)

    cursor.execute(insert_patient_query, patient_data)
    con.commit()
    st.write("Patient record inserted successfully.")

def fetch_all_patients(con):
    """Fetch all records from the 'patients' table."""
    cursor = con.cursor()

    select_patients_query = "SELECT id, name, age, contact_number, email, address, date_added FROM patients"

    cursor.execute(select_patients_query)
    patients = cursor.fetchall()

    return patients

def fetch_patient_by_id(con, patient_id):
    """Fetch a patient's record from the 'patients' table based on ID."""
    cursor = con.cursor()

    select_patient_query = "SELECT * FROM patients WHERE id = ?"
    cursor.execute(select_patient_query, (patient_id,))
    patient = cursor.fetchone()

    return patient

def fetch_patient_by_contact(con, contact_number):
    """Fetch a patient's record from the 'patients' table based on contact number."""
    cursor = con.cursor()

    select_patient_query = "SELECT * FROM patients WHERE contact_number = ?"
    cursor.execute(select_patient_query, (contact_number,))
    patient = cursor.fetchone()

    return patient

def fetch_patient_by_cnic(con, cnic):
    """Fetch a patient's record from the 'patients' table based on CNIC."""
    cursor = con.cursor()

    # Select the database
    cursor.execute("USE userdb")

    select_patient_query = "SELECT * FROM patients WHERE cnic = ?"
    cursor.execute(select_patient_query, (cnic,))
    patient = cursor.fetchone()

    return patient

def delete_patient_record(con, delete_option, delete_value):
    """Delete a patient record from the 'patients' table based on ID, name, or contact number."""
    cursor = con.cursor()

    if delete_option == "ID":
        delete_patient_query = "DELETE FROM patients WHERE id = ?"
    elif delete_option == "Name":
        delete_patient_query = "DELETE FROM patients WHERE name = ?"
    elif delete_option == "Contact Number":
        delete_patient_query = "DELETE FROM patients WHERE contact_number = ?"

    cursor.execute(delete_patient_query, (delete_value,))
    con.commit()
    st.write("Patient record deleted successfully.")

def insert_appointment_record(con, patient_id, appointment_date, appointment_time, doctor_name, notes):
    """Insert a new appointment record into the 'appointments' table."""
    cursor = con.cursor()

    # Select the database
    cursor.execute("USE userdb")
    appointment_time = appointment_time.strftime("%H:%M:%S")
    appointment_date = appointment_date.strftime("%Y-%m-%d")
    insert_appointment_query = """
    INSERT INTO appointments (patient_id, appointment_date, appointment_time, doctor_name, notes)
    VALUES (?, ?, ?, ?, ?)
    """

    appointment_data = (patient_id, appointment_date, appointment_time, doctor_name, notes)

    cursor.execute(insert_appointment_query, appointment_data)
    con.commit()
    print("Appointment record inserted successfully.")

def fetch_all_appointments(con):
    """Fetch all records from the 'appointments' table."""
    cursor = con.cursor()

    # Select the database
    cursor.execute("USE userdb")

    select_appointments_query = """
    SELECT id, patient_id, date(appointment_date) AS appointment_date, 
           time(appointment_time) AS appointment_time, doctor_name, notes
    FROM appointments
    """
    cursor.execute(select_appointments_query)
    appointments = cursor.fetchall()

    return appointments

def show_all_appointments(con):
    cursor = con.cursor()

    select_query = """
    SELECT id, patient_id, date(appointment_date), time(appointment_time), doctor_name, notes FROM appointments
    """
    cursor.execute(select_query)
    records = cursor.fetchall()

    if records:
        st.subheader("All Appointment Records")
        df = pd.DataFrame(records, columns=['ID', 'Patient ID', 'Appointment Date', 'Appointment Time', 'Doctor Name', 'Notes'])
        st.dataframe(df)
    else:
        st.write("No appointments found")

def edit_appointment_record(con, appointment_id, new_appointment_date, new_appointment_time, new_doctor_name, new_notes):
    """Edit an appointment record in the 'appointments' table."""
    cursor = con.cursor()

    # Select the database
    cursor.execute("USE userdb")
    update_appointment_query = """
    UPDATE appointments
    SET appointment_date = ?, appointment_time = ?, doctor_name = ?, notes = ?
    WHERE id = ?
    """
    appointment_data = (new_appointment_date, new_appointment_time, new_doctor_name, new_notes, appointment_id)

    cursor.execute(update_appointment_query, appointment_data)
    con.commit()

def fetch_appointment_by_id(con, appointment_id):
    """Fetch an appointment's record from the 'appointments' table based on ID."""
    cursor = con.cursor()
    # Select the database
    cursor.execute("USE userdb")

    select_appointment_query = """
    SELECT id, patient_id, date(appointment_date), time(appointment_time), doctor_name, notes
    FROM appointments
    WHERE id = ?
    """
    cursor.execute(select_appointment_query, (appointment_id,))
    appointment = cursor.fetchone()

    return appointment

def fetch_appointment_by_patient_id(con, patient_id):
    query = """
    SELECT id, patient_id, date(appointment_date), time(appointment_time), doctor_name, notes
    FROM appointments
    WHERE patient_id = ?
    """
    # Select the database
    cursor = con.cursor()
    cursor.execute(query, (patient_id,))
    appointment = cursor.fetchone()
    return appointment

def fetch_appointment_by_doctor_name(con, doctor_name):
    query = """
    SELECT id, patient_id, date(appointment_date), time(appointment_time), doctor_name, notes
    FROM appointments
    WHERE doctor_name = ?
    """
    cursor = con.cursor()
    cursor.execute("USE userdb")
    cursor.execute(query, (doctor_name,))
    appointment = cursor.fetchone()
    return appointment

def search_appointment(con):
    search_option = st.selectbox("Select search option", ["ID", "Patient ID", "Doctor Name"], key="search_option")
    search_value = st.text_input("Enter search value", key="search_value")

    if st.button("Search"):
        if search_option == "ID":
            appointment = fetch_appointment_by_id(con, search_value)
        elif search_option == "Patient ID":
            appointment = fetch_appointment_by_patient_id(con, search_value)
        elif search_option == "Doctor Name":
            appointment = fetch_appointment_by_doctor_name(con, search_value)

        if appointment:
            st.subheader("Appointment Details")
            df = pd.DataFrame([appointment], columns=['ID', 'Patient ID', 'Appointment Date', 'Appointment Time', 'Doctor Name', 'Notes'])
            st.dataframe(df)
            st.session_state.edit_appointment = appointment
        else:
            st.write("Appointment not found")
    if 'edit_appointment' in st.session_state:
        edit_appointment(con)

def edit_appointment(con):
    appointment = st.session_state.edit_appointment
    st.subheader("Edit Appointment Details")
    if appointment[2]:
        appointment_date = datetime.strptime(appointment[2], "%Y-%m-%d").date() if isinstance(appointment[2], str) else appointment[2]
    else:
        appointment_date = datetime.today().date()  # Default to today's date if None
    new_appointment_date = st.date_input("Appointment Date", value=appointment_date)
    new_appointment_time = st.text_input("Appointment Time", value=appointment[3])
    new_doctor_name = st.text_input("Doctor Name", value=appointment[4])
    new_notes = st.text_input("Notes", value=appointment[5])

    if st.button("Update Appointment"):
        edit_appointment_record(con, appointment[0], new_appointment_date, new_appointment_time, new_doctor_name, new_notes)
        st.write("Appointment record updated successfully.")
        del st.session_state.edit_appointment

def update_patient_record(con):
    """Update a patient's record in the 'patients' table."""

    search_option = st.selectbox("Select search option", ["ID", "Contact Number", "CNIC"], key="search_option")
    search_value = st.text_input("Enter search value", key="search_value")

    if st.button("Search :magic_wand:"):
        if search_option == "ID":
            patient = fetch_patient_by_id(con, search_value)
        elif search_option == "Contact Number":
            patient = fetch_patient_by_contact(con, search_value)
        elif search_option == "CNIC":
            patient = fetch_patient_by_cnic(con, search_value)

        if patient:
            st.subheader("Patient Details")
            df = pd.DataFrame([patient], columns=['ID', 'Name', 'Age', 'Contact Number', 'Email', 'Address', 'Date Added'])
            st.dataframe(df)
            st.session_state.edit_patient = patient
        else:
            st.write("Patient not found")

    if 'edit_patient' in st.session_state:
        edit_patient(con)

def edit_patient(con):
    """Edit a patient's record in the 'patients' table."""

    st.subheader("Edit Patient Details")
    new_name = st.text_input("Enter new name", value=st.session_state.edit_patient[1])
    new_age = st.number_input("Enter new age", value=st.session_state.edit_patient[2])
    new_contact = st.text_input("Enter new contact number", value=st.session_state.edit_patient[3])
    new_email = st.text_input("Enter new email", value=st.session_state.edit_patient[4])
    new_address = st.text_input("Enter new address", value=st.session_state.edit_patient[5])

    if st.button("Update :roller_coaster:"):
        patient_id = st.session_state.edit_patient[0]
        update_patient_info(con, patient_id, new_name, new_age, new_contact, new_email, new_address)

def update_patient_info(con, patient_id, new_name, new_age, new_contact, new_email, new_address):
    """Update a patient's record in the 'patients' table."""
    cursor = con.cursor()

    cursor.execute("USE userdb")
    update_patient_query = """
    UPDATE patients
    SET name = ?, age = ?, contact_number = ?, email = ?, address = ?
    WHERE id = ?
    """
    patient_data = (new_name, new_age, new_contact, new_email, new_address, patient_id)

    cursor.execute(update_patient_query, patient_data)
    con.commit()
    st.write("Patient record updated successfully.")

def main():
    """The main entry point of the program"""
    st.title("Patient Management System :hospital:")
    lott1 = loti("https://assets6.lottiefiles.com/packages/lf20_olluraqu.json")
    lotipatient = loti("https://assets6.lottiefiles.com/packages/lf20_vPnn3K.json")
    con = create_connection()

    #create_patients_table(con)
    #create_appointments_table(con)

    menu = ["Home", "Add patient Record", "Show patient Records", "Search and Edit Patient", "Delete Patients Record",
            "Add patients Appointments", "Show All Appointments", "Search and Edit Patients Appointments"]
    options = st.sidebar.radio("Select an Option :dart:", menu)
    
    if options == "Home":
        st.subheader("Welcome to Hospital Management System")
        st.write("Navigate from sidebar to access database")
        st_lottie(lott1, height=500)

    elif options == "Add patient Record":
        st.subheader("Enter patient details :woman_in_motorized_wheelchair:")
        st_lottie(lotipatient, height=200)
        name = st.text_input("Enter name of patient", key="name")
        age = st.number_input("Enter age of patient", key="age", value=1)
        contact = st.text_input("Enter contact of patient", key="contact")
        email = st.text_input("Enter Email of patient", key="email")
        address = st.text_input("Enter Address of patient", key="address")
        if st.button("add patient record"):
            cursor = con.cursor()
            select_query = """
            SELECT * FROM patients WHERE contact_number=?
            """
            cursor.execute(select_query, (contact,))
            existing_patient = cursor.fetchone()
            if existing_patient:
                st.warning("A patient with the same contact number already exists")
            else:  
                insert_patient_record(con, name, age, contact, email, address)

    elif options == "Show patient Records":
        patients = fetch_all_patients(con)
        if patients:
            st.subheader("All patients Records :magic_wand:")
            df = pd.DataFrame(patients, columns=['ID', 'Name', 'Age', 'Contact Number', 'Email', 'Address', 'Date Added'])
            st.dataframe(df)
        else:
            st.write("No patients found")

    elif options == "Search and Edit Patient":
        update_patient_record(con)

    elif options == "Delete Patients Record":
        st.subheader("Search a patient to delete :skull_and_crossbones:")
        delete_option = st.selectbox("Select delete option", ["ID", "Name", "Contact Number"], key="delete_option")
        delete_value = st.text_input("Enter delete value", key="delete_value")

        

    if st.button("Delete"):
        delete_patient_record(con, delete_option, delete_value)

    elif options == "Add patients Appointments":
          patient_id = st.number_input("Enter patient ID:", key="appointment_patient_id")
          appointment_date = st.date_input("Enter appointment date:", key="appointment_date")
          appointment_time = st.time_input("Enter appointment time:", key="appointment_time")
          doctor_name = st.text_input("Enter doctor's name:", key="appointment_doctor_name")
          notes = st.text_area("Enter appointment notes:", key="appointment_notes")

          if st.button("Add Appointment"):
               insert_appointment_record(con, patient_id, appointment_date, appointment_time, doctor_name, notes)
               st.write("Appointment record added successfully.")    

    elif options=="Show All Appointments":
         show_all_appointments(con)


    elif options == "Search and Edit Patients Appointments":

        search_appointment(con) 
                

    con.close()

if __name__ == "__main__":
    main()
