from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import mysql.connector
import pandas as pd
import numpy as np
import os # NEW: Import os for environment variables

app = Flask(__name__)
# Keep this secret key, but in a real production app, this would also be an os.environ variable!
app.secret_key = 'chanakya_super_secret_key_123' 

# ==========================================
# DATABASE CONNECTION (UPDATED FOR CLOUD)
# ==========================================
def get_db_connection():
    # Use Railway's environment variables, but default to localhost for your local testing
    return mysql.connector.connect(
        host=os.environ.get('MYSQLHOST', 'shinkansen.proxy.rlwy.net'),
        user=os.environ.get('MYSQLUSER', 'root'),
        password=os.environ.get('MYSQLPASSWORD', 'fOkTmcDUHjMzDOwcbPEJxmpLWSRMDlmy'), 
        database=os.environ.get('MYSQLDATABASE', 'railway'),
        port=os.environ.get('MYSQLPORT', 10566)
    )

# ... [Keep the rest of your app.py exactly the same] ...

def clean_and_process_data(df, table_name):
    df = df.drop_duplicates()
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    if table_name == "Sub_Events":
        if 'category' in df.columns:
            df['category'] = df['category'].str.lower()
        if 'description' in df.columns:
            df['description'] = df['description'].fillna("No description provided")
        if 'is_competition' in df.columns:
            df['is_competition'] = pd.to_numeric(df['is_competition'], errors='coerce').fillna(0).astype(int)

    elif table_name == "Participants":
        if 'roll_number' in df.columns:
            df['roll_number'] = df['roll_number'].str.upper()
        if 'full_name' in df.columns:
            df['full_name'] = df['full_name'].str.title().fillna("Unknown Participant")
            
    elif table_name == "Schools_Branches":
        if 'name' in df.columns:
            df['name'] = df['name'].str.title()

    df = df.replace({np.nan: None})
    return df

# ==========================================
# FRONTEND ROUTES
# ==========================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stakeholder')
def stakeholder():
    return render_template('stakeholder.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == '1234':
            session['coordinator_logged_in'] = True
            return redirect(url_for('coordinator'))
        return render_template('login.html', error="Invalid password. Access Denied.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('coordinator_logged_in', None)
    return redirect(url_for('index'))

@app.route('/coordinator')
def coordinator():
    if not session.get('coordinator_logged_in'):
        return redirect(url_for('login'))
    return render_template('dash.html')

# ==========================================
# DATA ENTRY
# ==========================================
@app.route('/upload/<table_name>', methods=['POST'])
def upload_csv(table_name):
    if 'coordinator_logged_in' not in session: return "Unauthorized", 401
    try:
        clean_df = clean_and_process_data(pd.read_csv(request.files['file']), table_name)
        conn = get_db_connection()
        cursor = conn.cursor()
        cols, placeholders = ",".join(clean_df.columns), ",".join(["%s"] * len(clean_df.columns))
        sql = f"INSERT IGNORE INTO {table_name} ({cols}) VALUES ({placeholders})"
        for _, row in clean_df.iterrows(): cursor.execute(sql, tuple(row))
        conn.commit()
        return f"Successfully processed data into {table_name}.", 200
    except Exception as e: return f"Error: {str(e)}", 500
    finally:
        if 'conn' in locals() and conn.is_connected(): cursor.close(); conn.close()

@app.route('/insert/<table_name>', methods=['POST'])
def manual_insert(table_name):
    if 'coordinator_logged_in' not in session: return jsonify({"message": "Unauthorized"}), 401
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cleaned = {k: str(v).strip() for k, v in request.json.items() if str(v).strip() != ""}
        sql = f"INSERT INTO {table_name} ({','.join(cleaned.keys())}) VALUES ({','.join(['%s']*len(cleaned))})"
        cursor.execute(sql, tuple(cleaned.values()))
        conn.commit()
        return jsonify({"message": "Data inserted successfully!"}), 200
    except Exception as e: return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if 'conn' in locals() and conn.is_connected(): cursor.close(); conn.close()

# ==========================================
# ANALYTICS API (Filters and Distinct Counts Fixed)
# ==========================================
# ==========================================
# ANALYTICS API
# ==========================================
@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Safely handle filters
    start_date = request.args.get('start_date') or '2000-01-01'
    end_date = request.args.get('end_date') or '2099-12-31'
    cat_param = request.args.get('category', 'all') 

    # Convert 'all' from frontend into the SQL wildcard '%'
    category_filter = '%' if cat_param == 'all' else cat_param

    # Append time to strictly capture the whole day
    start_dt = f"{start_date} 00:00:00"
    end_dt = f"{end_date} 23:59:59"
    
    analytics_data = {}
    try:
        # 1. Participants per school
        cursor.execute("""
            SELECT s.name AS school_name, COUNT(DISTINCT p.participant_id) AS total_participations
            FROM Schools_Branches s
            JOIN Participants p ON s.sb_id = p.sb_id
            JOIN Event_Registrations er ON p.participant_id = er.participant_id
            JOIN Sub_Events se ON er.sub_event_id = se.sub_event_id
            WHERE se.event_time BETWEEN %s AND %s AND se.category LIKE %s
            GROUP BY s.name ORDER BY total_participations DESC
        """, (start_dt, end_dt, category_filter))
        analytics_data['school_participants'] = cursor.fetchall()

        # 2. Winners per school 
        cursor.execute("""
            SELECT s.name AS school_name, COUNT(DISTINCT cr.result_id) AS total_wins
            FROM Schools_Branches s
            JOIN Participants p ON s.sb_id = p.sb_id
            JOIN Competition_Results cr ON p.participant_id = cr.participant_id
            JOIN Sub_Events se ON cr.sub_event_id = se.sub_event_id
            WHERE se.event_time BETWEEN %s AND %s AND se.category LIKE %s
            GROUP BY s.name ORDER BY total_wins DESC
        """, (start_dt, end_dt, category_filter))
        analytics_data['school_winners'] = cursor.fetchall()

        # 3. Top Students
        cursor.execute("""
            SELECT p.full_name, p.roll_number, COUNT(er.registration_id) AS participation_count
            FROM Participants p
            JOIN Event_Registrations er ON p.participant_id = er.participant_id
            JOIN Sub_Events se ON er.sub_event_id = se.sub_event_id
            WHERE se.event_time BETWEEN %s AND %s AND se.category LIKE %s
            GROUP BY p.participant_id, p.full_name, p.roll_number 
            ORDER BY participation_count DESC LIMIT 3
        """, (start_dt, end_dt, category_filter))
        analytics_data['top_students'] = cursor.fetchall()

        # 4. Category Breakdown
        cursor.execute("""
            SELECT category, COUNT(DISTINCT sub_event_id) AS event_count 
            FROM Sub_Events 
            WHERE event_time BETWEEN %s AND %s AND category LIKE %s
            GROUP BY category
        """, (start_dt, end_dt, category_filter))
        analytics_data['category_breakdown'] = cursor.fetchall()

        # 5. Popular Events
        cursor.execute("""
            SELECT se.sub_event_name, COUNT(er.registration_id) AS total_registrations
            FROM Sub_Events se
            LEFT JOIN Event_Registrations er ON se.sub_event_id = er.sub_event_id
            WHERE se.event_time BETWEEN %s AND %s AND se.category LIKE %s
            GROUP BY se.sub_event_id, se.sub_event_name 
            ORDER BY total_registrations DESC LIMIT 10
        """, (start_dt, end_dt, category_filter))
        analytics_data['popular_events'] = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()
        
    return jsonify(analytics_data)

# ==========================================
# HARDCODED SCHEDULE & LOOKUP
# ==========================================
@app.route('/api/events/schedule', methods=['GET'])
def get_event_schedule():
    upcoming = [
        {"name": "Tech Innovation", "status": "Coming soon"},
        {"name": "Hackathon", "status": "Coming soon"}
    ]
    past = [
        {"name": "AI Workshop", "count": 11},
        {"name": "Cultural Fest", "count": 84},
        {"name": "Tech Fest", "count": 52},
        {"name": "Sports Day", "count": 53}
    ]
    return jsonify({"upcoming_events": upcoming, "past_events": past})

@app.route('/api/student_lookup/<roll_number>', methods=['GET'])
def student_lookup(roll_number):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    roll = roll_number.upper().strip()
    student_data = {}
    try:
        cursor.execute("""
            SELECT se.sub_event_name, se.category, se.event_time
            FROM Participants p JOIN Event_Registrations er ON p.participant_id = er.participant_id
            JOIN Sub_Events se ON er.sub_event_id = se.sub_event_id WHERE p.roll_number = %s ORDER BY se.event_time DESC
        """, (roll,))
        student_data['participation_history'] = cursor.fetchall()

        cursor.execute("""
            SELECT se.sub_event_name, cr.rank_position, cr.award_prize
            FROM Participants p JOIN Competition_Results cr ON p.participant_id = cr.participant_id
            JOIN Sub_Events se ON cr.sub_event_id = se.sub_event_id WHERE p.roll_number = %s
        """, (roll,))
        student_data['competition_results'] = cursor.fetchall()
        
        if not student_data['participation_history'] and not student_data['competition_results']:
            return jsonify({"message": "No records found for this roll number."}), 404
        return jsonify(student_data)
    finally:
        cursor.close(); conn.close()

if __name__ == '__main__':
    app.run(debug=True)
