import json

class Translation:
    id = 0
    definition = ""
    pos = ""
    chinese_sentence = ""
    english_sentence = ""

    def __init__(self, row):
        self.id = row[0]
        self.definition = row[1]
        self.pos = row[2]
        self.chinese_sentence = row[3]
        self.english_sentence = row[4]

    def dict(self):
        return {
            "id": self.id,
            "definition": self.definition,
            "pos": self.pos,
            "chinese_sentence": self.chinese_sentence,
            "english_sentence": self.english_sentence
        }
