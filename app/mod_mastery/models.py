from app import db

class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

class Mastery(Base):

    __tablename__ = "masteries"

    user_id = db.Column(db.Integer, nullable=False)
    entry_id = db.Column(db.Integer, nullable=False)
    mastery = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id, entry_id):
        self.user_id = user_id
        self.entry_id = entry_id
        self.mastery = 0

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "entry_id": self.entry_id,
            "mastery": self.mastery
        }
