from app import db
from app.mod_games.question import Question
from app.mod_games.result import Result
from app.mod_vocab.models import Entry

import json
from pypinyin import pinyin

class CompoundResult(Result):
    __tablename__ = "compound_results"

class CompoundQuestion(Question):

    __tablename__ = "compound_questions"

    result_type = CompoundResult

    prompt = db.Column(db.String(255), nullable=False)
    choices = db.Column(db.String(255), nullable=False)
    pinyin_choices = db.Column(db.String(255), nullable=False)

    def __init__(self, prompt, choices):
        self.prompt = prompt
        self.choices = json.dumps(choices)

        pinyin_choices = choices

        for idx, choice in enumerate(pinyin_choices):
            pinyin_choices[idx] = pinyin(pinyin_choices[idx])[0][0]

        self.pinyin_choices = json.dumps(pinyin_choices)

    def serialize(self):
        all_choices = []
        choices = [x for x in json.loads(self.choices) if len(x) > 0]
        pinyin_choices = [x for x in json.loads(self.pinyin_choices) if len(x) > 0]

        for column in choices:
            all_choices.extend([x[0] for x in column])

        all_choices.append("".join([x[0][0] for x in choices]))

        entries = Entry.query.filter(Entry.chinese.in_(all_choices)).all()
        words = [entry.chinese for entry in entries]
        translations = {entry.chinese: entry.english for entry in entries}

        return {
            "id": self.id,
            "prompt": self.prompt,
            "choices": choices,
            "pinyin_choices": pinyin_choices,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "translations": translations,
            "words": words
        }
