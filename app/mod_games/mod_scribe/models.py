import jieba, json

from app import db
from app.pinyin import pinyin

class ScribeQuestion(db.Model):

    __tablename__ = "scribe_questions"

    id = db.Column(db.Integer, primary_key=True)
    chinese = db.Column(db.String(255), nullable=False)
    english = db.Column(db.String(255), nullable=False)
    other_english_answers = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

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
            "words": [word for word in jieba.cut(self.chinese, cut_all=False)],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class ScribeResult(db.Model):

    __tablename__ = "scribe_results"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    game_id = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    wrong_answers = db.Column(db.Integer, nullable=False)
    correct_question_ids = db.Column(db.String(255), nullable=False)
    wrong_question_ids = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    def __init__(self, user_id, game_id, correct_answers, wrong_answers, correct_question_ids, wrong_question_ids):
        self.user_id = user_id
        self.game_id = game_id
        self.correct_answers = correct_answers
        self.wrong_answers = wrong_answers
        self.correct_question_ids = json.dumps(correct_question_ids)
        self.wrong_question_ids = json.dumps(wrong_question_ids)
