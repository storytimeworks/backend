from app import db
from app.chinese import pinyin, segment
from app.mod_games.question import Question
from app.mod_games.result import Result

class ExpressionsResult(Result):
    __tablename__ = "expressions_results"

class ExpressionsQuestion(Question):

    __tablename__ = "expressions_questions"
    result_type = ExpressionsResult

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
        words = []
        words.extend(segment(self.choice_1))
        words.extend(segment(self.choice_2))
        words.extend(segment(self.choice_3))
        words.extend(segment(self.choice_4))

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
            "choice_1_pinyin": pinyin(self.choice_1),
            "choice_2_pinyin": pinyin(self.choice_2),
            "choice_3_pinyin": pinyin(self.choice_3),
            "choice_4_pinyin": pinyin(self.choice_4),
            "followed_by": self.followed_by,
            "preceded_by": self.preceded_by,
            "words": words,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
