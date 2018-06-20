from app import db

class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

class ExpressionsQuestion(Base):

    __tablename__ = "expressions_questions"

    prompt = db.Column(db.String(255), nullable=False)
    correct_choice = db.Column(db.String(255), nullable=False)
    choice_2 = db.Column(db.String(255), nullable=False)
    choice_3 = db.Column(db.String(255), nullable=False)
    choice_4 = db.Column(db.String(255), nullable=False)

    def __init__(self, prompt, correct_choice, choice_2, choice_3, choice_4):
        self.prompt = prompt
        self.correct_choice = correct_choice
        self.choice_2 = choice_2
        self.choice_3 = choice_3
        self.choice_4 = choice_4

    def serialize(self):
        return {
            "id": self.id,
            "prompt": self.prompt,
            "choices": [
                self.correct_choice,
                self.choice_2,
                self.choice_3,
                self.choice_4
            ]
        }
