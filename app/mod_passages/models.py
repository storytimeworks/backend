from app import db
import json

class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Passage(Base):

    __tablename__ = "passages"

    chinese_name = db.Column(db.Text, nullable=False)
    english_name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    story_id = db.Column(db.Integer, nullable=False)
    data = db.Column(db.Text, nullable=False)

    def __init__(self, chinese_name, english_name, description, story_id, data):
        self.chinese_name = chinese_name
        self.english_name = english_name
        self.description = description
        self.story_id = story_id
        self.data = data

    def serialize(self):
        return {
            "id": self.id,
            "chinese_name": self.chinese_name,
            "english_name": self.english_name,
            "description": self.description,
            "story_id": self.story_id,
            "data": json.loads(self.data),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
