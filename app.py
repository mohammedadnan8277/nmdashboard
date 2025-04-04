from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import pandas as pd

app = Flask(__name__)
app.secret_key = '8073797174'  # Change this to a strong secret key!

# Mock user database (replace with real database in production)
USERS = {
    "admin": "Nmadmin@2025"  # username: password
}

# Load data
try:
    df = pd.read_csv("data.csv", encoding="ISO-8859-1", usecols=["College", "District", "University", "Course", "Student Count"])
    df.fillna("", inplace=True)  # Fill NaN with empty strings
    print("Data loaded successfully:", df.head().to_dict(orient="records"))
except Exception as e:
    print(f"Error loading data: {e}")
    df = pd.DataFrame()

# Get unique filter values
filters = {
    "College": df["College"].dropna().unique().tolist(),
    "District": df["District"].dropna().unique().tolist(),
    "University": df["University"].dropna().unique().tolist(),
    "Course": df["Course"].dropna().unique().tolist()
}

# Login page route (GET)
@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

# Login API (POST)
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username in USERS and USERS[username] == password:
        session['logged_in'] = True
        session['username'] = username
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

# Logout API
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route("/check-auth", methods=["GET"])
def check_auth():
    return jsonify({'loggedIn': session.get('logged_in', False)})

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# Dashboard page (protected)
@app.route("/")
@login_required
def index():
    return render_template("dashboard.html")

@app.route("/api/filters", methods=["GET"])
def get_filters():
    print("Serving filters:", filters)
    return jsonify(filters)

@app.route("/api/stats", methods=["POST"])
def get_stats():
    filter_criteria = request.get_json() or {}
    print("Received filters for stats:", filter_criteria)
    
    filtered_df = df.copy()
    for key, value in filter_criteria.items():
        if value:
            filtered_df = filtered_df[filtered_df[key] == value]
    
    stats = {
        "enrolled": int(filtered_df["Student Count"].sum()),
        "completed": len(filtered_df) // 2,
        "inprogress": len(filtered_df) // 4,
        "notstarted": len(filtered_df) // 4,
        "notcompleted": len(filtered_df) // 2
    }
    print("Serving stats:", stats)
    return jsonify(stats)

@app.route("/filter", methods=["POST"])
def filter_data():
    try:
        filter_criteria = request.get_json()
        print("Received filters:", filter_criteria)
        
        filtered_df = df.copy()
        for key, value in filter_criteria.items():
            if value:
                filtered_df = filtered_df[filtered_df[key] == value]

        filtered_data = filtered_df.to_dict(orient="records")
        print("Filtered data:", filtered_data)
        return jsonify(filtered_data)
    
    except Exception as e:
        print(f"Error in filter_data: {e}")
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
