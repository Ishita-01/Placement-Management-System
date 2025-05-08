import sqlite3
import pandas as pd

def create_connection():
    return sqlite3.connect('placement_portal_1.db', check_same_thread=False)

def create_tables(conn):
    cursor = conn.cursor()

    # Students Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        name TEXT NOT NULL,
        roll_number TEXT PRIMARY KEY,
        branch TEXT NOT NULL,
        cgpa REAL,
        grad_year INTEGER,
        password TEXT NOT NULL,
        placed INTEGER DEFAULT 0
    )''')
    
    # Companies Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        branches TEXT NOT NULL,
        min_cgpa REAL,
        grad_year INTEGER,
        role TEXT NOT NULL,
        package REAL
    )''')
    
    # Eligibility Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS eligibility (
        student_id TEXT,
        company_id INTEGER,
        notified INTEGER DEFAULT 0,
        applied INTEGER DEFAULT 0,
        FOREIGN KEY(student_id) REFERENCES students(roll_number),
        FOREIGN KEY(company_id) REFERENCES companies(id),
        PRIMARY KEY(student_id, company_id)
    )''')
    
    # Selected Students Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS selected_students (
        student_id TEXT,
        company_id INTEGER,
        selection_date TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(student_id) REFERENCES students(roll_number),
        FOREIGN KEY(company_id) REFERENCES companies(id),
        PRIMARY KEY(student_id, company_id)
    )''')
    
    # Notifications Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        student_id TEXT,
        message TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        read INTEGER DEFAULT 0,
        FOREIGN KEY(student_id) REFERENCES students(roll_number)
        PRIMARY KEY (student_id, created_at)
    )''')
    
    conn.commit()

# Student CRUD Operations
def add_student(conn, student_data):
    cursor = conn.cursor()
    # Unpack student data
    name, roll_number, branch, cgpa, grad_year, password = student_data
    # If password is empty, use roll number as password
    if not password:
        password = roll_number
    cursor.execute('''
    INSERT INTO students (name, roll_number, branch, cgpa, grad_year, password)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', student_data)
    conn.commit()
    return cursor.lastrowid

def update_student(conn, student_id, update_data):
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE students SET 
    name=?, branch=?, cgpa=?, grad_year=?, password=?
    WHERE roll_number=?
    ''', (*update_data, student_id))
    conn.commit()

def delete_student(conn, student_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE roll_number=?", (student_id,))
    cursor.execute("DELETE FROM eligibility WHERE student_id=?", (student_id,))
    cursor.execute("DELETE FROM selected_students WHERE student_id=?", (student_id,))
    cursor.execute("DELETE FROM notifications WHERE student_id=?", (student_id,))
    conn.commit()

# Company CRUD Operations
def add_company(conn, company_data):
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO companies (name, branches, min_cgpa, grad_year, role, package)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', company_data)
    conn.commit()
    return cursor.lastrowid

def update_company(conn, company_id, update_data):
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE companies SET
    name=?, branches=?, min_cgpa=?, grad_year=?, role=?, package=?
    WHERE id=?
    ''', (*update_data, company_id))
    conn.commit()

def delete_company(conn, company_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM companies WHERE id=?", (company_id,))
    cursor.execute("DELETE FROM eligibility WHERE company_id=?", (company_id,))
    cursor.execute("DELETE FROM selected_students WHERE company_id=?", (company_id,))
    conn.commit()

# Eligibility Management
def get_eligible_students_for_company(conn, company):
    cursor = conn.cursor()
    if company[2] is not None:
        branches = [b.strip() for b in company[2].split(',')]
    else:
        branches = []

    placeholders = ','.join(['?']*len(branches))
    
    query = f'''
    SELECT s.name, s.roll_number, s.branch, s.cgpa, s.grad_year
    FROM students s
    WHERE s.branch IN ({placeholders})
    AND s.cgpa >= ?
    AND s.grad_year = ?
    AND s.placed = 0
    '''
    
    cursor.execute(query, branches + [company[3], company[4]])
    return cursor.fetchall()

def add_eligibility(conn, student_id, company_id):
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR IGNORE INTO eligibility (student_id, company_id, notified, applied)
    VALUES (?, ?, 1, ?)
    ''', (student_id, company_id, 0))
    
    # Create notification for student
    company_name = get_company_by_id(conn, company_id)[1]
    notification_msg = f"You are eligible for {company_name}. Check your eligibility tab for details."
    add_notification(conn, student_id, notification_msg)
    
    conn.commit()

def set_applied_status(conn, student_id, company_id, status):
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE eligibility SET applied=?
    WHERE student_id=? AND company_id=?
    ''', (status, student_id, company_id))
    conn.commit()

# Selected Students Management
def add_selected_student(conn, student_id, company_id):
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO selected_students (student_id, company_id)
        VALUES (?, ?)
        ''', (student_id, company_id))
        
        # Update student placed status
        cursor.execute('''
        UPDATE students SET placed=1
        WHERE roll_number=?
        ''', (student_id,))
        
        # Create notification for student
        company_name = get_company_by_id(conn, company_id)[1]
        notification_msg = f"Congratulations! You have been selected by {company_name}."
        add_notification(conn, student_id, notification_msg)
        
        conn.commit()
        return True
    except sqlite3.Error:
        conn.rollback()
        return False

def import_selected_students_csv(conn, file, company_id):
    df = pd.read_csv(file)
    success_count = 0
    failed_count = 0
    
    if 'roll_number' not in df.columns:
        return 0, 0, "CSV must contain 'roll_number' column"
    
    for _, row in df.iterrows():
        roll_number = row['roll_number']
        student = get_student_by_roll_without_password(conn, roll_number)
        
        if student:
            try:
                if add_selected_student(conn, student[1], company_id):
                    success_count += 1
                else:
                    failed_count += 1
            except Exception:
                failed_count += 1
        else:
            failed_count += 1
    
    return success_count, failed_count, None

# Notification Management
def add_notification(conn, student_id, message):
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO notifications (student_id, message)
    VALUES (?, ?)
    ''', (student_id, message))
    conn.commit()

def get_notifications(conn, student_id):
    cursor = conn.cursor()
    cursor.execute('''
    SELECT student_id, message, created_at, read
    FROM notifications
    WHERE student_id=?
    ORDER BY created_at DESC
    ''', (student_id,))
    return cursor.fetchall()

def mark_notification_read(conn, student_id, created_at):
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE notifications SET read=1
    WHERE student_id=? AND created_at=?
    ''', (student_id, created_at,))
    conn.commit()

# Data Retrieval
def get_all_students(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY name")
    return cursor.fetchall()

def get_all_companies(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies ORDER BY name")
    return cursor.fetchall()

def get_company_by_id(conn, company_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies WHERE id=?", (company_id,))
    return cursor.fetchone()

def get_student_by_id(conn, student_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE roll_number=?", (student_id,))
    return cursor.fetchone()

def get_eligible_companies_for_student(conn, student_id):
    cursor = conn.cursor()
    cursor.execute('''
    SELECT c.id, c.name, c.branches, c.min_cgpa, c.role, c.package, e.applied
    FROM companies c
    JOIN eligibility e ON c.id = e.company_id
    WHERE e.student_id = ? AND e.notified = 1
    ''', (student_id,))
    return cursor.fetchall()

def get_student_by_roll(conn, roll_number, password):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE roll_number = ? AND password = ?', (roll_number, password))
    return cursor.fetchone()

def get_student_by_roll_without_password(conn, roll_number):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE roll_number = ?', (roll_number,))
    return cursor.fetchone()

def get_selected_students(conn, company_id=None):
    cursor = conn.cursor()
    if company_id:
        cursor.execute('''
        SELECT s.name, s.roll_number, s.branch, s.cgpa, c.name, c.role, c.package, ss.selection_date
        FROM selected_students ss
        JOIN students s ON ss.student_id = s.roll_number
        JOIN companies c ON ss.company_id = c.id
        WHERE ss.company_id = ?
        ORDER BY ss.selection_date DESC
        ''', (company_id,))
    else:
        cursor.execute('''
        SELECT s.name, s.roll_number, s.branch, s.cgpa, c.name, c.role, c.package, ss.selection_date
        FROM selected_students ss
        JOIN students s ON ss.student_id = s.roll_number
        JOIN companies c ON ss.company_id = c.id
        ORDER BY ss.selection_date DESC
        ''')
    return cursor.fetchall()

def get_applied_students_for_company(conn, company):
    cursor = conn.cursor()
    if company[2] is not None:
        branches = [b.strip() for b in company[2].split(',')]
    else:
        branches = []

    placeholders = ','.join(['?'] * len(branches))
    
    query = f'''
    SELECT s.rowid, s.name, s.roll_number, s.branch, s.cgpa, s.grad_year
    FROM students s
    JOIN eligibility e ON s.roll_number = e.student_id
    WHERE s.branch IN ({placeholders})
    AND s.cgpa >= ?
    AND s.grad_year = ?
    AND s.placed = 0
    AND e.company_id = ?
    AND e.applied = 1
    '''

    cursor.execute(query, branches + [company[3], company[4], company[0]])
    return cursor.fetchall()


# Statistics
def get_placement_statistics(conn):
    cursor = conn.cursor()
    stats = {}
    
    # Total students
    cursor.execute("SELECT COUNT(*) FROM students")
    stats['total_students'] = cursor.fetchone()[0]
    
    # Placed students
    cursor.execute("SELECT COUNT(*) FROM students WHERE placed=1")
    stats['placed_students'] = cursor.fetchone()[0]
    
    if stats['total_students'] > 0:
        stats['placement_percentage'] = (stats['placed_students'] / stats['total_students']) * 100
    else:
        stats['placement_percentage'] = 0
    
    # Branch-wise placement
    cursor.execute('''
    SELECT s.branch, COUNT(ss.student_id)
    FROM students s
    JOIN selected_students ss ON s.roll_number = ss.student_id
    GROUP BY s.branch
    ''')
    stats['branch_placements'] = cursor.fetchall()
    
    # Company-wise placement
    cursor.execute('''
    SELECT c.name, COUNT(ss.student_id)
    FROM companies c
    JOIN selected_students ss ON c.id = ss.company_id
    GROUP BY c.id
    ORDER BY COUNT(ss.student_id) DESC
    LIMIT 5
    ''')
    stats['company_placements'] = cursor.fetchall()
    
    # Package statistics
    cursor.execute('''
    SELECT AVG(c.package), MAX(c.package), MIN(c.package)
    FROM selected_students ss
    JOIN companies c ON ss.company_id = c.id
    ''')
    package_stats = cursor.fetchone()
    if package_stats[0] is not None:
        stats['avg_package'] = package_stats[0]
        stats['max_package'] = package_stats[1]
        stats['min_package'] = package_stats[2]
    else:
        stats['avg_package'] = 0
        stats['max_package'] = 0
        stats['min_package'] = 0
    
    return stats

# def fix_database_schema(conn):
#     cursor = conn.cursor()
#     # Check if placed column exists
#     try:
#         cursor.execute("SELECT placed FROM students LIMIT 1")
#         print("Column exists, no action needed")
#     except sqlite3.OperationalError:
#         # Column doesn't exist, add it
#         print("Adding missing placed column")
#         cursor.execute("ALTER TABLE students ADD COLUMN placed INTEGER DEFAULT 0")
#         conn.commit()

#      # Check if selection_date column exists in selected_students table
#     try:
#         cursor.execute("SELECT selection_date FROM selected_students LIMIT 1")
#         print("selection_date column exists, no action needed")
#     except sqlite3.OperationalError:
#         # Column doesn't exist, add it
#         print("Adding missing selection_date column")
#         cursor.execute("ALTER TABLE selected_students ADD COLUMN selection_date TEXT DEFAULT CURRENT_TIMESTAMP")
#         conn.commit()