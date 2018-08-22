import json

from app.mod_games.mod_scribe import ScribeQuestion
from app.mod_games.result import Result

class SpeakerResult(Result):
    __tablename__ = "speaker_results"

class SpeakerQuestion(ScribeQuestion):

    __table_args__ = {"extend_existing": True}
    __tablename__ = "scribe_questions"

    num_questions = 3
    result_type = SpeakerResult

    def serialize(self):
        return {
            "id": self.id,
            "chinese": self.chinese,
            "english": self.english,
            "other_english_answers": json.loads(self.other_english_answers),
            "words": json.loads(self.words),
            "words_pinyin": json.loads(self.words_pinyin),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
