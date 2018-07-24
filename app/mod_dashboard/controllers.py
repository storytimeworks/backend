from flask import Blueprint, jsonify, request

from app import admin_required, db
from app.chinese import segment
from app.mod_games.mod_scribe.models import ScribeQuestion
from app.mod_vocab.models import Entry

mod_dashboard = Blueprint("dashboard", __name__, url_prefix="/dashboard")

def get_scribe_stats():
    questions = ScribeQuestion.query.all()

    words = set()

    for question in questions:
        question_words = segment(question.chinese)
        words.update(question_words)

    total_entries = len(words)

    entries = Entry.query.filter(Entry.chinese.in_(words)).all()

    for entry in entries:
        words.remove(entry.chinese)

    return {
        "name": "Scribe",
        "completed_entries": total_entries - len(words),
        "total_entries": total_entries,
        "completed_questions": len(questions),
        "total_questions": 200,
        "needed_entries": list(words)
    }

@mod_dashboard.route("", methods=["GET"])
@admin_required
def get_stats():
    stats = [
        get_scribe_stats()
    ]

    return jsonify(stats)
