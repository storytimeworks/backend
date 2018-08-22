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

    prompts = db.Column(db.Text, nullable=False)
    choices = db.Column(db.Text, nullable=False)
    words = db.Column(db.String(255), nullable=False)

    def __init__(self, prompts, choices):
        self.prompts = json.dumps(prompts)
        self.choices = json.dumps(choices)

        words = []

        for prompt in prompts:
            words.extend(segment(prompt))

        self.words = json.dumps(words)

    def serialize(self):
        return {
            "id": self.id,
            "prompts": json.loads(self.prompts),
            "choices": json.loads(self.choices),
            "words": json.loads(self.words),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
