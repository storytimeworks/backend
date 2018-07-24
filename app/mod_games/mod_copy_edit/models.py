from app import db
from app.chinese import segment
from app.mod_games.question import Question
from app.mod_games.result import Result

class CopyEditResult(Result):
    __tablename__ = "copy_edit_results"

class CopyEditQuestion(Question):

    __tablename__ = "copy_edit_questions"
    result_type = CopyEditResult

    prompt = db.Column(db.String(255), nullable=False)
    explanation = db.Column(db.String(255), nullable=False)
    correct_sentence = db.Column(db.String(255), nullable=False)

    def __init__(self, prompt, explanation, correct_sentence):
        self.prompt = prompt
        self.explanation = explanation
        self.correct_sentence = correct_sentence

    def serialize(self):
        start_range = 0
        end_range = 0

        try:
            start_range = self.prompt.index("{")
            end_range = self.prompt.index("}") - 1
        except ValueError:
            pass

        prompt_text = self.prompt.replace("{", "").replace("}", "")
        words = segment(prompt_text)

        return {
            "id": self.id,
            "prompt": self.prompt,
            "explanation": self.explanation,
            "correct_sentence": self.correct_sentence,
            "start_range": start_range,
            "end_range": end_range,
            "words": words,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
