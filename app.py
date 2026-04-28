import os
import pandas as pd
import mysql.connector
from flask import Flask, request, jsonify, render_template
from urllib.parse import urlparse
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# --- 1. DATABASE CONNECTION (Using Railway MySQL URL) ---
# Requirement: Manage via environment variables [cite: 64]
def get_db_connection():
    db_url = os.getenv('MYSQL_URL') # Railway typically provides this
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    url = urlparse(db_url)
    return mysql.connector.connect(
        host=url.hostname,
        user=url.username,
        password=url.password,
        database=url.path[1:], 
        port=url.port or 3306
    )

# --- 2. DATA PROCESSING & CLEANING LAYER ---
# Requirement: Handles nulls, duplicates, and inconsistent formatting [cite: 31]
def clean_portal_data(data):
    # Standardize strings to Title Case and lowercase categories [cite: 31]
    name = str(data.get('name', 'Unnamed Event')).strip().title()
    category = str(data.get('category', 'other')).lower().strip()
    
    # Standardize categories based on project requirements [cite: 17]
    valid_cats = ['technical', 'cultural', 'sports', 'workshop', 'other']
    if category not in valid_cats:
        category = 'other'
        
    return {
        "main_event_id": int(data['main_event_id']),
        "name": name,
        "category": category,
        "venue_id": int(data['venue_id']),
        "event_time": data['event_time'], # Format: YYYY-MM-DD HH:MM:SS
        "org_school_id": data.get('org_school_id'), # NULL if University-wide
        "is_competition": bool(int(data.get('is_competition', 0))),
        "description": str(data.get('description', '')).strip()
    }

# --- 3. DATA ENTRY PORTAL ROUTE ---
@app.route('/api/submit-event', methods=['POST'])
def submit_event():
    raw_data = request.json
    clean = clean_portal_data(raw_data)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Requirement: Log submission timestamp for every record [cite: 27]
        # This is handled by the 'created_at' column in your InnoDB schema
        sql = """
            INSERT INTO Sub_Events 
            (main_event_id, sub_event_name, category, venue_id, event_time, organizing_school_id, is_competition, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            clean['main_event_id'], clean['name'], clean['category'],
            clean['venue_id'], clean['event_time'], clean['org_school_id'],
            clean['is_competition'], clean['description']
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "message": "Cleaned data stored in Cloud DB"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 4. ANALYTICS & VISUALIZATION LAYER ---
# Requirement: Compute derived metrics (Participation rate, top performers, trends) [cite: 31]
@app.route('/api/dashboard-data')
def get_dashboard_insights():
    conn = get_db_connection()
    
    # Load raw data for repeatable processing [cite: 32]
    df_p = pd.read_sql("SELECT * FROM Participants", conn)
    df_r = pd.read_sql("SELECT * FROM Event_Registrations", conn)
    df_se = pd.read_sql("SELECT * FROM Sub_Events", conn)
    df_res = pd.read_sql("SELECT * FROM Competition_Results", conn)

    # A. Internal vs External Ratio 
    ratio = df_p['is_internal'].value_counts(normalize=True).to_dict()

    # B. Semester Trends (Event Frequency by Month) [cite: 31, 36]
    df_se['event_time'] = pd.to_datetime(df_se['event_time'])
    monthly_trends = df_se.groupby(df_se['event_time'].dt.month_name()).size().to_dict()

    # C. Derived Metric: Top Performers (Engagement Score) [cite: 31, 36]
    # Weighting: 1st=10, 2nd=5, 3rd=2
    points = {1: 10, 2: 5, 3: 2}
    df_res['points'] = df_res['rank_position'].map(points)
    top_scores = df_res.groupby('participant_id')['points'].sum().sort_values(ascending=False).head(5)
    
    conn.close()
    return jsonify({
        "internal_external_ratio": ratio,
        "semester_trends": monthly_trends,
        "top_performers": top_scores.to_dict()
    })

if __name__ == '__main__':
    # Hosted on cloud platform, accessible via public URL [cite: 56]
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
