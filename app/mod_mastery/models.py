from app import db

class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Mastery(Base):

    __tablename__ = "masteries"

    user_id = db.Column(db.Integer, nullable=False)
    entry_id = db.Column(db.Integer, nullable=False)
    mastery = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id, entry_id, mastery):
        self.user_id = user_id
        self.entry_id = entry_id
        self.mastery = mastery

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "entry_id": self.entry_id,
            "mastery": self.mastery,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
