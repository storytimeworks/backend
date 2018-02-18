import json

class Translation:
    id = 0
    chinese = ""
    english = ""
    pinyin = ""
    definition = ""
    pos = ""
    chinese_sentence = ""
    english_sentence = ""

    def __init__(self, row):
        self.id = row[0]
        self.chinese = row[1]
        self.english = row[2]
        self.pinyin = row[3]
        self.definition = row[4]
        self.pos = row[5]
        self.chinese_sentence = row[6]
        self.english_sentence = row[7]

    def dict(self):
        return {
            "id": self.id,
            "chinese": self.chinese,
            "english": self.english,
            "pinyin": self.pinyin,
            "definition": self.definition,
            "pos": self.pos,
            "chineseSentence": self.chinese_sentence,
            "englishSentence": self.english_sentence
        }
