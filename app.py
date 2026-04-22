import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = "chanakya_university_2026"

# --- 1. DATABASE CONNECTION ---
def get_db_connection():
    # Priority: Railway Environment Variables -> Local Defaults
    try:
        return mysql.connector.connect(
            host=os.getenv('MYSQLHOST', 'localhost'),
            user=os.getenv('MYSQLUSER', 'root'),
            password=os.getenv('MYSQLPASSWORD', ''),
            database=os.getenv('MYSQLDATABASE', 'chanakya_db'),
            port=int(os.getenv('MYSQLPORT', 3306))
        )
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# --- 2. DATA PROCESSING & NORMALIZATION LAYER (Section 2.3) ---
def process_and_clean_metrics(df):
    """
    Cleans and standardizes data before it reaches the dashboard.
    Handles Requirement 2.3: Handling nulls and normalization.
    """
    if df.empty:
        return df

    # A. Handling Nulls
    df['venue'] = df['venue'].fillna('Main Campus')
    df['organizer_name'] = df['organizer_name'].fillna('University Coordinator')
    df['branch'] = df['branch'].fillna('N/A')

    # B. Normalization: Standardize naming conventions
    # Ensures 'school of engineering' and 'School of Engineering' are grouped together
    df['department'] = df['department'].str.strip().str.title()
    df['branch'] = df['branch'].str.strip().str.title()
    
    # C. Data Type Correction
    df['event_date'] = pd.to_datetime(df['event_date'], errors='coerce')
    
    # D. Deduplication
    df = df.drop_duplicates(subset=['name', 'event_date', 'department'])

    return df

# --- 3. ROUTES: DATA ENTRY PORTAL (Section 2.1) ---
@app.route('/')
def index():
    schools = [
        'School of Engineering', 
        'School of Law, Governance & Public Policy', 
        'School of Mathematics & Natural Sciences', 
        'School of Biosciences', 
        'School of Arts, Humanities & Social Sciences'
    ]
    branches = [
        'CSE', 'CSAI', 'ECE','VLSI','Mechanical and Aerospace','civil','Biotechnology'
    ]
    return render_template('index.html', schools=schools, branches=branches)

@app.route('/submit_event', methods=['POST'])
def submit_event():
    conn = get_db_connection()
    if not conn:
        return "Database Connection Failed", 500
    
    cursor = conn.cursor()
    
    # Raw Data Collection
    name = request.form.get('event_name')
    dept = request.form.get('department')
    branch = request.form.get('branch') if dept == 'School of Engineering' else 'N/A'
    category = request.form.get('category')
    date = request.form.get('event_date')
    venue = request.form.get('venue')
    organizer = request.form.get('organizer')
    
    # SQL Insertion with Parameterized Queries (Prevents SQL Injection)
    query = """INSERT INTO events (name, department, branch, category, event_date, venue, organizer_name) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    
    try:
        cursor.execute(query, (name, dept, branch, category, date, venue, organizer))
        conn.commit()
    except Exception as e:
        print(f"Insertion Error: {e}")
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('dashboard'))

# --- 4. ROUTES: ANALYTICS DASHBOARD (Section 2.3) ---
@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    if not conn:
        return "Database Connection Failed", 500

    # Load raw data from MySQL into Pandas
    query = "SELECT * FROM events"
    raw_df = pd.read_sql(query, conn)
    conn.close()

    # Apply Cleaning and Normalization Layer
    clean_df = process_and_clean_metrics(raw_df)

    if clean_df.empty:
        return render_template('dashboard.html', dept_data=[], branch_data=[], cat_data=[], total_events=0)

    # Generate Actionable Insights
    dept_stats = clean_df.groupby('department').size().reset_index(name='count').to_dict(orient='records')
    
    # Filter for Engineering specific branch metrics
    eng_df = clean_df[clean_df['department'] == 'School Of Engineering']
    branch_stats = eng_df.groupby('branch').size().reset_index(name='count').to_dict(orient='records')
    
    cat_stats = clean_df.groupby('category').size().reset_index(name='count').to_dict(orient='records')
    total_events = len(clean_df)

    return render_template('dashboard.html', 
                           dept_data=dept_stats,
                           branch_data=branch_stats,
                           cat_data=cat_stats,
                           total_events=total_events)

if __name__ == '__main__':
    # Local Development Run
    app.run(host='0.0.0.0', port=5000, debug=True)
