from flask import Flask, render_template, request, url_for, session, redirect
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2


app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role'].title()  # Ensure role is capitalized
        hashed_password = generate_password_hash(password)

        try:
            conn = psycopg2.connect(
                host="localhost",
                database="crm_db",
                user="your_db_user",
                password="your_db_password"
            )
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)",
                (username, hashed_password, email, role)
            )
            conn.commit()
            cur.close()
            conn.close()
            return "User registered successfully!"
        except Exception as e:
            return f"An error occurred: {e}"
    return render_template('signup.html')

@app.route('/')
def home():
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = psycopg2.connect(
                host="localhost",
                database="crm_db",
                user="your_db_user",
                password="your_db_password"
            )
            cur = conn.cursor()
            cur.execute(
                "SELECT id, username, password, role FROM users WHERE username = %s", (username,)
            )
            user = cur.fetchone()
            cur.close()
            conn.close()
            if user and check_password_hash(user[2], password):
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['role'] = user[3]
                # redirect based on role 
                if user[3] == 'Admin':
                    return redirect('/admin-dashboard')
                elif user[3] == 'Manager':
                    return redirect('/manager-dashboard')
                elif user[3] == 'Salesperson':
                    return redirect('/sales-dashboard')
                else:
                    return render_template('login.html', error="Invalid credentials")
        except Exception as e:
            return f"An error occurred: {e}"
    return render_template('login.html')  

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'user_id' in session and session['role'] == 'Admin':
        return render_template('admin-dashboard.html')
    return "Access denied. Admins only."
@app.route('/manager-dashboard')
def manager_dashboard():
    if 'user_id' in session and session['role'] == 'Manager':
        return render_template('manager-dashboard.html')
    return "Access denied. Managers only."
@app.route('/sales-dashboard')
def sales_dashboard():
    if 'user_id' not in session or session.get('role') != 'Salesperson':
        return "Access denied. Sales team only."
    user_id = session['user_id']
    conn = psycopg2.connect(
        host="localhost",
        database="crm_db",
        user="your_db_user",
        password="your_db_password"
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, email, phone, status
        FROM leads
        WHERE assigned_to = %s
        ORDER BY id
    """, (user_id,))
    leads = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('sales-dashboard.html', username=session.get('username'), leads=leads)        


@app.route('/admin/users')
def view_users():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="crm_db",
            user="your_db_user",
            password="your_db_password"
        )
        cur = conn.cursor()
        cur.execute("SELECT id, username, email, role FROM users ORDER BY id")
        users = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('view_users.html', users=users)
    except Exception as e:
        return f"Error fetching users: {e}"
@app.route('/admin/add-user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role'].title()
        hashed_password = generate_password_hash(password)

        try:
            conn = psycopg2.connect(
                host="localhost",
                database="crm_db",
                user="your_db_user",
                password="your_db_password"
            )
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)",
                (username, hashed_password, email, role)
            )
            conn.commit()
            cur.close()
            conn.close()
            return redirect('/admin/users')
        except Exception as e:
            return f"An error occurred: {e}"
    return render_template('add_user.html')

@app.route('/admin/users')
def user_list():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="crm_db",
            user="your_db_user",
            password="your_db_password"
        )
        cur = conn.cursor()
        cur.execute("SELECT id, username, email, role FROM users ORDER BY id")
        users = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('user_list.html', users=users)
    except Exception as e:
        return f"Error fetching users: {e}"
@app.route('/admin/edit-user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    conn = psycopg2.connect(
        host="localhost",
        database="crm_db",
        user="your_db_user",
        password="your_db_password"
    )
    cur = conn.cursor()
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']
        cur.execute(
            "UPDATE users SET username=%s, email=%s, role=%s WHERE id=%s",
            (username, email, role, user_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/admin/users')
    else:
        cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return render_template('edit_user.html', user=user)

@app.route('/admin/delete-user/<int:user_id>')
def delete_user(user_id):
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="crm_db",
            user="your_db_user",
            password="your_db_password"
        )
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        return "🗑️ User deleted! <a href='/admin/users'>Back to List</a>"
    except Exception as e:
        return f"Error deleting user: {e}"

@app.route('/admin/leads')
def view_leads():
    conn = psycopg2.connect(
        host="localhost",
        database="crm_db",
        user="your_db_user",
        password="your_db_password"
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT leads.id, leads.name, leads.email, leads.phone, leads.status, users.username
        FROM leads
        LEFT JOIN users ON leads.assigned_to = users.id
        ORDER BY leads.id
    """)
    leads = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('leads.html', leads=leads)
@app.route('/admin/add-lead', methods=['GET', 'POST'])
def add_lead():
    conn = psycopg2.connect(
        host="localhost",
        database="crm_db",
        user="your_db_user",
        password="your_db_password"
    )
    cur = conn.cursor()
    # Get users for the assign dropdown
    cur.execute("SELECT id, username FROM users")
    users = cur.fetchall()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        status = request.form['status']
        assigned_to = request.form['assigned_to'] or None  # Allow unassigned

        cur.execute(
            "INSERT INTO leads (name, email, phone, status, assigned_to) VALUES (%s, %s, %s, %s, %s)",
            (name, email, phone, status, assigned_to)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/admin/leads')
    cur.close()
    conn.close()
    return render_template('add-lead.html', users=users, lead=None)

@app.route('/admin/delete-lead/<int:lead_id>', methods=['POST'])
def delete_lead(lead_id):
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="crm_db",
            user="your_db_user",
            password="your_db_password"
        )
        cur = conn.cursor()
        cur.execute("DELETE FROM leads WHERE id = %s", (lead_id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('view_leads'))
    except Exception as e:
        return f"An error occurred while deleting: {e}"

@app.route('/admin/edit-lead/<int:lead_id>', methods=['GET', 'POST'])
def edit_lead(lead_id):
    conn = psycopg2.connect(
        host="localhost",
        database="crm_db",
        user="your_db_user",
        password="your_db_password"
    )
    cur = conn.cursor()
    # Get users for the assign dropdown
    cur.execute("SELECT id, username FROM users")
    users = cur.fetchall()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        status = request.form['status']
        assigned_to = request.form['assigned_to'] or None
        cur.execute(
            "UPDATE leads SET name=%s, email=%s, phone=%s, status=%s, assigned_to=%s WHERE id=%s",
            (name, email, phone, status, assigned_to, lead_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('view_leads'))
    else:
        cur.execute("SELECT * FROM leads WHERE id=%s", (lead_id,))
        lead = cur.fetchone()
        cur.close()
        conn.close()
        return render_template('add-lead.html', users=users, lead=lead)



# app.py

@app.route('/log-activity/<int:lead_id>', methods=['GET', 'POST'])
def log_activity(lead_id):
    if request.method == 'POST':
        activity_type = request.form['activity_type']
        summary = request.form['summary']
        activity_date = request.form.get('activity_date', datetime.now())
        user_id = session.get('user_id')

        conn = psycopg2.connect(
            host="localhost",
            database="crm_db",
            user="your_db_user",
            password="your_db_password"
        )
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO activities (lead_id, user_id, activity_type, summary, activity_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (lead_id, user_id, activity_type, summary, activity_date))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('view_activity', lead_id=lead_id))

    return render_template('log_activity.html', lead_id=lead_id)

@app.route('/view-activity/<int:lead_id>')
def view_activity(lead_id):
    conn = psycopg2.connect(
        host="localhost",
        database="crm_db",
        user="your_db_user",
        password="your_db_password"
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT a.activity_type, a.summary, a.activity_date, u.username 
        FROM activities a
        LEFT JOIN users u ON a.user_id = u.id
        WHERE a.lead_id = %s
        ORDER BY a.activity_date DESC
    """, (lead_id,))
    activities = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('view_activity.html', activities=activities)

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    role = session.get('role')

    conn = psycopg2.connect(
        host="localhost",
        database="crm_db",
        user="your_db_user",
        password="your_db_password"
    )
    cur = conn.cursor()

    # 1. Count leads by status (your schema uses 'status', not 'stage')
    cur.execute("""
        SELECT status, COUNT(*) 
        FROM leads 
        GROUP BY status
    """)
    lead_data = cur.fetchall()
    stages = [row[0] for row in lead_data]
    counts = [row[1] for row in lead_data]

    cur.close()
    conn.close()

    return render_template('dashboard.html', stages=stages, counts=counts)

@app.route('/sales/leads')
def sales_leads():
    if 'user_id' not in session or session.get('role') != 'Salesperson':
        return "Access denied. Sales team only."
    user_id = session['user_id']
    conn = psycopg2.connect(
        host="localhost",
        database="crm_db",
        user="your_db_user",
        password="your_db_password"
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT leads.id, leads.name, leads.email, leads.phone, leads.status
        FROM leads
        WHERE leads.assigned_to = %s
        ORDER BY leads.id
    """, (user_id,))
    leads = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('sales_leads.html', leads=leads)

@app.route('/sales/update-lead/<int:lead_id>', methods=['GET', 'POST'])
def update_lead_status(lead_id):
    if 'user_id' not in session or session.get('role') != 'Salesperson':
        return "Access denied. Sales team only."
    conn = psycopg2.connect(
        host="localhost",
        database="crm_db",
        user="your_db_user",
        password="your_db_password"
    )
    cur = conn.cursor()
    if request.method == 'POST':
        new_status = request.form['status']
        cur.execute(
            "UPDATE leads SET status=%s WHERE id=%s AND assigned_to=%s",
            (new_status, lead_id, session['user_id'])
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/sales-dashboard')
    else:
        cur.execute("SELECT id, name, status FROM leads WHERE id=%s AND assigned_to=%s", (lead_id, session['user_id']))
        lead = cur.fetchone()
        cur.close()
        conn.close()
        if not lead:
            return "Lead not found or not assigned to you."
        return render_template('update-lead.html', lead=lead)

@app.route('/sales/log-activity/<int:lead_id>', methods=['GET', 'POST'])
def log_activity_sales(lead_id):
    if 'user_id' not in session or session.get('role') != 'Salesperson':
        return "Access denied. Sales team only."
    if request.method == 'POST':
        activity_type = request.form['activity_type']
        summary = request.form['summary']
        activity_date = request.form.get('activity_date') or datetime.now()
        user_id = session['user_id']

        conn = psycopg2.connect(
            host="localhost",
            database="crm_db",
            user="your_db_user",
            password="your_db_password"
        )
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO activities (lead_id, user_id, activity_type, summary, activity_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (lead_id, user_id, activity_type, summary, activity_date))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/sales/leads')
    return render_template('log_activity.html', lead_id=lead_id)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)





