from flask import render_template, request, session, redirect, url_for, flash, g, current_app
import random as r
import requests
import sqlite3
from datetime import datetime


def get_db():
    """Get database connection"""
    if "db" not in g:
        conn = sqlite3.connect(current_app.config["DATABASE"])
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


def init_quiz_db():
    """Initialize quiz results table"""
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            percentage REAL NOT NULL,
            grade TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    db.commit()


def save_quiz_result(user_id, score, total_questions, percentage, grade):
    """Save quiz result to database"""
    db = get_db()
    db.execute(
        """
        INSERT INTO quiz_results (user_id, score, total_questions, percentage, grade)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, score, total_questions, percentage, grade)
    )
    db.commit()


def get_user_quiz_history(user_id):
    """Get quiz history for user"""
    db = get_db()
    results = db.execute(
        """
        SELECT * FROM quiz_results 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 10
        """,
        (user_id,)
    ).fetchall()
    return results


def init_quiz(app):
    # Initialize database table on app startup
    with app.app_context():
        init_quiz_db()

    @app.route("/quiz", methods=["GET", "POST"])
    def quiz_home():
        # Check if user is logged in
        if not session.get("user_id"):
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))

        if request.method == "POST":

            no_ques = request.form.get("no_ques")
            category = request.form.get("category")
            diff = request.form.get("diff")
            q_type = request.form.get("type")

            question = requests.get(
                f"https://opentdb.com/api.php?amount={no_ques}&category={category}&difficulty={diff}&type={q_type}"
            )

            session["questions"] = question.json()
            session["score"] = 0
            session["current_question"] = 0

            return redirect(url_for("quiz"))

        # Get user's quiz history
        user_id = session.get("user_id")
        history = get_user_quiz_history(user_id)

        return render_template("quiz_home.html", history=history)

    @app.route("/quiz/play", methods=["GET", "POST"])
    def quiz():
        # Check if user is logged in
        if not session.get("user_id"):
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))

        if "questions" not in session:
            return redirect(url_for("quiz_home"))

        question_no = len(session["questions"]["results"])

        # ---------- User submitted answer ----------
        if request.method == "POST":

            current = session["questions"]["results"][session["current_question"]]

            answer = request.form.get("answer")

            if answer == current["correct_answer"]:
                session["score"] += 1

            session["current_question"] += 1

            if session["current_question"] >= question_no:
                return redirect(url_for("result"))

            return redirect(url_for("quiz"))

        # ---------- Show Question ----------

        current = session["questions"]["results"][session["current_question"]]

        question = current["question"]

        options = current["incorrect_answers"].copy()
        options.append(current["correct_answer"])
        r.shuffle(options)

        progress = (session["current_question"] / question_no) * 100

        return render_template(
            "quiz.html",
            question=question,
            options=options,
            progress=progress,
            current=session["current_question"] + 1,
            total=question_no,
        )

    @app.route("/result")
    def result():
        # Check if user is logged in
        if not session.get("user_id"):
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))

        if "questions" not in session:
            return redirect(url_for("quiz_home"))

        score = session["score"]
        total_questions = len(session["questions"]["results"])
        per = (score / total_questions) * 100

        if 90 <= per <= 100:
            grade = "A"
            comment = "Well Done Hero !!"
        elif 80 <= per < 90:
            grade = "B"
            comment = "Keep Going !!"
        elif 70 <= per < 80:
            grade = "C"
            comment = "Can Do Better !!"
        elif 60 <= per < 70:
            grade = "D"
            comment = "Not Bad !!"
        elif 50 <= per < 60:
            grade = "E"
            comment = "Need To Work Hard !!"
        else:
            grade = "F"
            comment = "Not Quite Good, But You Can Do Better !!"

        # Save quiz result to database
        user_id = session.get("user_id")
        save_quiz_result(user_id, score, total_questions, per, grade)

        return render_template(
            "result.html",
            score=score,
            per=per,
            grade=grade,
            comment=comment,
        )