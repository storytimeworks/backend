from app import db

class Log(db.Model):

    __tablename__ = "logs"

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(15), nullable=False)
    method = db.Column(db.String(7), nullable=False)
    path = db.Column(db.Text, nullable=False)
    status_code = db.Column(db.SmallInteger, nullable=False)
    user_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, ip, method, path, status_code, user_id = None):
        self.ip = ip
        self.method = method
        self.path = path
        self.status_code = status_code
        self.user_id = user_id
