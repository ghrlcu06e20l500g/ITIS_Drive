from flask import *
from werkzeug.utils import secure_filename

import query
import os
import io


def user_directory() -> str:
    return os.path.join(os.getcwd(), "storage", session["user"]["username"])
def get_user_files() -> list:
    files = []
    user_dir = user_directory()
    for filename in os.listdir(user_dir):
        file_path = os.path.join(user_dir, filename)
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                files.append({
                    "name": os.path.basename(file_path),
                    "content": file.read()
                })
    return files
def get_articles() -> list[str]:
    articles = []
    for filename in reversed(os.listdir("articles")):
        if filename.endswith(".html"):
            with open(os.path.join("articles", filename), "r", encoding="utf-8") as file:
                articles.append(file.read())
    return articles

class App(Flask):
    class Settings():
        def __init__(self, app):
            app.add_url_rule("/settings", view_func = self.settings)
            app.add_url_rule("/settings/update_username", view_func = self.update_username, methods = ["POST"])
            app.add_url_rule("/settings/update_password", view_func = self.update_password, methods = ["POST"])
        def settings(self):
            return render_template("settings.html",
                user = session.get("user"), 
                articles = get_articles()
            )
        def update_username(self):
            return redirect(url_for("settings"))
        def update_password(self):
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
