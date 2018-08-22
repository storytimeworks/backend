import json

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
        update("chinese", chinese)
        update("english", english)
        update("other_english_answers", other_english_answers)

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

    def update(self, key, value):
        if key == "chinese":
            self.chinese = value
            self.pinyin = pinyin(value)
            self.words = json.dumps(segment(value))
            self.words_pinyin = json.dumps([pinyin(word) for word in segment(value)])
        elif key == "other_english_answers":
            self.other_english_answers = json.dumps(value)
        else:
            super(ScribeQuestion, self).update(key, value)
