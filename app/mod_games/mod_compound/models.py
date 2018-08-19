from app import db
from app.mod_games.question import Question
from app.mod_games.result import Result
from app.mod_vocab.models import Entry

import json

class CompoundResult(Result):
    __tablename__ = "compound_results"

class CompoundQuestion(Question):

    __tablename__ = "compound_questions"

    result_type = CompoundResult

    prompt = db.Column(db.String(255), nullable=False)
    choices = db.Column(db.Text, nullable=False)
    answer = db.Column(db.String(255), nullable=False)

    def __init__(self, prompt, choices, answer):
        self.prompt = prompt
        self.choices = json.dumps(choices)
        self.answer = answer

    def serialize(self):
        all_choices = []
        choices = [x for x in json.loads(self.choices) if len(x) > 0]

        for column in choices:
            all_choices.extend([x["character"] for x in column])

        all_choices.append("".join([x[0]["character"] for x in choices]))

        entries = Entry.query.filter(Entry.chinese.in_(all_choices)).all()
        words = [entry.chinese for entry in entries]
        translations = {entry.chinese: entry.english for entry in entries}

        return {
            "id": self.id,
            "prompt": self.prompt,
            "choices": choices,
            "answer": self.answer,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "translations": translations,
            "words": all_choices
        }
