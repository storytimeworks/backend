from app import db

class WriterAnswer(db.Model):

    __tablename__ = "writer_answers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(36), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, name):
        self.name = name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "timestamp": self.timestamp
        }
