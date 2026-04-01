from flask import Flask, render_template, request, redirect, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

DATABASE = "database.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )
    ''')

    cursor.execute("DELETE FROM users")

    cursor.execute("INSERT INTO users (username, password, role) VALUES ('user','1234','user')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin','admin123','admin')")

    db.commit()
    db.close()

@app.route('/')
def home():
    db = get_db()
    users = db.execute("SELECT * FROM users").fetchall()
    return render_template("home.html", users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            return redirect('/')
        else:
            return "Invalid credentials"

    return render_template("login.html")

@app.route('/profile/<int:user_id>')
def profile(user_id):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    return render_template("profile.html", user=user)

@app.route('/hidden-admin-123')
def admin():
    db = get_db()
    users = db.execute("SELECT * FROM users").fetchall()
    return render_template("admin.html", users=users)

@app.route('/delete/<int:user_id>')
def delete_user(user_id):
    db = get_db()
    db.execute("DELETE FROM users WHERE id=?", (user_id,))
    db.commit()
    return redirect('/hidden-admin-123')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
