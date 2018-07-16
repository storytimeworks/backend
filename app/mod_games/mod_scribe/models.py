import jieba, json

from app import db
from app.chinese import pinyin, segment
from app.mod_games.question import Question
from app.mod_games.result import Result

class ScribeResult(Result):
    __tablename__ = "scribe_results"

class ScribeQuestion(Question):

    __tablename__ = "scribe_questions"

    result_type = ScribeResult

    chinese = db.Column(db.String(255), nullable=False)
    english = db.Column(db.String(255), nullable=False)
    other_english_answers = db.Column(db.String, nullable=False)

    def __init__(self, chinese, english, other_english_answers):
        self.chinese = chinese
        self.english = english
        self.other_english_answers = json.dumps(self.other_english_answers)

    def serialize(self):
        return {
            "id": self.id,
            "chinese": self.chinese,
            "english": self.english,
            "other_english_answers": json.loads(self.other_english_answers),
            "pinyin": pinyin(self.chinese),
            "words": [word for word in segment(self.chinese)],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
