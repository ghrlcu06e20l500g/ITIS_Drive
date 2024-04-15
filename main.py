from flask import *
from werkzeug.utils import secure_filename

import query
import os
import io
import json


def user_directory() -> str:
    return os.path.join(os.getcwd(), "storage", session["user"]["username"])
def get_user_files() -> list:
    files = []
    user_dir = user_directory()
    for filename in os.listdir(user_dir):
        file_path = os.path.join(user_dir, filename)
        if os.path.isfile(file_path):
            with open(file_path, "rb") as file:
                files.append({
                    "name": os.path.basename(file_path),
                    "content": file.read()
                })
    return files
def get_articles() -> list[dict]:
    articles = []
    for filename in os.listdir("articles"):
        if filename.endswith(".json"):
            with open(os.path.join("articles", filename), "r") as file:
                articles.append(json.load(file))
    return articles

class App(Flask):
    class Settings():
        def __init__(self, app):
            app.add_url_rule("/settings", view_func = self.settings)
            app.add_url_rule("/settings/update_username", view_func = self.update_username, methods = ["POST"])
            app.add_url_rule("/settings/update_password", view_func = self.update_password, methods = ["POST"])
            self.message = None
        def settings(self):
            return render_template("settings.html",
                user = session.get("user"), 
                articles = get_articles(),
                message = self.message
            )
        def update_username(self):
            old_name: str = session.get("user")["username"]
            new_name: str = request.form["username"]

            if old_name == new_name:
                self.message = { "type": "info", "text": "That's already your username. :D"}
                return redirect(url_for("settings"))
            if query.run(f"SELECT * FROM users WHERE username = '{old_name}'", query.Mode.FETCH_ONE):
                self.message = { "type": "danger", "text": "User already exists. D:"}
                return redirect(url_for("settings"))

            session["user"] = {"username": new_name, "password": session.get("user")["password"]} 
            query.run(f"UPDATE users SET username = '{new_name}' WHERE username = '{old_name}'")
            self.message = { "type": "info", "text": "Username updated. :D"}
            return redirect(url_for("settings"))
        def update_password(self):
            name: str = session.get("user")["username"]
            password: str = request.form["password"]

            if session.get("user")["password"] == password:
                self.message = { "type": "info", "text": "That's already your password. ;D"}
                return redirect(url_for("settings")) 

            session["user"] = {"username": session.get("user")["username"], "password": password} 
            query.run(f"UPDATE users SET password = '{password}' WHERE username = '{name}'")
            self.message = { "type": "info", "text": "Password updated. :D"}
            return redirect(url_for("settings")) 
    class Login():
        def __init__(self, app):
            app.add_url_rule("/login", view_func = self.login)
            app.add_url_rule("/login/send_credentials", view_func = self.send_credentials, methods = ["POST"])
        def login(self):
            return render_template("login.html", user = None, articles = get_articles())
        def send_credentials(self): 
            username = request.form['username']
            password = request.form['password']
            user = query.run(f"SELECT * FROM users WHERE username='{username}'", query.Mode.FETCH_ONE)
            
            if user is not None:
                if user["password"] == password:
                    session["user"] = {"username": user["username"], "password": password} 
                    return redirect(url_for("home"))
                else:
                    return render_template("login.html", message = "Wrong password. D:", articles = get_articles())
            else:
                query.run(f"INSERT INTO users(username, password) VALUES(\"{username}\", \"{password}\")")
                session["user"] = {"username": username, "password": password}
                
                if not os.path.exists(user_directory()):
                    os.makedirs(user_directory())
                
                return redirect(url_for("home"))
    class Drive():
        def __init__(self, app):
            app.add_url_rule("/drive", view_func = self.drive)
            app.add_url_rule("/drive/upload_file", view_func = self.upload_file, methods = ["POST"])
            app.add_url_rule("/drive/delete_file/<string:filename>", view_func = self.delete_file)
            app.add_url_rule("/drive/download_file/<string:filename>", view_func = self.download_file)
        def drive(self):
            return render_template("drive.html",
                user = session.get("user"), 
                articles = get_articles(),
                files = get_user_files()
            )
        def upload_file(self):
            if "file" not in request.files:
                flash("No file part")
                return redirect(url_for("drive"))
            file = request.files["file"]
            if file.filename == "":
                flash("No selected file")
            if file:
                file.save(os.path.join(user_directory(), file.filename))
            
            return redirect(url_for("drive"))
        def delete_file(self, filename: str):
            filepath: str = os.path.join(user_directory(), filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            return redirect(url_for("drive"))
        def download_file(self, filename: str):
            filepath: str = os.path.join(user_directory(), filename)
            if os.path.exists(filepath):
                return send_file(filepath, as_attachment=True)
            return redirect(url_for("drive"))
    class News():
        def __init__(self, app):
            app.add_url_rule("/news", view_func = self.news)
        def news(self):
            return render_template("news.html",
                user = session.get("user"), 
                articles = get_articles()
            )
    def __init__(self):
        super().__init__(__name__)
        self.secret_key = "A_SUPER_SECRET_KEY"
        
        self.add_url_rule("/", view_func = self.index)
        self.add_url_rule("/home", view_func = self.home)
        self.add_url_rule("/logout", view_func = self.logout)
        App.Settings(self)
        App.Login(self)
        App.Drive(self)
        App.News(self)

        self.run(debug=True)
    def index(self):
        return redirect(url_for("home"))
    def home(self):
        return render_template("home.html",
            user = session.get("user"), 
            articles = get_articles()
        )
    def logout(self):
        session.clear()
        return redirect(url_for("home"))

if __name__ == "__main__":
    App()
