from app import db
import json

class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Entry(Base):

    __tablename__ = "entries"

    chinese = db.Column(db.Text, nullable=False)
    english = db.Column(db.Text, nullable=False)
    pinyin = db.Column(db.Text, nullable=False)
    translations = db.Column(db.Text, nullable=False)
    categories = db.Column(db.Text, nullable=False)

    def __init__(self, chinese, english, pinyin):
        self.chinese = chinese
        self.english = english
        self.pinyin = pinyin
        self.translations = "[]"
        self.categories = "[]"

    def serialize(self):
        return {
            "id": self.id,
            "chinese": self.chinese,
            "english": self.english,
            "pinyin": self.pinyin,
            "translations": json.loads(self.translations),
            "categories": json.loads(self.categories),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class Sentence(Base):

    __tablename__ = "chinese_sentences"

    chinese = db.Column(db.Text, nullable=False)
    english = db.Column(db.Text, nullable=False)

    def __init__(self, chinese, english):
        self.chinse = chinese
        self.english = english

    def serialize(self):
        return {
            "id": self.id,
            "chinese": self.chinese,
            "english": self.english,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
