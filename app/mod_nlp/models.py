from app import db

class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

class NLPApp(Base):

    __tablename__ = "nlp_apps"

    name = db.Column(db.String(30), nullable=False)
    passage_id = db.Column(db.Integer, nullable=False)
    access_token = db.Column(db.String(32), nullable=False)
    app_id = db.Column(db.String(36), nullable=False)

    def __init__(self, name, passage_id, access_token, app_id):
        self.name = name
        self.passage_id = passage_id
        self.access_token = access_token
        self.app_id = app_id

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "passage_id": self.passage_id,
            "access_token": self.access_token,
            "app_id": self.app_id
        }
