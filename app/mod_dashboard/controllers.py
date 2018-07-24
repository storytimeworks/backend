from flask import Blueprint, jsonify, request
import json

from app import admin_required, db
from app.chinese import segment
from app.mod_games.mod_compound.models import CompoundQuestion
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

def get_compound_stats():
    questions = CompoundQuestion.query.all()

    words = set()

    for question in questions:
        all_words = []
        choices = [x for x in json.loads(question.choices) if len(x) > 0]

        for column in choices:
            all_words.extend([x[0] for x in column])

        all_words.append("".join([x[0][0] for x in choices]))

        words.update(all_words)

    total_entries = len(words)

    entries = Entry.query.filter(Entry.chinese.in_(words)).all()

    for entry in entries:
        words.remove(entry.chinese)

    return {
        "name": "Compound",
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
        get_compound_stats(),
        get_scribe_stats()
    ]

    return jsonify(stats)
