from flask import *
import sqlite3

settings_blueprint = Blueprint("settings_blueprint", __name__)


@settings_blueprint.route("/settings")
def settings():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    return render_template("settings.html", user = user, message = None, message_type = None)

@settings_blueprint.route("/settings/update_username", methods=["POST"])
def update_username():
    username = request.form["username"]

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.row_factory = sqlite3.Row

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if not username:
        return render_template("settings.html",
            message = "You can't call youself that. D:",
            message_type = "danger"
        )
    elif username == session["user"]["username"]:
        return render_template("settings.html", 
            message = "That's already your username. :D", 
            message_type = "info"
        )
    elif user is not None:
        return render_template("settings.html",
            message = "User already exists. D:",
            message_type = "danger"
        )
    else:
        cursor.execute("UPDATE users SET username = ? WHERE username = ?", (username, session["user"]["username"]))
        connection.commit()
        session["user"] = {
            "username": username, 
            "password": session["user"]["password"]
        }

        return render_template("settings.html",
            message = "Username updated. :D",
            message_type = "info"
        )

@settings_blueprint.route("/settings/update_password", methods=["POST"])
def update_password():
    password = request.form["password"]

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.row_factory = sqlite3.Row

    if not password:
        return render_template("settings.html",
            message = "You can't have your password be that. D:",
            message_type = "danger"
        )
    elif password == session["user"]["password"]:
        return render_template("settings.html", 
            message = "That's already your password. ;D", 
            message_type = "info"
        )
    else:
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (password, session["user"]["username"]))
        connection.commit()
        session["user"] = {
            "username": session["user"]["username"], 
            "password": password
        }

        return render_template("settings.html",
            message = "Password updated. :D",
            message_type = "info"
        )

@settings_blueprint.route("/settings/delete_account_post")
def delete_account_post():
    
    
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.row_factory = sqlite3.Row
    cursor.execute("DELETE FROM users WHERE username=?", (session["user"]["username"],))
    connection.commit()

    session.pop("user", None)
    return redirect(url_for("home"))
