from app import db
from app.mod_games.question import Question
from app.mod_games.result import Result

class CopyEditResult(Result):
    __tablename__ = "copy_edit_results"

class CopyEditQuestion(Question):

    __tablename__ = "copy_edit_questions"
    result_type = CopyEditResult

    prompt = db.Column(db.String(255), nullable=False)

    def __init__(self, prompt):
        self.prompt = prompt

    def serialize(self):
        return {
            "id": self.id,
            "prompt": self.prompt,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
