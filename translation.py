import json

class Translation:
    id = 0
    source = ""
    target = ""
    pinyin = ""
    definitions = []

    def __init__(self, row):
        self.id = row[0]
        self.source = row[1]
        self.target = row[2]
        self.pinyin = row[3]
        self.definitions = json.loads(row[4])

    def dict(self):
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "pinyin": self.pinyin,
            "definitions": self.definitions
        }
