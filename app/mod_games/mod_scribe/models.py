from app import db
from app.pinyin import pinyin

class ScribeQuestion(db.Model):

    __tablename__ = "scribe_questions"

    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.String(255), nullable=False)

    def __init__(self, prompt):
        self.prompt = prompt

    def serialize(self):
        return {
            "id": self.id,
            "pinyin": pinyin(self.prompt),
            "prompt": self.prompt
        }

class ScribeResult(db.Model):

    __tablename__ = "scribe_results"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    game_id = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    wrong_answers = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    def __init__(self, user_id, game_id, correct_answers, wrong_answers):
        self.user_id = user_id
        self.game_id = game_id
        self.correct_answers = correct_answers
        self.wrong_answers = wrong_answers
