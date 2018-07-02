from app import db

class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Character(Base):

    __tablename__ = "characters"

    english_name = db.Column(db.String(20), nullable=False)
    chinese_name = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.Integer, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "english_name": self.english_name,
            "chinese_name": self.chinese_name,
            "gender": self.gender,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
