import os
import bcrypt
import pymysql
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session
load_dotenv() 

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,
    )


@app.route("/")
def home():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS n FROM users")
        row = cur.fetchone()
    db.close()
    return f"Connected! Users in DB: {row['n']}"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm_password", "")

    errors = []
    if not name:
        errors.append("Name is required")
    if not email:
        errors.append("Email is required")
    if not password:
        errors.append("Password is required")
    if not confirm:
        errors.append("Confirm password is required")
    if password and confirm and password != confirm:
        errors.append("Passwords do not match")

    if errors:
        return render_template("register.html", errors=errors, name=name, email=email)

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s)",
                (email, name, hashed),
            )
            user_id = cur.lastrowid
        db.commit()
    except pymysql.err.IntegrityError:
        return render_template("register.html", errors=["Email Already Exists"],
                               name=name, email=email)
    finally:
        db.close()

    session["user_id"] = user_id
    session["name"] = name
    return redirect("/todos")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    errors = []
    if not email:
        errors.append("Email is required")
    if not password:
        errors.append("Password is required")
    if errors:
        return render_template("login.html", errors=errors, email=email)

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT user_id, name, password_hash FROM users WHERE email = %s",
                (email,),
            )
            user = cur.fetchone()
    finally:
        db.close()

    if user is None or not bcrypt.checkpw(
        password.encode("utf-8"), user["password_hash"].encode("utf-8")
    ):
        return render_template("login.html", errors=["Invalid email or password"],
                               email=email)

    session["user_id"] = user["user_id"]
    session["name"] = user["name"]
    return redirect("/todos")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


def validate_title(title):
    if not title.strip():
        return "Title is required"
    if len(title) > 200:
        return "Title is too long (200 characters at most)"
    return None


def show_list(errors=None, new_title=None):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT todo_id, title, is_done, created_at FROM todos "
                "WHERE user_id = %s ORDER BY todo_id DESC",
                (session["user_id"],),
            )
            items = cur.fetchall()
    finally:
        db.close()
    return render_template("todos.html", name=session["name"], todos=items,
                           errors=errors, new_title=new_title)


@app.route("/todos")
def todos():
    if "user_id" not in session:
        return redirect("/login")
    return show_list()


@app.route("/todos/add", methods=["POST"])
def add_todo():
    if "user_id" not in session:
        return redirect("/login")
    title = request.form.get("title", "").strip()
    error = validate_title(title)
    if error:
        return show_list(errors=[error], new_title=title)

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("INSERT INTO todos (user_id, title) VALUES (%s, %s)",
                        (session["user_id"], title))
        db.commit()
    finally:
        db.close()
    return redirect("/todos")


@app.route("/todos/<int:todo_id>/edit", methods=["POST"])
def edit_todo(todo_id):
    if "user_id" not in session:
        return redirect("/login")
    title = request.form.get("title", "").strip()
    error = validate_title(title)
    if error:
        return show_list(errors=[error])

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("UPDATE todos SET title = %s WHERE todo_id = %s AND user_id = %s",
                        (title, todo_id, session["user_id"]))
        db.commit()
    finally:
        db.close()
    return redirect("/todos")


@app.route("/todos/<int:todo_id>/toggle", methods=["POST"])
def toggle_todo(todo_id):
    if "user_id" not in session:
        return redirect("/login")
    is_done = 1 if request.form.get("is_done") == "1" else 0

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("UPDATE todos SET is_done = %s WHERE todo_id = %s AND user_id = %s",
                        (is_done, todo_id, session["user_id"]))
        db.commit()
    finally:
        db.close()
    return redirect("/todos")


@app.route("/todos/<int:todo_id>/delete", methods=["POST"])
def delete_todo(todo_id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("DELETE FROM todos WHERE todo_id = %s AND user_id = %s",
                        (todo_id, session["user_id"]))
        db.commit()
    finally:
        db.close()
    return redirect("/todos")

if __name__ == "__main__":
    app.run(debug=True)