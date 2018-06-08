from app import db

class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

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
            "gender": self.gender
        }
