from app import db
from pypinyin import pinyin

class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

class ExpressionsQuestion(Base):

    __tablename__ = "expressions_questions"

    prompt = db.Column(db.String(255), nullable=False)
    choice_1 = db.Column(db.String(255), nullable=False)
    choice_2 = db.Column(db.String(255), nullable=False)
    choice_3 = db.Column(db.String(255))
    choice_4 = db.Column(db.String(255))
    choice_1_correct = db.Column(db.Boolean, nullable=False)
    choice_2_correct = db.Column(db.Boolean, nullable=False)
    choice_3_correct = db.Column(db.Boolean)
    choice_4_correct = db.Column(db.Boolean)
    followed_by = db.Column(db.Integer)
    preceded_by = db.Column(db.Integer)

    def __init__(self, prompt, choice_1, choice_2, choice_3, choice_4, choice_1_correct, choice_2_correct, choice_3_correct, choice_4_correct):
        self.prompt = prompt
        self.choice_1 = choice_1
        self.choice_2 = choice_2
        self.choice_3 = choice_3
        self.choice_4 = choice_4
        self.choice_1_correct = choice_1_correct
        self.choice_2_correct = choice_2_correct
        self.choice_3_correct = choice_3_correct
        self.choice_4_correct = choice_4_correct

    def serialize(self):
        return {
            "id": self.id,
            "prompt": self.prompt,
            "choice_1": self.choice_1,
            "choice_2": self.choice_2,
            "choice_3": self.choice_3,
            "choice_4": self.choice_4,
            "choice_1_correct": self.choice_1_correct,
            "choice_2_correct": self.choice_2_correct,
            "choice_3_correct": self.choice_3_correct,
            "choice_4_correct": self.choice_4_correct,
            "followed_by": self.followed_by,
            "preceded_by": self.preceded_by
        }
