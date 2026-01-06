from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "mysecretkey123"

ADMIN_PASSWORD = "Sai@000"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "flames.db")

# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_db() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name1 TEXT,
            name2 TEXT,
            result TEXT,
            color TEXT,
            emoji TEXT,
            created_at TEXT
        )
        """)
init_db()

# ---------- FLAMES LOGIC ----------
def calculate_flames(name1, name2):
    name1 = name1.replace(" ", "").lower()
    name2 = name2.replace(" ", "").lower()

    list1 = list(name1)
    list2 = list(name2)

    for ch in list1[:]:
        if ch in list2:
            list1.remove(ch)
            list2.remove(ch)

    count = len(list1) + len(list2)

    flames = ['F', 'L', 'A', 'M', 'E', 'S']
    while len(flames) > 1:
        index = (count - 1) % len(flames)
        flames.pop(index)

    flames_meaning = {
        'F': ('Friends', '#3498db', '🤝'),
        'L': ('Love', '#e74c3c', '❤️'),
        'A': ('Affection', '#f39c12', '💛'),
        'M': ('Marriage', '#9b59b6', '💍'),
        'E': ('Enemy', '#2c3e50', '😈'),
        'S': ('Siblings', '#1abc9c', '👫')
    }

    text, color, emoji = flames_meaning[flames[0]]
    return {'text': text, 'color': color, 'emoji': emoji}

# ---------- ROUTES ----------
@app.route("/", methods=["GET", "POST", "HEAD"])
def index():
    result = None
    if request.method == "POST":
        name1 = request.form.get("name1")
        name2 = request.form.get("name2")

        if name1 and name2:
            result = calculate_flames(name1, name2)
            with get_db() as con:
                con.execute("""
                INSERT INTO submissions
                (name1, name2, result, color, emoji, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    name1,
                    name2,
                    result["text"],
                    result["color"],
                    result["emoji"],
                    datetime.now().strftime("%d-%m-%Y %I:%M %p")
                ))

    return render_template("index.html", result=result)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin"))

    if not session.get("admin"):
        return render_template("admin_login.html")

    with get_db() as con:
        rows = con.execute("""
        SELECT name1, name2, result, color, emoji
        FROM submissions
        ORDER BY id DESC
        """).fetchall()

    submissions = [(n1, n2, {"text": r, "color": c, "emoji": e})
                   for n1, n2, r, c, e in rows]

    return render_template("admin.html", submissions=submissions)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
