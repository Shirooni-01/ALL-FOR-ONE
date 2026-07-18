from flask import render_template, request, session, redirect, url_for, flash, g, current_app
from datetime import datetime
import sqlite3


def get_db():
    """Get database connection"""
    if "db" not in g:
        conn = sqlite3.connect(current_app.config["DATABASE"])
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


def init_notes_db():
    """Create notes table if it doesn't exist"""
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            note TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    db.commit()


def get_user_notes(user_id):
    """Get all notes for a specific user"""
    db = get_db()
    notes = db.execute(
        """
        SELECT id, title, note, 
               strftime('%d %b %Y, %I:%M %p', updated_at) as time
        FROM notes 
        WHERE user_id = ? 
        ORDER BY updated_at DESC
        """,
        (user_id,)
    ).fetchall()
    return [dict(note) for note in notes]


def add_note(user_id, title, note_text):
    """Add a new note"""
    db = get_db()
    db.execute(
        """
        INSERT INTO notes (user_id, title, note) 
        VALUES (?, ?, ?)
        """,
        (user_id, title, note_text)
    )
    db.commit()


def update_note(user_id, note_id, title=None, note_text=None):
    """Update a note"""
    db = get_db()
    
    # Verify note belongs to user
    note = db.execute(
        "SELECT id FROM notes WHERE id = ? AND user_id = ?",
        (note_id, user_id)
    ).fetchone()
    
    if not note:
        return False
    
    if title:
        db.execute(
            "UPDATE notes SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (title, note_id)
        )
    if note_text:
        db.execute(
            "UPDATE notes SET note = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (note_text, note_id)
        )
    
    db.commit()
    return True


def delete_note(user_id, note_id):
    """Delete a note"""
    db = get_db()
    
    # Verify note belongs to user before deleting
    note = db.execute(
        "SELECT id FROM notes WHERE id = ? AND user_id = ?",
        (note_id, user_id)
    ).fetchone()
    
    if not note:
        return False
    
    db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    db.commit()
    return True


def init_notes(app):
    # Initialize database on app startup
    with app.app_context():
        init_notes_db()

    @app.route("/notes", methods=["GET", "POST"])
    def notes_page():
        # Check if user is logged in
        if not session.get("user_id"):
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))

        user_id = session.get("user_id")
        notes = get_user_notes(user_id)

        if request.method == "POST":
            title = request.form.get("title")
            note_text = request.form.get("note")
            note_id = request.form.get("index")
            note_id_del = request.form.get("index_del")
            editednote = request.form.get("editednote")
            editedtitle = request.form.get("editedtitle")
            search = request.form.get("search")

            searchednote = None

            # Add new note
            if title and note_text:
                add_note(user_id, title, note_text)
                notes = get_user_notes(user_id)

            # Update note
            if note_id is not None and (editednote or editedtitle):
                update_note(user_id, int(note_id), editedtitle, editednote)
                notes = get_user_notes(user_id)

            # Delete note
            if note_id_del is not None and request.form.get("delete") == "Delete":
                delete_note(user_id, int(note_id_del))
                notes = get_user_notes(user_id)

            # Search notes
            if search:
                for note in notes:
                    if search.lower().strip() == note["title"].lower().strip():
                        searchednote = note
                        break

            return render_template(
                "notes.html",
                notes=notes,
                searchednote=searchednote,
            )

        return render_template(
            "notes.html",
            notes=notes,
        )