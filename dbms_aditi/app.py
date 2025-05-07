import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tempfile
import os
from PIL import Image
from datetime import datetime
from database import *

# Initialize database
conn = create_connection()
fix_database_schema(conn) 
create_tables(conn)


# Page Configuration
st.set_page_config(
    page_title="Placement Portal", 
    page_icon="🎯", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# Logout function
def logout():
    st.session_state.logged_in = False
    st.session_state.user_type = None
    st.session_state.user_id = None
    st.session_state.user_name = None

# Custom CSS


st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #000000;
        text-align: center;
        margin-bottom: 1rem;
    }
     .stRadio div, .stTextInput label, .stsubheader {
        color: white !important;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #333;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .card {
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .blue-card {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
    }

    .green-card {
            background: linear-gradient(135deg, #3a0ca3, #7209b7);

    }
    .notification {
        padding: 0.8rem;
        border-radius: 5px;
        margin-bottom: 0.5rem;
    }
    .unread {
       background: linear-gradient(135deg, #1e3c72, #2a5298);
    }
    .read {
        background: linear-gradient(135deg, #3a0ca3, #7209b7);
    }
    .stat-box {
        background: linear-gradient(135deg, #3a0ca3, #7209b7);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .stat-value {
        font-size: 3rem;
        font-weight: bold;
        color: white;
    }
    .stat-label {
        font-size: 1rem;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)


#  authentication

if not st.session_state.logged_in:
    # st.subheader("Login")
    st.markdown(
    """
    <h1 class="main-header" style="color: black;">🎯 Placement Portal</h1>
    """,
    unsafe_allow_html=True
    )
    st.markdown('<h3 style="color: black; font-weight: bold;">Login</h3>', unsafe_allow_html=True)
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #000000;
        text-align: center;
        margin-bottom: 1rem;
    }
     .stRadio div, .stTextInput label, .stsubheader {
        color: black !important;
        font-weight: bold;
    }</style>
""", unsafe_allow_html=True)
    user_type = st.radio("Select User Type", ["Placement Coordinator", "Student"])
    
    if user_type == "Placement Coordinator":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username == "admin" and password == "admin":
                st.session_state.logged_in = True
                st.session_state.user_type = "coordinator"
                st.session_state.user_name = "Admin"
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials!")
    
    elif user_type == "Student":
        roll_number = st.text_input("Roll Number")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            student = get_student_by_roll(conn, roll_number, password)
            if student:
                st.session_state.logged_in = True
                st.session_state.user_type = "student"
                st.session_state.user_id = student[0]
                st.session_state.user_name = student[1]
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials!")




# Set page config for wide layout and center alignment



# Close login-box and container divs
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown(
    """
    <h1 class="main-header" style="color: white;">🎯 Placement Portal</h1>
    """,
    unsafe_allow_html=True
)
    st.button("Logout", on_click=logout)
    st.write(f"Welcome, **{st.session_state.user_name}**")
    
    
    if st.session_state.user_type == "coordinator":
        menu = st.radio("Navigation", [
            "Dashboard", 
            "Manage Students", 
            "Manage Companies", 
            "Notify Students", 
            "Selected Students"
        ])
    elif st.session_state.user_type == "student":
        menu = st.radio("Navigation", [
            "Profile", 
            "Eligible Companies", 
            "Notifications", 
            "Placement Statistics"
        ])

# Main content
if not st.session_state.logged_in:
    
    

    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://theplan.it//awardsContest/2019/Education/3194/1_Thapar_Student_Residencies.jpg");
            background-size: cover;
            background-attachment: fixed;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

  

# Coordinator Portal
elif st.session_state.user_type == "coordinator":
    
    # Dashboard
    if menu == "Dashboard":
        st.markdown('<h2 class="sub-header">Placement Dashboard</h2>', unsafe_allow_html=True)
        
        # Get statistics
        stats = get_placement_statistics(conn)
        
        # Top row statistics
        col1, col2, col3 = st.columns(3)
        
       
        with col1:
            st.markdown('<div class="stat-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="stat-value">{stats["placed_students"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="stat-label">Placed Students</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stat-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="stat-value">{stats["placed_students"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="stat-label">Placed Students</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="stat-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="stat-value">{stats["placement_percentage"]:.1f}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="stat-label">Placement Percentage</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Package statistics
        st.markdown("### Package Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="stat-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="stat-value">₹{float(stats["avg_package"]):.2f}L</div>', unsafe_allow_html=True)
            st.markdown('<div class="stat-label">Average Package</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stat-box">', unsafe_allow_html=True)
            max_package = float(stats["max_package"].replace(" LPA", "").strip())
           
            st.markdown(f'<div class="stat-value">₹{max_package:.2f}L</div>', unsafe_allow_html=True)
            st.markdown('<div class="stat-label">Highest Package</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="stat-box">', unsafe_allow_html=True)
            min_package = float(stats["min_package"].replace(" LPA", "").strip())
            
            st.markdown(f'<div class="stat-value">₹{min_package:.2f}L</div>', unsafe_allow_html=True)
            st.markdown('<div class="stat-label">Lowest Package</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Placement graphs
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Branch-wise Placements")
            if stats['branch_placements']:
                branch_df = pd.DataFrame(stats['branch_placements'], columns=['Branch', 'Count'])
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.bar(branch_df['Branch'], branch_df['Count'], color='skyblue')
                ax.set_xlabel('Branch')
                ax.set_ylabel('Number of Placements')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("No branch placement data available yet")
        
        with col2:
            st.markdown("### Top Recruiting Companies")
            if stats['company_placements']:
                company_df = pd.DataFrame(stats['company_placements'], columns=['Company', 'Count'])
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.bar(company_df['Company'], company_df['Count'], color='lightgreen')
                ax.set_xlabel('Company')
                ax.set_ylabel('Number of Selections')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("No company placement data available yet")
        
        # Recent placements
        st.markdown("### Recent Placements")
        selected = get_selected_students(conn)
        if selected:
            df = pd.DataFrame(selected, columns=[
                'ID', 'Name', 'Roll Number', 'Branch', 'CGPA', 
                'Company', 'Role', 'Package (LPA)', 'Selection Date'
            ])
            st.dataframe(df[['Name', 'Roll Number', 'Branch', 'Company', 'Role', 'Package (LPA)', 'Selection Date']], use_container_width=True)
        else:
            st.info("No placement data available yet")
    
    # Student Management
    elif menu == "Manage Students":
        st.markdown('<h2 class="sub-header">Student Management</h2>', unsafe_allow_html=True)
        
        tabs = st.tabs(["View Students", "Add Student", "Update Student", "Delete Student", "Import/Export CSV"])
        
        # View Students Tab
        with tabs[0]:
            students = get_all_students(conn)
            if students:
                df = pd.DataFrame(students, columns=[
                    'ID', 'Name', 'Roll Number', 'Branch', 'CGPA', 
                    'Graduation Year', 'Password', 'Placed'
                ])
                df['Placed'] = df['Placed'].apply(lambda x: 'Yes' if x == 1 else 'No')
                st.dataframe(df[['Name', 'Roll Number', 'Branch', 'CGPA', 'Graduation Year', 'Placed']], use_container_width=True)
            else:
                st.info("No students found in the database.")
        
        # Add Student Tab
        with tabs[1]:
            with st.form("add_student_form"):
                st.subheader("Add New Student")
                name = st.text_input("Name")
                roll_number = st.text_input("Roll Number")
                branch = st.selectbox("Branch", ["CSE", "IT", "ECE", "EEE", "MECH", "CIVIL", "OTHER"])
                if branch == "OTHER":
                    branch = st.text_input("Specify Branch")
                cgpa = st.number_input("CGPA", 0.0, 10.0, step=0.1)
                grad_year = st.number_input("Graduation Year", 2024, 2030)
                password = st.text_input("Password (Leave empty to use roll number)", type="password")
                
                submit = st.form_submit_button("Add Student")
                if submit:
                    if name and roll_number and branch and password:
                        try:
                            add_student(conn, (name, roll_number, branch, cgpa, grad_year, password))
                            st.success(f"Student {name} added successfully!")
                        except sqlite3.IntegrityError:
                            st.error(f"Roll number {roll_number} already exists!")
                    else:
                        st.error("Please fill all required fields.")
        
        # Update Student Tab
        with tabs[2]:
            students = get_all_students(conn)
            if students:
                selected = st.selectbox(
                    "Select Student to Update", 
                    students, 
                    format_func=lambda x: f"{x[1]} ({x[2]})"
                )
                
                if selected:
                    with st.form("update_student_form"):
                        st.subheader(f"Update Student: {selected[1]}")
                        name = st.text_input("Name", value=selected[1])
                        branch = st.selectbox("Branch", ["CSE", "IT", "ECE", "EEE", "MECH", "CIVIL", "OTHER"], index=["CSE", "IT", "ECE", "EEE", "MECH", "CIVIL"].index(selected[3]) if selected[3] in ["CSE", "IT", "ECE", "EEE", "MECH", "CIVIL"] else 6)
                        if branch == "OTHER":
                            branch = st.text_input("Specify Branch", value=selected[3])
                        cgpa = st.number_input("CGPA", 0.0, 10.0, value=selected[4], step=0.1)
                        grad_year = st.number_input("Graduation Year", 2024, 2030, value=selected[5])
                        password = st.text_input("Password", value=selected[6], type="password")
                        
                        submit = st.form_submit_button("Update Student")
                        if submit:
                            if name and branch and password:
                                update_student(conn, selected[0], (name, branch, cgpa, grad_year, password))
                                st.success(f"Student {name} updated successfully!")
                            else:
                                st.error("Please fill all required fields.")
            else:
                st.info("No students found in the database.")
        
        # Delete Student Tab
        with tabs[3]:
            students = get_all_students(conn)
            if students:
                selected = st.selectbox(
                    "Select Student to Delete", 
                    students, 
                    format_func=lambda x: f"{x[1]} ({x[2]})",
                    key="delete_student"
                )
                
                if selected:
                    st.warning(f"Are you sure you want to delete {selected[1]} ({selected[2]})? This action cannot be undone.")
                    if st.button("Delete Student"):
                        delete_student(conn, selected[0])
                        st.success(f"Student {selected[1]} deleted successfully!")
                        st.experimental_rerun()
            else:
                st.info("No students found in the database.")
        
        # Import/Export CSV Tab
        with tabs[4]:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Import Students from CSV")
                csv_file = st.file_uploader("Upload Student CSV", type=["csv"])
                if csv_file:
                    df = pd.read_csv(csv_file)
                    st.write("Preview:")
                    st.dataframe(df.head())
                    
                    required_cols = ["name", "roll_number", "branch", "cgpa", "grad_year", "password"]
                    if all(col in df.columns for col in required_cols):
                        if st.button("Import Students"):
                            success_count = 0
                            error_count = 0
                            
                            for _, row in df.iterrows():
                                try:
                                    student_data = list(row[required_cols])
                                    if pd.isna(student_data[5]) or student_data[5] == '':
                                        student_data[5] = student_data[1]  
                                    add_student(conn, tuple(student_data))
                                    success_count += 1
                                except Exception as e:
                                    error_count += 1
                            
                            st.success(f"Successfully imported {success_count} students")
                            if error_count > 0:
                                st.warning(f"{error_count} students could not be imported (possibly duplicates)")
                    else:
                        st.error(f"CSV must contain columns: {', '.join(required_cols)}")
            
            with col2:
                st.subheader("Export Students to CSV")
                if st.button("Export All Students"):
                    students = get_all_students(conn)
                    if students:
                        df = pd.DataFrame(students, columns=[
                            'id', 'name', 'roll_number', 'branch', 'cgpa', 
                            'grad_year', 'password', 'placed'
                        ])
                        
                        # Don't include id and convert placed to yes/no
                        export_df = df[['name', 'roll_number', 'branch', 'cgpa', 'grad_year', 'password']]
                        
                        # Convert to CSV
                        csv = export_df.to_csv(index=False)
                        st.download_button(
                            "Download CSV",
                            csv,
                            "students.csv",
                            "text/csv",
                            key='download-students-csv'
                        )
                    else:
                        st.info("No students found in the database.")
    
    # Company Management
    elif menu == "Manage Companies":
        st.markdown('<h2 class="sub-header">Company Management</h2>', unsafe_allow_html=True)
        
        tabs = st.tabs(["View Companies", "Add Company", "Update Company", "Delete Company", "Import/Export CSV"])
        
        # View Companies Tab
        with tabs[0]:
            companies = get_all_companies(conn)
            if companies:
                df = pd.DataFrame(companies, columns=[
                    'ID', 'Name', 'Eligible Branches', 'Min CGPA', 
                    'Graduation Year', 'Role', 'Package (LPA)'
                ])
                st.dataframe(df.drop('ID', axis=1), use_container_width=True)
            else:
                st.info("No companies found in the database.")
        
        # Add Company Tab
        with tabs[1]:
            with st.form("add_company_form"):
                st.subheader("Add New Company")
                name = st.text_input("Company Name")
                
                # Multi-select for branches
                all_branches = ["CSE", "IT", "ECE", "EEE", "MECH", "CIVIL"]
                selected_branches = st.multiselect("Eligible Branches", all_branches)
                branches = ",".join(selected_branches)
                
                min_cgpa = st.number_input("Minimum CGPA Required", 0.0, 10.0, step=0.1)
                grad_year = st.number_input("Graduation Year", 2024, 2030)
                role = st.text_input("Role Offered")
                package = st.number_input("Package (LPA)", 0.0, 100.0, step=0.1)
                
                submit = st.form_submit_button("Add Company")
                if submit:
                    if name and branches and role:
                        add_company(conn, (name, branches, min_cgpa, grad_year, role, package))
                        st.success(f"Company {name} added successfully!")
                    else:
                        st.error("Please fill all required fields.")
        
        # Update Company Tab
        with tabs[2]:
            companies = get_all_companies(conn)
            if companies:
                selected = st.selectbox(
                    "Select Company to Update", 
                    companies, 
                    format_func=lambda x: f"{x[1]} - {x[5]}"
                )
                
                if selected:
                    with st.form("update_company_form"):
                        st.subheader(f"Update Company: {selected[1]}")
                        name = st.text_input("Company Name", value=selected[1])
                        
                        # Multi-select for branches with pre-selected values
                        all_branches = ["CSE", "IT", "ECE", "EEE", "MECH", "CIVIL"]
                        
                        if selected[2] is not None:
                            current_branches = selected[2].split(',')
                        else:
                            current_branches = []  # Default to an empty list

                        selected_branches = st.multiselect(
                            "Eligible Branches", 
                            all_branches,
                            default=[b for b in current_branches if b in all_branches]
                        )
                        branches = ",".join(selected_branches)
                        
                        min_cgpa = st.number_input("Minimum CGPA Required", 0.0, 10.0, value=selected[3], step=0.1)
                        grad_year = st.number_input("Graduation Year", 2024, 2030, value=selected[4])
                        role = st.text_input("Role Offered", value=selected[5])
                        package_str = selected[6]
                        package = float(package_str.replace(" LPA", "").strip())
                        package = st.number_input("Package (LPA)", 0.0, 100.0, value=package, step=0.1)
                        
                        submit = st.form_submit_button("Update Company")
                        if submit:
                            if name and branches and role:
                                update_company(conn, selected[0], (name, branches, min_cgpa, grad_year, role, package))
                                st.success(f"Company {name} updated successfully!")
                            else:
                                st.error("Please fill all required fields.")
            else:
                st.info("No companies found in the database.")
        
        # Delete Company Tab
        with tabs[3]:
            companies = get_all_companies(conn)
            if companies:
                selected = st.selectbox(
                    "Select Company to Delete", 
                    companies, 
                    format_func=lambda x: f"{x[1]} - {x[5]}",
                    key="delete_company"
                )
                
                if selected:
                    st.warning(f"Are you sure you want to delete {selected[1]}? This action cannot be undone.")
                    if st.button("Delete Company"):
                        delete_company(conn, selected[0])
                        st.success(f"Company {selected[1]} deleted successfully!")
                        st.experimental_rerun()
            else:
                st.info("No companies found in the database.")
        
        # Import/Export CSV Tab
        with tabs[4]:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Import Companies from CSV")
                csv_file = st.file_uploader("Upload Company CSV", type=["csv"])
                if csv_file:
                    df = pd.read_csv(csv_file)
                    st.write("Preview:")
                    st.dataframe(df.head())
                    
                    required_cols = ["name", "branches", "min_cgpa", "grad_year", "role", "package"]
                    if all(col in df.columns for col in required_cols):
                        if st.button("Import Companies"):
                            success_count = 0
                            error_count = 0
                            
                            for _, row in df.iterrows():
                                try:
                                    add_company(conn, tuple(row[required_cols]))
                                    success_count += 1
                                except Exception as e:
                                    error_count += 1
                            
                            st.success(f"Successfully imported {success_count} companies")
                            if error_count > 0:
                                st.warning(f"{error_count} companies could not be imported")
                    else:
                        st.error(f"CSV must contain columns: {', '.join(required_cols)}")
            
            with col2:
                st.subheader("Export Companies to CSV")
                if st.button("Export All Companies"):
                    companies = get_all_companies(conn)
                    if companies:
                        df = pd.DataFrame(companies, columns=[
                            'id', 'name', 'branches', 'min_cgpa', 
                            'grad_year', 'role', 'package'
                        ])
                        
                        # Don't include id
                        export_df = df[['name', 'branches', 'min_cgpa', 'grad_year', 'role', 'package']]
                        
                        # Convert to CSV
                        csv = export_df.to_csv(index=False)
                        st.download_button(
                            "Download CSV",
                            csv,
                            "companies.csv",
                            "text/csv",
                            key='download-companies-csv'
                        )
                    else:
                        st.info("No companies found in the database.")
    
    # Notify Students Tab
    elif menu == "Notify Students":
        st.markdown('<h2 class="sub-header">Notify Eligible Students</h2>', unsafe_allow_html=True)
        
        companies = get_all_companies(conn)
        if companies:
            selected_company = st.selectbox(
                "Select Company", 
                companies, 
                format_func=lambda x: f"{x[1]} - {x[5]} (Min CGPA: {x[3]})"
            )
            
            if selected_company:
                st.markdown(f"""
                <div class='card blue-card'>
                    <h3>{selected_company[1]}</h3>
                    <p><strong>Role:</strong> {selected_company[5]}</p>
                    <p><strong>Package:</strong> {selected_company[6]} LPA</p>
                    <p><strong>Eligible Branches:</strong> {selected_company[2]}</p>
                    <p><strong>Min CGPA:</strong> {selected_company[3]}</p>
                    <p><strong>Graduation Year:</strong> {selected_company[4]}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Get eligible students
                eligible_students = get_eligible_students_for_company(conn, selected_company)
                
                if eligible_students:
                    st.subheader(f"Eligible Students ({len(eligible_students)})")
                    df = pd.DataFrame(eligible_students, columns=[
                        'ID', 'Name', 'Roll Number', 'Branch', 'CGPA', 'Graduation Year'
                    ])
                    st.dataframe(df.drop('ID', axis=1), use_container_width=True)
                    
                    if st.button("Notify All Eligible Students"):
                        for student in eligible_students:
                            add_eligibility(conn, student[0], selected_company[0])
                        st.success(f"Successfully notified {len(eligible_students)} students about {selected_company[1]}!")
                else:
                    st.info("No eligible students found for this company's criteria.")
        else:
            st.info("No companies found in the database. Please add companies first.")
    
    # Selected Students Tab
    elif menu == "Selected Students":
        st.markdown('<h2 class="sub-header">Selected Students Management</h2>', unsafe_allow_html=True)
        
        tabs = st.tabs(["View Selected Students", "Mark Students as Selected", "Import Selected Students CSV"])
        
        # View Selected Students Tab
        with tabs[0]:
            companies = get_all_companies(conn)
            if companies:
                filter_company = st.selectbox(
                    "Filter by Company (Optional)", 
                    [None] + companies, 
                    format_func=lambda x: x[1] if x else "All Companies"
                )
                
                if filter_company:
                    selected_students = get_selected_students(conn, filter_company[0])
                else:
                    selected_students = get_selected_students(conn)
                
                if selected_students:
                    df = pd.DataFrame(selected_students, columns=[
                        'ID', 'Name', 'Roll Number', 'Branch', 'CGPA', 
                        'Company', 'Role', 'Package (LPA)', 'Selection Date'
                    ])
                    st.dataframe(df[['Name', 'Roll Number', 'Branch', 'CGPA', 'Company', 'Role', 'Package (LPA)', 'Selection Date']], use_container_width=True)
                else:
                    st.info("No selected students found.")
            else:
                st.info("No companies found in the database.")
        
        # Mark Students as Selected Tab
        with tabs[1]:
            companies = get_all_companies(conn)
            if companies:
                selected_company = st.selectbox(
                    "Select Company", 
                    companies, 
                    format_func=lambda x: f"{x[1]} - {x[5]}"
                )
                
                if selected_company:
                    # Get eligible students
                    eligible_students = get_eligible_students_for_company(conn, selected_company)
                    
                    if eligible_students:
                        st.subheader("Select Students to Mark as Placed")
                        selected_student_ids = st.multiselect(
                            "Select Students", 
                            eligible_students,
                            format_func=lambda x: f"{x[1]} ({x[2]}) - CGPA: {x[4]}"
                        )
                        
                        if st.button("Mark Selected Students as Placed"):
                            for student in selected_student_ids:
                                add_selected_student(conn, student[0], selected_company[0])
                            st.success(f"{len(selected_student_ids)} students marked as placed at {selected_company[1]}!")
                    else:
                        st.info("No eligible students found for this company.")
            else:
                st.info("No companies found in the database.")
        
        # Import Selected Students CSV Tab
        with tabs[2]:
            st.subheader("Import Selected Students from CSV")
            
            companies = get_all_companies(conn)
            if companies:
                selected_company = st.selectbox(
                    "Select Company for Import", 
                    companies, 
                    format_func=lambda x: f"{x[1]} - {x[5]}",
                    key="import_selected_company"
                )
                
                if selected_company:
                    st.write("Upload a CSV file with the roll numbers of selected students")
                    st.info("CSV must contain a column named 'roll_number'")
                    
                    csv_file = st.file_uploader("Upload Selected Students CSV", type=["csv"])
                    if csv_file:
                        df = pd.read_csv(csv_file)
                        st.write("Preview:")
                        st.dataframe(df.head())
                        
                        if 'roll_number' in df.columns:
                            if st.button("Import Selected Students"):
                                success_count, failed_count, error = import_selected_students_csv(
                                    conn, csv_file, selected_company[0]
                                )
                                
                                if error:
                                    st.error(error)
                                else:
                                    st.success(f"Successfully marked {success_count} students as placed")
                                    if failed_count > 0:
                                        st.warning(f"{failed_count} students could not be marked (possibly invalid roll numbers or already placed)")
                        else:
                            st.error("CSV must contain a column named 'roll_number'")
            else:
                st.info("No companies found in the database.")

# Student Portal
elif st.session_state.user_type == "student":
    student_id = st.session_state.user_id
    student = get_student_by_id(conn, student_id)
    
    # Profile Tab
    if menu == "Profile":
        st.markdown('<h2 class="sub-header">Student Profile</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="card blue-card">
                <h3>Personal Information</h3>
                <p><strong>Name:</strong> {student[1]}</p>
                <p><strong>Roll Number:</strong> {student[2]}</p>
                <p><strong>Branch:</strong> {student[3]}</p>
                <p><strong>CGPA:</strong> {student[4]}</p>
                <p><strong>Graduation Year:</strong> {student[5]}</p>
                <p><strong>Placement Status:</strong> {'Placed' if student[7] == 1 else 'Not Placed'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if student[7] == 1:  # If student is placed
                # Get placement details
                cursor = conn.cursor()
                cursor.execute('''
                SELECT c.name, c.role, c.package, ss.selection_date
                FROM selected_students ss
                JOIN companies c ON ss.company_id = c.id
                WHERE ss.student_id = ?
                ''', (student_id,))
                placement = cursor.fetchone()
                
                if placement:
                    st.markdown(f"""
                    <div class="card green-card">
                        <h3>Placement Information</h3>
                        <p><strong>Company:</strong> {placement[0]}</p>
                        <p><strong>Role:</strong> {placement[1]}</p>
                        <p><strong>Package:</strong> {placement[2]} LPA</p>
                        <p><strong>Selection Date:</strong> {placement[3]}</p>
                        <p>Congratulations on your placement!</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Eligible Companies Tab
    elif menu == "Eligible Companies":
        st.markdown('<h2 class="sub-header">Eligible Companies</h2>', unsafe_allow_html=True)
        
        # Get eligible companies for the student
        eligible_companies = get_eligible_companies_for_student(conn, student_id)
        
        if eligible_companies:
            st.write(f"You are eligible for {len(eligible_companies)} companies:")
            
            for company in eligible_companies:
                with st.expander(f"{company[1]} - {company[4]}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Role:** {company[4]}")
                        st.write(f"**Package:** {company[5]} LPA")
                        st.write(f"**Minimum CGPA:** {company[3]}")
                    
                    with col2:
                        st.write(f"**Eligible Branches:** {company[2]}")
                        applied_status = "Applied" if company[6] == 1 else "Not Applied"
                        
                        if company[6] == 0:  # Not applied
                            if st.button("Apply Now", key=f"apply_{company[0]}"):
                                set_applied_status(conn, student_id, company[0], 1)
                                st.success(f"Successfully applied to {company[1]}!")
                                st.experimental_rerun()
                        else:  # Already applied
                            st.success("You have already applied for this company")
        else:
            st.info("You are not eligible for any companies at the moment. Check back later for updates.")
    
    # Notifications Tab
    elif menu == "Notifications":
        st.markdown('<h2 class="sub-header">Your Notifications</h2>', unsafe_allow_html=True)
        
        notifications = get_notifications(conn, student_id)
        
        if notifications:
            for notification in notifications:
                read_class = "read" if notification[3] == 1 else "unread"
                st.markdown(f"""
                <div class="notification {read_class}">
                    <p>{notification[1]}</p>
                    <small>Date: {notification[2]}</small>
                </div>
                """, unsafe_allow_html=True)
                
                if notification[3] == 0:  # Unread
                    if st.button("Mark as Read", key=f"notif_{notification[0]}"):
                        mark_notification_read(conn, notification[0])
                        st.experimental_rerun()
        else:
            st.info("You have no notifications at the moment.")
    
    # Placement Statistics Tab
    elif menu == "Placement Statistics":
        st.markdown('<h2 class="sub-header">Placement Statistics</h2>', unsafe_allow_html=True)
        
        # Get statistics
        stats = get_placement_statistics(conn)
        
        # Display statistics in a student-friendly way
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="stat-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="stat-value">{stats["placement_percentage"]:.1f}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="stat-label">Placement Percentage</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stat-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="stat-value">₹{stats["avg_package"]:.2f}L</div>', unsafe_allow_html=True)
            st.markdown('<div class="stat-label">Average Package</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="stat-box">', unsafe_allow_html=True)
            try:
                max_package = float(stats["max_package"].replace(" LPA", "").strip())
                # max_package = st.number_input("Package (LPA)", 0.0, 100.0, value=max_package, step=0.1)
            except ValueError:
                max_package = 0.0  # Default value if conversion fails
            
            st.markdown(f'<div class="stat-value">₹{max_package:.2f}L</div>', unsafe_allow_html=True)

            st.markdown('<div class="stat-label">Highest Package</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Branch-wise placements (with focus on student's branch)
        st.subheader("Branch-wise Placement Percentage")
        
        if stats['branch_placements']:
            branch_df = pd.DataFrame(stats['branch_placements'], columns=['Branch', 'Count'])
            
            # Get total students per branch
            cursor = conn.cursor()
            cursor.execute("SELECT branch, COUNT(*) FROM students GROUP BY branch")
            branch_totals = cursor.fetchall()
            
            total_df = pd.DataFrame(branch_totals, columns=['Branch', 'Total'])
            
            # Merge to calculate percentages
            merged_df = pd.merge(branch_df, total_df, on='Branch', how='right').fillna(0)
            merged_df['Percentage'] = (merged_df['Count'] / merged_df['Total'] * 100).round(1)
            
            # Highlight student's branch
            student_branch = student[3]
            colors = ['#1E88E5' if branch == student_branch else 'lightgray' for branch in merged_df['Branch']]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(merged_df['Branch'], merged_df['Percentage'], color=colors)
            ax.set_xlabel('Branch')
            ax.set_ylabel('Placement Percentage (%)')
            ax.set_ylim(0, 100)
            
            for i, v in enumerate(merged_df['Percentage']):
                ax.text(i, v + 3, f"{v}%", ha='center')
            
            plt.tight_layout()
            st.pyplot(fig)
            
            if student_branch in merged_df['Branch'].values:
                branch_index = merged_df[merged_df['Branch'] == student_branch].index[0]
                branch_percentage = merged_df.loc[branch_index, 'Percentage']
                st.info(f"Your branch ({student_branch}) has a placement percentage of {branch_percentage}%")
        else:
            st.info("No branch placement data available yet")
        
        # Top companies by package
        st.subheader("Top Companies by Package")
        cursor = conn.cursor()
        cursor.execute('''
        SELECT name, role, package 
        FROM companies 
        ORDER BY package DESC 
        LIMIT 5
        ''')
        top_companies = cursor.fetchall()
        
        if top_companies:
            df = pd.DataFrame(top_companies, columns=['Company', 'Role', 'Package (LPA)'])
            st.table(df)
        else:
            st.info("No company data available yet")