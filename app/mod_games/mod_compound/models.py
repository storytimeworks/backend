from app import db
from pypinyin import pinyin

import json

class CompoundQuestion(db.Model):

    __tablename__ = "compound_questions"

    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.String(255), nullable=False)
    choices = db.Column(db.String(255), nullable=False)
    pinyin_choices = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __init__(self, prompt, choices):
        self.prompt = prompt
        self.choices = json.dumps(choices)

        pinyin_choices = choices

        for idx, choice in enumerate(pinyin_choices):
            pinyin_choices[idx] = pinyin(pinyin_choices[idx])[0][0]

        self.pinyin_choices = json.dumps(pinyin_choices)

    def serialize(self):
        return {
            "id": self.id,
            "prompt": self.prompt,
            "choices": json.loads(self.choices),
            "pinyin_choices": json.loads(self.pinyin_choices),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
