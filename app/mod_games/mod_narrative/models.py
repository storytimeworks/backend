import json

from app import db
from app.chinese import segment
from app.mod_games.question import Question
from app.mod_games.result import Result

class NarrativeResult(Result):
    __tablename__ = "narrative_results"

class NarrativeQuestion(Question):

    __tablename__ = "narrative_questions"

    result_type = NarrativeResult

    parts = db.Column(db.Text, nullable=False)
    words = db.Column(db.String(255), nullable=False)

    def __init__(self, parts):
        self.update("parts", parts)

    def serialize(self):
        return {
            "id": self.id,
            "parts": json.loads(self.parts),
            "words": json.loads(self.words),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    def update(self, key, value):
        if key == "parts":
            self.parts = json.dumps(value)

            words = []

            for part in value:
                if "prompt" in part:
                    words.extend(segment(part["prompt"]))

            self.words = json.dumps(words)
