from flask import Flask, render_template, request, session, redirect, url_for, flash, g, current_app
import secrets
import string
import sqlite3
from datetime import datetime

# Character pools
keys = string.ascii_letters + string.digits + string.punctuation

# Pronounceable syllables
syllables = [
    "ba", "be", "bi", "bo", "bu",
    "ka", "ke", "ki", "ko", "ku",
    "la", "le", "li", "lo", "lu",
    "ma", "me", "mi", "mo", "mu",
    "na", "ne", "ni", "no", "nu",
    "pa", "pe", "pi", "po", "pu",
    "ra", "re", "ri", "ro", "ru",
    "sa", "se", "si", "so", "su",
    "ta", "te", "ti", "to", "tu"
]


def get_db():
    """Get database connection"""
    if "db" not in g:
        conn = sqlite3.connect(current_app.config["DATABASE"])
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


def init_password_db():
    """Create password history table"""
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS password_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    db.commit()


def get_user_history(user_id):
    """Get password history for specific user (last 20)"""
    db = get_db()
    history = db.execute(
        """
        SELECT password, strftime('%d %b %Y, %I:%M %p', created_at) as timestamp
        FROM password_history 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 20
        """,
        (user_id,)
    ).fetchall()
    return [dict(h) for h in history]


def add_to_history(user_id, password):
    """Add password to user's history"""
    db = get_db()
    db.execute(
        """
        INSERT INTO password_history (user_id, password) 
        VALUES (?, ?)
        """,
        (user_id, password)
    )
    db.commit()


def generate_random_password():
    password = ""

    password += secrets.choice(string.ascii_uppercase)
    password += secrets.choice(string.ascii_lowercase)
    password += secrets.choice(string.digits)
    password += secrets.choice(string.punctuation)

    length = secrets.randbelow(9) + 8

    while len(password) < length:
        password += secrets.choice(keys)

    password = list(password)
    secrets.SystemRandom().shuffle(password)

    return "".join(password)


def generate_pronounceable_password():
    word = ""

    for _ in range(4):
        word += secrets.choice(syllables)

    word = word.capitalize()
    word += secrets.choice(string.digits)
    word += secrets.choice(string.digits)
    word += secrets.choice("@#$%&!?")

    return word


def password_strength(password):

    score = 0

    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1

    if any(c.isupper() for c in password):
        score += 1

    if any(c.islower() for c in password):
        score += 1

    if any(c.isdigit() for c in password):
        score += 1

    if any(c in string.punctuation for c in password):
        score += 1

    if score >= 5:
        rating = "Very Strong 💪"
    elif score == 4:
        rating = "Strong ✅"
    elif score == 3:
        rating = "Moderate ⚠️"
    else:
        rating = "Weak ❌"

    return score, rating


def init_password(app):
    # Initialize database on app startup
    with app.app_context():
        init_password_db()

    @app.route("/password", methods=["GET", "POST"])
    def password():
        # Check if user is logged in
        if not session.get("user_id"):
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))

        user_id = session.get("user_id")
        password_history = get_user_history(user_id)

        if request.method == "POST":

            pronounceable = request.form.get("pronounceable")

            if pronounceable:
                generated_password = generate_pronounceable_password()
            else:
                generated_password = generate_random_password()

            # Save to user's history
            add_to_history(user_id, generated_password)
            password_history = get_user_history(user_id)

            score, rating = password_strength(generated_password)

            return render_template(
                "password.html",
                generated_password=generated_password,
                rating=rating,
                score=score,
                password_history=password_history,
            )

        return render_template(
            "password.html",
            generated_password=None,
            rating=None,
            score=0,
            password_history=password_history,
        )