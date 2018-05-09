from app import db

class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

class Attempt(Base):

    __tablename__ = "flashcard_attempts"

    entry_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    correct = db.Column(db.Boolean, nullable=False)
    attempted_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __init__(self, entry_id, user_id, correct):
        self.entry_id = entry_id
        self.user_id = user_id
        self.correct = correct

    def serialize(self):
        return {
            "id": self.id,
            "entry_id": self.entry_id,
            "user_id": self.user_id,
            "correct": self.correct,
            "attempted_at": self.attempted_at
        }
