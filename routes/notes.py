from flask import render_template, request, session, redirect, url_for, flash
from datetime import datetime
import json
import os

# Load all notes from JSON
def load_all_notes():
    try:
        with open("notes.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_all_notes(all_notes):
    with open("notes.json", "w") as f:
        json.dump(all_notes, f, indent=4)


def get_user_notes(user_id):
    """Get only notes belonging to a specific user"""
    all_notes = load_all_notes()
    return [note for note in all_notes if note.get("user_id") == user_id]


def save_user_note(user_id, title, note_text):
    """Save a new note with user_id"""
    all_notes = load_all_notes()
    all_notes.append({
        "user_id": user_id,
        "title": title,
        "note": note_text,
        "time": datetime.now().strftime("%d %b %Y, %I:%M %p"),
    })
    save_all_notes(all_notes)


def update_user_note(user_id, index, editednote, editedtitle):
    """Update a note belonging to user"""
    all_notes = load_all_notes()
    user_notes_indices = [i for i, n in enumerate(all_notes) if n.get("user_id") == user_id]
    
    if index < len(user_notes_indices):
        actual_index = user_notes_indices[index]
        if editednote:
            all_notes[actual_index]["note"] = editednote
        if editedtitle:
            all_notes[actual_index]["title"] = editedtitle
        all_notes[actual_index]["time"] = datetime.now().strftime("%d %b %Y, %I:%M %p")
        save_all_notes(all_notes)


def delete_user_note(user_id, index):
    """Delete a note belonging to user"""
    all_notes = load_all_notes()
    user_notes_indices = [i for i, n in enumerate(all_notes) if n.get("user_id") == user_id]
    
    if index < len(user_notes_indices):
        actual_index = user_notes_indices[index]
        all_notes.pop(actual_index)
        save_all_notes(all_notes)


def init_notes(app):

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
            index = request.form.get("index")
            index_del = request.form.get("index_del")
            editednote = request.form.get("editednote")
            editedtitle = request.form.get("editedtitle")
            search = request.form.get("search")

            searchednote = None

            if title and note_text:
                save_user_note(user_id, title, note_text)
                notes = get_user_notes(user_id)

            if index is not None and (editednote or editedtitle):
                update_user_note(user_id, int(index), editednote, editedtitle)
                notes = get_user_notes(user_id)

            if index_del is not None and request.form.get("delete") == "Delete":
                delete_user_note(user_id, int(index_del))
                notes = get_user_notes(user_id)

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