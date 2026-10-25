import os
import sqlite3

from flask import Flask, g, redirect, render_template, request

app = Flask(__name__)
app.config["DATABASE"] = os.environ.get("DATABASE", "notes.db")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        get_db().execute(
            "CREATE TABLE IF NOT EXISTS notes ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, content TEXT NOT NULL)"
        )
        get_db().commit()


@app.route("/healthz")
def healthz():
    return {"status": "ok"}


@app.route("/")
def index():
    q = request.args.get("q", "")
    # Parameterized query: user input never becomes SQL code
    notes = get_db().execute(
        "SELECT id, title, content FROM notes WHERE title LIKE ? ORDER BY id DESC",
        (f"%{q}%",),
    ).fetchall()
    # render_template auto-escapes .html templates: user input never becomes HTML code
    #introudce XSS vulnerability for demo purpose
    highlight = f"<mark>{q}</mark>" if q else ""
    return render_template("index.html", notes=notes, q=q, highlight=highlight)


@app.route("/notes", methods=["POST"])
def create_note():
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    if not title or not content:
        return "Title and content are required", 400
    db = get_db()
    db.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
    db.commit()
    return redirect("/")


if __name__ == "__main__":
    init_db()
    # Debug off; listen on 127.0.0.1 unless APP_HOST is set (the container sets 0.0.0.0)
    app.run(host=os.environ.get("APP_HOST", "127.0.0.1"), port=5000)
