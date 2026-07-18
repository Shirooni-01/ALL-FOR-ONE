from flask import Flask, render_template, request, session, redirect, url_for, flash
import secrets
import string
import json
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

PASSWORD_HISTORY_FILE = "password_history.json"


def load_all_history():
    """Load all password history from JSON"""
    try:
        with open(PASSWORD_HISTORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_all_history(all_history):
    """Save all password history to JSON"""
    with open(PASSWORD_HISTORY_FILE, "w") as f:
        json.dump(all_history, f, indent=4)


def get_user_history(user_id):
    """Get password history for specific user"""
    all_history = load_all_history()
    user_history = [p for p in all_history if p.get("user_id") == user_id]
    return user_history[:20]  # Return last 20


def add_to_history(user_id, password):
    """Add password to user's history"""
    all_history = load_all_history()
    all_history.insert(0, {
        "user_id": user_id,
        "password": password,
        "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p")
    })
    save_all_history(all_history)


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