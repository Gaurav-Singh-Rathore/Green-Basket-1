from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
import os


app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session management

DATABASE = "greenbasket.db"

# Function to get the database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Access rows as dictionaries
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialize the database
def init_db():
    with app.app_context():
        db = get_db()
        with open("schema.sql", "r") as f:
            db.executescript(f.read())
        db.commit()

# Route for homepage (renders index.html)
@app.route("/")
def home():
    return render_template("index.html")

@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/why')
def why():
    return render_template('why.html')

@app.route('/store')
def store():
    return render_template('store.html')

# Route for user registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        db.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
        db.commit()
        return redirect(url_for("login"))  # ✅ Fix: Redirect correctly
    
    return render_template("register.html")  # ✅ Fix: Render the correct template

# Route for user login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password)).fetchone()

        if user:
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard"))  # ✅ Redirect correctly
        else:
            return "Invalid Credentials!", 401  # Return HTTP 401 Unauthorized
    
    return render_template("login.html")  # ✅ Fix: Render login.html

# User dashboard (protected route)
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))  # ✅ Fix: Redirect correctly

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    return f"Welcome {user['username']}! <a href='/logout'>Logout</a>"

# Route for logout
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("home"))

# Route to list all products
@app.route("/products")
def products():
    db = get_db()
    products = db.execute("SELECT * FROM products").fetchall()
    return {"products": [dict(p) for p in products]}  # Returns JSON

# Route to add a new product (for admins)
@app.route("/add_product", methods=["POST"])
def add_product():
    name = request.form["name"]
    price = float(request.form["price"])
    stock = int(request.form["stock"])

    db = get_db()
    db.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
    db.commit()
    return redirect(url_for("products"))

# Route to display stores
@app.route("/stores")
def stores():
    db = get_db()
    stores = db.execute("SELECT * FROM stores").fetchall()
    return {"stores": [dict(s) for s in stores]}  # Returns JSON

@app.route("/contact")
def contact():
    return render_template("contact.html")  # Ensure contact.html exists

if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        init_db()  # ✅ Fix: Ensure database is initialized
    app.run(debug=True)
