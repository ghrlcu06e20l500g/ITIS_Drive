from flask import *
import sqlite3
import string
import random

app = Flask(__name__)
app.secret_key = "thisisasupersecretvalue"

@app.route("/")
def index():
    return redirect(url_for("home"))

@app.route("/home")
def home():
    return render_template("home.html", user = session.get("user"))

@app.route("/login")
def login():
    return render_template("login.html", message = None)
@app.route("/login_post", methods=["POST"])
def login_post():
    username = request.form['username']
    password = request.form['password']

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.row_factory = sqlite3.Row

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if user is not None:
        if user["password"] == password:
            session["user"] = {"username": user["username"]}
            return redirect(url_for("home"))
        else:
            return render_template("login.html", message = "Wrong password.")
    else:
        cursor.execute("INSERT INTO users(username, password) VALUES(?, ?)", (username, password, ))
        connection.commit()
        session["user"] = {"username": username} 
        return redirect(url_for("home"))

@app.route("/settings")
def settings():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    return render_template("settings.html", user = user)
@app.route("/delete_account_post", methods=["POST"])
def delete_account_post():
    
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.row_factory = sqlite3.Row
    cursor.execute("DELETE FROM users WHERE username=?", (session.get("user")["username"],))
    connection.commit()

    session.pop("user", None)
    return redirect(url_for("home"))

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
