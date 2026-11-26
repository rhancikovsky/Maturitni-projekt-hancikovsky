
from flask import Flask, render_template, request, redirect, url_for, session
import subprocess
import sys
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "zmen-tento-klic-na-vlastni-nahodny-retezec"

DB_PATH = Path(__file__).parent / "database" / "game.db"


def get_database_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


@app.route("/")
def index():
    connection = get_database_connection()

    scores = connection.execute(
        """
        SELECT users.username, scores.score, scores.played_at
        FROM scores
        JOIN users ON scores.user_id = users.id
        ORDER BY scores.score DESC
        """
    ).fetchall()

    connection.close()

    return render_template("index.html", scores=scores)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            error = "Vyplň uživatelské jméno i heslo."
        elif len(username) > 30:
            error = "Uživatelské jméno může mít maximálně 30 znaků."
        elif len(password) < 8:
            error = "Heslo musí mít alespoň 8 znaků."
        else:
            password_hash = generate_password_hash(password)
            connection = get_database_connection()

            try:
                connection.execute(
                    """
                    INSERT INTO users (username, password_hash)
                    VALUES (?, ?)
                    """,
                    (username, password_hash),
                )
                connection.commit()
                connection.close()
                return redirect(url_for("login"))

            except sqlite3.IntegrityError:
                connection.close()
                error = "Toto uživatelské jméno už existuje."

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        connection = get_database_connection()

        user = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        connection.close()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))

        error = "Nesprávné uživatelské jméno nebo heslo."

    return render_template("login.html", error=error)

@app.route("/play")
def play():
    if "user_id" not in session:
        return redirect(url_for("login"))

    subprocess.Popen([
        sys.executable,
        str(Path(__file__).parent / "main.py"),
        str(session["user_id"])
    ])

    return redirect(url_for("index"))
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
