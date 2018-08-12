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
    pinyin = db.Column(db.String(255), nullable=False)
    words = db.Column(db.String(255), nullable=False)
    words_pinyin = db.Column(db.String(255), nullable=False)
    english = db.Column(db.String(255), nullable=False)
    other_english_answers = db.Column(db.Text, nullable=False)

    def __init__(self, chinese, english, other_english_answers):
        self.chinese = chinese
        self.pinyin = pinyin(chinese)
        self.words = json.dumps(segment(chinese))
        self.words_pinyin = json.dumps([pinyin(word) for word in segment(chinese)])
        self.english = english
        self.other_english_answers = json.dumps(self.other_english_answers)

    def serialize(self):
        return {
            "id": self.id,
            "chinese": self.chinese,
            "pinyin": self.pinyin,
            "words": json.loads(self.words),
            "english": self.english,
            "other_english_answers": json.loads(self.other_english_answers),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
