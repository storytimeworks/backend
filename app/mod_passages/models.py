from app import db
import json

class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Passage(Base):

    __tablename__ = "passages"

    name = db.Column(db.Text, nullable=False)
    story_id = db.Column(db.Integer, nullable=False)
    data = db.Column(db.Text, nullable=False)

    def __init__(self, name, story_id, data):
        self.name = name
        self.story_id = story_id
        self.data = data

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "story_id": self.story_id,
            "data": json.loads(self.data),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
