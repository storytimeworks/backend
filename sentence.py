import json

class Sentence:
    chinese = ""
    english = ""

    def __init__(self, row):
        self.chinese = row[0]
        self.english = row[1]

    def dict(self):
        return {
            "chinese": self.chinese,
            "english": self.english
        }
