import json

class Entry:
    id = 0
    chinese = None
    english = None
    pinyin = None
    translations = None
    translation_ids = []

    def __init__(self, row):
        self.id = row[0]
        self.chinese = row[1]
        self.english = row[2]
        self.pinyin = row[3]
        self.translation_ids = [int(x) for x in row[4].split(",")]

    def dict(self):
        data = {"id": self.id}
        
        if self.chinese is not None and self.pinyin is not None:
            data["chinese"] = self.chinese
            data["pinyin"] = self.pinyin
        
        if self.english is not None:
            data["english"] = self.english
        
        if self.translations is not None:
            data["translations"] = self.translations
        elif self.translation_ids is not None:
            data["translation_ids"] = self.translation_ids
        
        return data
