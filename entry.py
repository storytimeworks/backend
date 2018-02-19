import json

class Entry:
    id = 0
    chinese = None
    english = None
    pinyin = None
    source_is_chinese = None
    translations = None

    def __init__(self, row):
        self.id = row[0]
        self.chinese = row[1]
        self.english = row[2]
        self.pinyin = row[3]
        self.source_is_chinese = row[4]
        self.translations = json.loads(row[5])

    def dict(self):
        return {
            "id": self.id,
            "chinese": self.chinese,
            "english": self.english,
            "pinyin": self.pinyin,
            "source_is_chinese": self.source_is_chinese,
            "translations": self.translations
        }
