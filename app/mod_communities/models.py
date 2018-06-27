from app import db
import json

class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Community(Base):

    __tablename__ = "communities"

    name = db.Column(db.String(32), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class Post(Base):

    __tablename__ = "posts"

    posted_by = db.Column(db.Integer, nullable=False)
    community = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)

    def __init__(self, posted_by, community, text):
        self.posted_by = posted_by
        self.community = community
        self.text = text

    def serialize(self):
        return {
            "id": self.id,
            "posted_by": self.posted_by,
            "community": self.community,
            "text": self.text,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
