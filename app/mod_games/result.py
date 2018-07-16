from app import db

class Result(db.Model):

    __abstract__ = True

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
