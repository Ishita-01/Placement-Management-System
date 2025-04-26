import streamlit as st
import pandas as pd
import sqlite3
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

# Database Setup
def create_connection():
    return sqlite3.connect('placement.db')

def create_tables(conn):
    cursor = conn.cursor()
    
    # Students Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                    roll_number TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    branch TEXT NOT NULL,
                    cgpa REAL,
                    linkedin TEXT,
                    email TEXT NOT NULL,
                    graduation_year INTEGER,
                    offer_accepted BOOLEAN DEFAULT 0
                    )''')
    
    # Companies Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS companies (
                    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL,
                    required_branch TEXT,
                    min_cgpa REAL,
                    graduation_year INTEGER,
                    role TEXT,
                    package TEXT
                    )''')
    
    # Create company_branches junction table (MISSING IN YOUR IMPLEMENTATION)
    cursor.execute('''CREATE TABLE IF NOT EXISTS company_branches (
                    company_id INTEGER,
                    branch TEXT,
                    FOREIGN KEY(company_id) REFERENCES companies(company_id),
                    PRIMARY KEY (company_id, branch)
                    )''')
    
    # Selected Students Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS selected_students (
                    selection_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    roll_number TEXT,
                    company_id INTEGER,
                    role TEXT,
                    FOREIGN KEY(roll_number) REFERENCES students(roll_number),
                    FOREIGN KEY(company_id) REFERENCES companies(company_id)
                    )''')
    
    conn.commit()

# CRUD Operations
def add_student(conn, student_data):
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO students 
                   (roll_number, name, branch, cgpa, linkedin, email, graduation_year)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''', student_data)
    conn.commit()

def update_student(conn, roll_number, update_data):
    cursor = conn.cursor()
    cursor.execute('''UPDATE students SET 
                   name=?, branch=?, cgpa=?, linkedin=?, email=?, graduation_year=?
                   WHERE roll_number=?''', 
                   (*update_data, roll_number))
    conn.commit()

def delete_student(conn, roll_number):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE roll_number=?", (roll_number,))
    conn.commit()

def add_company(conn, company_data, branches):
    cursor = conn.cursor()
    try:
        # Insert company
        cursor.execute('''INSERT INTO companies 
                       (company_name, min_cgpa, graduation_year, role, package)
                       VALUES (?, ?, ?, ?, ?)''', company_data)
        company_id = cursor.lastrowid
        
        # Insert branches
        for branch in branches:
            cursor.execute('''INSERT INTO company_branches (company_id, branch)
                           VALUES (?, ?)''', (company_id, branch))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error adding company: {str(e)}")
        return False
    
def update_company(conn, company_id, update_data, branches):
    cursor = conn.cursor()
    cursor.execute('''UPDATE companies SET 
                   company_name=?, required_branch=?, min_cgpa=?, 
                   graduation_year=?, role=?, package=?
                   WHERE company_id=?''', 
                   (*update_data, company_id))
    # Update branches
    cursor.execute("DELETE FROM company_branches WHERE company_id=?", (company_id,))
    for branch in branches:
        cursor.execute('''INSERT INTO company_branches (company_id, branch)
                       VALUES (?, ?)''', (company_id, branch))
    conn.commit()

def delete_company(conn, company_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM companies WHERE company_id=?", (company_id,))
    conn.commit()

# Email Functionality
def send_email(to_email, subject, body):
    # Configure your email settings
    smtp_server = st.secrets["email"]["smtp_server"]
    smtp_port = st.secrets["email"]["smtp_port"]
    sender_email = st.secrets["email"]["username"]
    password = st.secrets["email"]["password"]
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

# Main Application
def main():
    st.title("Placement Cell Management System")
    conn = create_connection()
    create_tables(conn)

    menu = ["Home", "Manage Students", "Manage Companies", 
            "Filter Students", "Process Selections", "View Data"]
    choice = st.sidebar.selectbox("Navigation", menu)

    if choice == "Home":
        st.subheader("Welcome to Placement Portal")
        st.image("https://cdn.pixabay.com/photo/2018/03/10/12/00/paper-3213924_1280.jpg", 
                use_column_width=True)

    elif choice == "Manage Students":
        st.subheader("Student Management")
        action = st.radio("Select Action", ["Add Student", "Update Student", "Delete Student"])

        if action == "Add Student":
            with st.form("student_form"):
                cols = st.columns(2)
                roll_number = cols[0].text_input("Roll Number")
                name = cols[1].text_input("Name")
                branch = cols[0].selectbox("Branch", ["CSE", "ECE", "ME", "EE", "CE"])
                cgpa = cols[1].number_input("CGPA", min_value=0.0, max_value=10.0)
                email = cols[0].text_input("Email")
                linkedin = cols[1].text_input("LinkedIn Profile")
                grad_year = cols[0].number_input("Graduation Year", 
                                               min_value=2023, max_value=2030)
                
                if st.form_submit_button("Add Student"):
                    student_data = (roll_number, name, branch, cgpa, 
                                  linkedin, email, grad_year)
                    add_student(conn, student_data)
                    st.success("Student added successfully!")

        elif action == "Update Student":
            roll_number = st.text_input("Enter Roll Number to Update")
            if roll_number:
                cursor = conn.cursor()
                student = cursor.execute("SELECT * FROM students WHERE roll_number=?", 
                                       (roll_number,)).fetchone()
                if student:
                    with st.form("update_student"):
                        name = st.text_input("Name", value=student[1])
                        branch = st.selectbox("Branch", ["CSE", "ECE", "ME", "EE", "CE"], 
                                           index=["CSE", "ECE", "ME", "EE", "CE"].index(student[2]))
                        cgpa = st.number_input("CGPA", value=student[3])
                        email = st.text_input("Email", value=student[5])
                        linkedin = st.text_input("LinkedIn Profile", value=student[4])
                        grad_year = st.number_input("Graduation Year", value=student[6])
                        
                        if st.form_submit_button("Update Student"):
                            update_data = (name, branch, cgpa, linkedin, email, grad_year)
                            update_student(conn, roll_number, update_data)
                            st.success("Student updated successfully!")
                else:
                    st.warning("Student not found!")

        elif action == "Delete Student":
            roll_number = st.text_input("Enter Roll Number to Delete")
            if st.button("Delete Student"):
                delete_student(conn, roll_number)
                st.success("Student deleted successfully!")

    elif choice == "Manage Companies":
        st.subheader("Company Management")
        action = st.radio("Select Action", ["Add Company", "Update Company", "Delete Company"])
    
        if action == "Add Company":
            with st.form("company_form"):
                cols = st.columns(2)
                company_name = cols[0].text_input("Company Name")
                branches = cols[1].multiselect("Required Branch", ["COPC", "COE", "COBS", "AI/ML", "ME", "EIC","ECE", "EEE","ENC", "RAI"])
                min_cgpa = cols[0].number_input("Minimum CGPA", min_value=0.0, max_value=10.0)
                grad_year = cols[1].number_input("Graduation Year", min_value=2023, max_value=2030)
                role = cols[0].text_input("Job Role")
                package = cols[1].text_input("Package Offered")
                
                if st.form_submit_button("Add Company"):
                    company_data = (company_name, branches, min_cgpa, grad_year, role, package)
                    add_company(conn, company_data)
                    st.success("Company added successfully!")
                elif not branches:
                    st.error("Please select at least one branch")

        elif action == "Update Company":
            company_id = st.number_input("Enter Company ID to Update", min_value=1)
            if company_id:
                cursor = conn.cursor()
                company = cursor.execute("SELECT * FROM companies WHERE company_id=?", 
                                       (company_id,)).fetchone()
                if company:
                    with st.form("update_company"):
                        cols = st.columns(2)
                        company_name = cols[0].text_input("Company Name", value=company[1])
                        branches = cols[1].multiselect("Required Branch", 
                                                          ["CSE", "ECE", "ME", "EE", "CE"],
                                                          index=["CSE", "ECE", "ME", "EE", "CE"].index(company[2]))
                        min_cgpa = cols[0].number_input("Minimum CGPA", value=company[3])
                        grad_year = cols[1].number_input("Graduation Year", value=company[4])
                        role = cols[0].text_input("Job Role", value=company[5])
                        package = cols[1].text_input("Package Offered", value=company[6])
                        
                        if st.form_submit_button("Update Company"):
                            update_data = (company_name, branches, min_cgpa,
                                         grad_year, role, package)
                            update_company(conn, company_id, update_data)
                            st.success("Company updated successfully!")
                else:
                    st.warning("Company not found!")
    
        elif action == "Delete Company":
            company_id = st.number_input("Enter Company ID to Delete", min_value=1)
            if st.button("Delete Company"):
                delete_company(conn, company_id)
                st.success("Company deleted successfully!")
    
            # Similar CRUD operations for companies (implementation similar to student management)
        
    elif choice == "Filter Students":
        st.subheader("Filter Eligible Students")
        cursor = conn.cursor()
        companies = cursor.execute("SELECT company_id, company_name FROM companies").fetchall()
        company_choice = st.selectbox("Select Company", companies, format_func=lambda x: x[1])
        
        if company_choice and st.button("Filter Students"):
            company_id = company_choice[0]
            company = cursor.execute('''SELECT * FROM companies 
                                      WHERE company_id=?''', (company_id,)).fetchone()
            # Get allowed branches
            allowed_branches = [b[0] for b in cursor.execute('''SELECT branch FROM company_branches 
                                                          WHERE company_id=?''', (company_id,)).fetchall()]
            query = '''SELECT s.* FROM students s
                 WHERE s.branch IN ({}) 
                 AND s.cgpa >= ? 
                 AND s.graduation_year=?
                 AND s.offer_accepted=0'''.format(','.join(['?']*len(allowed_branches)))
        
            params = (*allowed_branches, company[2], company[3])
            
            eligible_students = cursor.execute(query, params).fetchall()
            
            if eligible_students:
                df = pd.DataFrame(eligible_students, columns=["Roll Number", "Name", "Branch", 
                                                             "CGPA", "LinkedIn", "Email", 
                                                             "Graduation Year", "Offer Accepted"])
                st.dataframe(df)
                
                if st.button("Notify Eligible Students"):
                    for student in eligible_students:
                        body = f"""Dear {student[1]},
                        
                        You are eligible to apply for {company[1]} ({company[4]} role). 
                        Eligible Branches: {', '.join(allowed_branches)}
                        Minimum CGPA: {company[2]}
                        Graduation Year: {company[3]}
                        
                        Please submit your application before the deadline.
                        
                        Best regards,
                        Placement Cell"""
                        
                        if send_email(student[5], "New Placement Opportunity", body):
                            st.success(f"Email sent to {student[1]}")
            else:
                st.warning("No eligible students found for this company")

    elif choice == "Process Selections":
        st.subheader("Process Company Selections")
        uploaded_file = st.file_uploader("Upload Selection CSV", type=["csv"])
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("Uploaded Selections:")
            st.dataframe(df)
            
            if st.button("Process Selections"):
                cursor = conn.cursor()
                for index, row in df.iterrows():
                    # Verify student acceptance
                    cursor.execute('''UPDATE students SET offer_accepted=1 
                                   WHERE roll_number=?''', (row['roll_number'],))
                    # Add to selected students
                    cursor.execute('''INSERT INTO selected_students 
                                   (roll_number, company_id, role) 
                                   VALUES (?, ?, ?)''', 
                                   (row['roll_number'], row['company_id'], row['role']))
                conn.commit()
                st.success("Selections processed successfully!")

    elif choice == "View Data":
        st.subheader("View Records")
        view_choice = st.radio("Select Data", ["Students", "Companies", "Selected Students"])
        
        if view_choice == "Students":
            all_students = pd.read_sql("SELECT * FROM students", conn)
            st.dataframe(all_students)
        elif view_choice == "Companies":
            companies = pd.read_sql('''
            SELECT c.*, GROUP_CONCAT(cb.branch) AS branches 
            FROM companies c
            LEFT JOIN company_branches cb ON c.company_id = cb.company_id
            GROUP BY c.company_id
            ''', conn)
            st.dataframe(companies)
        elif view_choice == "Selected Students":
            selected_students = pd.read_sql('''SELECT s.roll_number, s.name, c.company_name, ss.role 
                              FROM selected_students ss
                              JOIN students s ON ss.roll_number = s.roll_number
                              JOIN companies c ON ss.company_id = c.company_id''', conn)
            st.dataframe(selected_students)

    conn.close()

if __name__ == "__main__":
    main()
