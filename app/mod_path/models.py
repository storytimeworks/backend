from app import db

class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

class PathAction(Base):

    __tablename__ = "path_actions"

    passage_id = db.Column(db.Integer, nullable=False)
    part = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, passage_id, part, user_id):
        self.passage_id = passage_id
        self.part = part
        self.user_id = user_id
