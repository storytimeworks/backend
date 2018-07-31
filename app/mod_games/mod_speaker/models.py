import jieba, json

from app import db
from app.chinese import segment
from app.mod_games.question import Question
from app.mod_games.result import Result

class SpeakerResult(Result):
    __tablename__ = "speaker_results"

class SpeakerQuestion(Question):

    __tablename__ = "speaker_questions"

    result_type = SpeakerResult

    prompt = db.Column(db.String(255), nullable=False)
    words = db.Column(db.String(255), nullable=False)

    def __init__(self, prompt):
        self.prompt = prompt
        self.words = json.dumps(segment(prompt))

    def serialize(self):
        return {
            "id": self.id,
            "prompt": self.prompt,
            "words": json.loads(self.words),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
