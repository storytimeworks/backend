from app import db
import json

class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.Text, nullable=False)
    filename = db.Column(db.String(40), nullable=False)
    voice = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __init__(self, source, filename, voice):
        self.source = source
        self.filename = filename
        self.voice = voice

class ChineseSpeechSynthesis(Base):

    __tablename__ = "chinese_speech"

class EnglishSpeechSynthesis(Base):

    __tablename__ = "english_speech"
