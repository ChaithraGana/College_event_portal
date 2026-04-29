import os
import pandas as pd
import mysql.connector
from flask import Flask, request, jsonify, render_template
from urllib.parse import urlparse
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# --- DATABASE CONNECTION ---
def get_db_connection():
    db_url = os.getenv('MYSQL_URL')
    if not db_url:
        raise ValueError("MYSQL_URL environment variable is not set")

    url = urlparse(db_url)

    return mysql.connector.connect(
        host=url.hostname,
        user=url.username,
        password=url.password,
        database=url.path[1:],
        port=url.port or 3306
    )

# --- HOME ROUTE (FIXES 404) ---
@app.route('/')
def home():
    return render_template('dashboard.html')

# --- DATA CLEANING ---
def clean_portal_data(data):
    name = str(data.get('name', 'Unnamed Event')).strip().title()
    category = str(data.get('category', 'other')).lower().strip()

    valid_cats = ['technical', 'cultural', 'sports', 'workshop', 'other']
    if category not in valid_cats:
        category = 'other'

    return {
        "main_event_id": int(data['main_event_id']),
        "name": name,
        "category": category,
        "venue_id": int(data['venue_id']),
        "event_time": data['event_time'],
        "org_school_id": data.get('org_school_id'),
        "is_competition": bool(int(data.get('is_competition', 0))),
        "description": str(data.get('description', '')).strip()
    }

# --- API: SUBMIT EVENT ---
@app.route('/api/submit-event', methods=['POST'])
def submit_event():
    raw_data = request.json
    clean = clean_portal_data(raw_data)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO Sub_Events 
            (main_event_id, sub_event_name, category, venue_id, event_time, organizing_school_id, is_competition, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            clean['main_event_id'], clean['name'], clean['category'],
            clean['venue_id'], clean['event_time'], clean['org_school_id'],
            clean['is_competition'], clean['description']
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success", "message": "Data stored successfully ✅"}), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --- ANALYTICS + CHART GENERATION ---
def generate_plots():
    conn = get_db_connection()

    df_p = pd.read_sql("SELECT * FROM Participants", conn)
    df_se = pd.read_sql("SELECT * FROM Sub_Events", conn)
    df_res = pd.read_sql("SELECT * FROM Competition_Results", conn)

    # Handle empty data safely
    if df_p.empty or df_se.empty:
        conn.close()
        return None, None

    # --- PIE CHART ---
    plt.figure(figsize=(5, 5))
    df_p['is_internal'].value_counts().plot(
        kind='pie', labels=['Internal', 'External'], autopct='%1.1f%%'
    )
    plt.title("Internal vs External Participation")

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    pie_chart = base64.b64encode(img.getvalue()).decode()
    plt.close()

    # --- BAR CHART ---
    df_se['event_time'] = pd.to_datetime(df_se['event_time'])
    df_se['month'] = df_se['event_time'].dt.month_name()

    plt.figure(figsize=(7, 4))
    df_se['month'].value_counts().plot(kind='bar')
    plt.title("Events Frequency by Month")

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    bar_chart = base64.b64encode(img.getvalue()).decode()
    plt.close()

    conn.close()
    return pie_chart, bar_chart


# --- DASHBOARD PAGE ---
@app.route('/dashboard')
def dashboard():
    pie_chart, bar_chart = generate_plots()
    return render_template('dashboard.html', pie_chart=pie_chart, bar_chart=bar_chart)


# --- OPTIONAL: API VERSION OF DASHBOARD DATA ---
@app.route('/api/dashboard-data')
def get_dashboard_data():
    conn = get_db_connection()

    df_p = pd.read_sql("SELECT * FROM Participants", conn)
    df_se = pd.read_sql("SELECT * FROM Sub_Events", conn)
    df_res = pd.read_sql("SELECT * FROM Competition_Results", conn)

    ratio = df_p['is_internal'].value_counts(normalize=True).to_dict()

    df_se['event_time'] = pd.to_datetime(df_se['event_time'])
    monthly_trends = df_se.groupby(df_se['event_time'].dt.month_name()).size().to_dict()

    points = {1: 10, 2: 5, 3: 2}
    df_res['points'] = df_res['rank_position'].map(points)
    top_performers = df_res.groupby('participant_id')['points'].sum().sort_values(ascending=False).head(5)

    conn.close()

    return jsonify({
        "ratio": ratio,
        "monthly_trends": monthly_trends,
        "top_performers": top_performers.to_dict()
    })


# --- RUN APP ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
