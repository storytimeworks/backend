from app import db

class MadMinuteResult(db.Model):

    __tablename__ = "mad_minute_results"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    game_id = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    wrong_answers = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, user_id, game_id, correct_answers, wrong_answers):
        self.user_id = user_id
        self.game_id = game_id
        self.correct_answers = correct_answers
        self.wrong_answers = wrong_answers
