from app import db
import json

class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Story(Base):

    __tablename__ = "stories"

    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    passage_ids = db.Column(db.Text, nullable=False)

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.passage_ids = "[]"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "passage_ids": json.loads(self.passage_ids),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
