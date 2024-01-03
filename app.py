from flask import Flask, redirect, render_template, request, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

# SQLite database setup
import sqlite3

con = sqlite3.connect("zoo.db", check_same_thread=False)
cur = con.cursor()

try:
    cur.execute("CREATE TABLE users(username, password)")
except:
    pass

try:
  cur.execute("CREATE TABLE animals(name, type, age, Picture)")
except:
    pass

# Decorator to check if the user is logged in
def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            flash('Login required', 'error')
            return redirect(url_for('login'))
        return route_function(*args, **kwargs)
    return wrapper

# Routes for your application

@app.route('/')
@login_required
def home():
    cur.execute("SELECT rowid, * FROM animals")
    animals = cur.fetchall()
    return render_template("home.html", animals=animals)

@app.route('/add_animal', methods=['GET', 'POST'])
@login_required
def add_animal():
    if request.method == 'POST':
        name = request.form['name']
        animal_type = request.form['type']
        age = request.form['age']
        Picture = request.form['Picture']
        cur.execute("INSERT INTO animals (name, type, age,Picture) VALUES (?, ?, ?,?)", (name, animal_type, age, Picture))
        con.commit()
        return redirect(url_for('home'))
    return render_template("add_animal.html")

@app.route('/animals_list')
@login_required
def animals_list():
    cur.execute("SELECT rowid, * FROM animals")
    animals = cur.fetchall()
    return render_template("animals_list.html", animals=animals)

@app.route('/update_animal/<int:animal_id>', methods=['GET', 'POST'])
@login_required
def update_animal(animal_id):
    if request.method == 'POST':
        name = request.form['name']
        animal_type = request.form['type']
        age = request.form['age']
        Picture = request.form['Picture']
        cur.execute("UPDATE animals SET name=?, type=?, age=?,Picture=? WHERE rowid=?", (name, animal_type, age,Picture, animal_id))
        con.commit()
        return redirect(url_for('animals_list'))

    cur.execute("SELECT rowid, * FROM animals WHERE rowid=?", (animal_id,))
    animal = cur.fetchone()
    return render_template("update_animal.html", animal=animal)

@app.route('/delete_animal/<int:animal_id>', methods=['POST'])
@login_required
def delete_animal(animal_id):
    cur.execute("DELETE FROM animals WHERE rowid=?", (animal_id,))
    con.commit()
    return redirect(url_for('animals_list'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username exists in the database
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()

        if user and check_password_hash(user[1], password):
            session['username'] = username
            flash('Login successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password)

        # Check if the username is already taken
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            flash('Username already taken. Please choose a different one.', 'error')
        else:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            con.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
