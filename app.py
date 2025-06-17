from flask import Flask, render_template, request, url_for, session, redirect
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
                else:
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
    if 'user_id' in session and session['role'] == 'Sales':
        return "Welcome to the Sales Dashboard!"
    return "Access denied. Sales team only."        


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

            


if __name__ == "__main__":
    app.run(debug=True)





