from flask import Blueprint, jsonify, request
import json, re

from app import admin_required, db
from app.chinese import segment
from app.mod_games.mod_compound.models import CompoundQuestion
from app.mod_games.mod_copy_edit.models import CopyEditQuestion
from app.mod_games.mod_expressions.models import ExpressionsQuestion
from app.mod_games.mod_scribe.models import ScribeQuestion
from app.mod_vocab.models import Entry

mod_dashboard = Blueprint("dashboard", __name__, url_prefix="/dashboard")

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

def get_copy_edit_stats():
    questions = CopyEditQuestion.query.all()

    return {
        "name": "Copy Edit",
        "completed_entries": 0,
        "total_entries": 0,
        "completed_questions": len(questions),
        "total_questions": 200,
        "needed_entries": []
    }

def get_expressions_stats():
    questions = ExpressionsQuestion.query.all()

    words = set()

    for question in questions:
        choices = [question.choice_1, question.choice_2, question.choice_3, question.choice_4]

        for choice in choices:
            if len(re.findall(r"[\u4e00-\u9fff]+", choice)) > 0:
                choice = choice.replace("\n", "").replace("?", "").replace("？", "").replace("!", "").replace("！", "").replace(".", "").replace("。", "")
                words.add(choice)

    total_entries = len(words)

    entries = Entry.query.filter(Entry.chinese.in_(words)).all()

    for entry in entries:
        words.remove(entry.chinese)

    return {
        "name": "Expressions",
        "completed_entries": total_entries - len(words),
        "total_entries": total_entries,
        "completed_questions": len(questions),
        "total_questions": 100,
        "needed_entries": list(words)
    }

def get_scribe_stats():
    questions = ScribeQuestion.query.all()

    words = set()

    for question in questions:
        question_words = segment(question.chinese)
        words.update(question_words)

    words.remove("，")
    words.remove("？")
    words.remove("！")

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
        get_compound_stats(),
        get_copy_edit_stats(),
        get_expressions_stats(),
        get_scribe_stats()
    ]

    return jsonify(stats)
