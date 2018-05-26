from app import db
import json

class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Story(Base):

    __tablename__ = "stories"

    chinese_name = db.Column(db.Text, nullable=False)
    english_name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    passage_ids = db.Column(db.Text, nullable=False)

    def __init__(self, chinese_name, english_name, description):
        self.chinese_name = chinese_name
        self.english_name = english_name
        self.description = description
        self.passage_ids = "[]"

    def serialize(self):
        return {
            "id": self.id,
            "chinese_name": self.chinese_name,
            "english_name": self.english_name,
            "description": self.description,
            "passage_ids": json.loads(self.passage_ids),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
