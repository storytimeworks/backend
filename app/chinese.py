import jieba
from pypinyin import pinyin as pypinyin

from app import db

def pinyin(text):
    # Separate Chinese sentences into separate words
    word_generator = jieba.cut(text)
    words = [{"chinese": word, "punctuation": False} for word in word_generator]

    # Add pinyin to the word objects
    pinyin_words = [pypinyin(word["chinese"]) for word in words]
    flattened_pinyin_words = [[j for i in words for j in i] for words in pinyin_words]
    joined_pinyin_words = ["".join(words) for words in flattened_pinyin_words]

    # True if the next word in the loop needs to be capitalized
    capitalize_next_word = True

    for i, _ in enumerate(words):
        word = joined_pinyin_words[i]

        if capitalize_next_word:
            # Capitalize this word, don't capitalize the next one
            word = word.capitalize()
            capitalize_next_word = False

        # Replace Chinese punctutation with regular punctuation
        if word == "。":
            capitalize_next_word = True
            word = "."
            words[i]["punctuation"] = True
        elif word == "，":
            word = ","
            words[i]["punctuation"] = True
        elif word == "！":
            capitalize_next_word = True
            word = "!"
            words[i]["punctuation"] = True
        elif word == "？":
            capitalize_next_word = True
            word = "?"
            words[i]["punctuation"] = True

        words[i]["pinyin"] = word

    sentence = ""

    for word in words:
        if word["punctuation"]:
            sentence += word["pinyin"]
        else:
            sentence += " " + word["pinyin"]

    return sentence[1:len(sentence)]

class JiebaException(db.Model):

    __tablename__ = "jieba_exceptions"

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(255), nullable=False)
    replacement = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

def segment(chinese):
    punctuation = ["。", "？", "！", "，", ".", "!", "?", ","]
    words = [x for x in jieba.cut(chinese) if x not in punctuation]

    exceptions = JiebaException.query.filter(JiebaException.word.in_(words) & ~JiebaException.word.like("%,%")).all()
    exceptions_map = {exception.word: exception.replacement for exception in exceptions}

    new_words = []

    for word in words:
        if word in exceptions_map:
            new_words.extend(exceptions_map[word].split(","))
        else:
            new_words.append(word)

    new_words_string = ",".join(new_words)

    reverse_exceptions = JiebaException.query.filter(JiebaException.word.like("%,%")).all()

    for exception in reverse_exceptions:
        new_words_string = new_words_string.replace(exception.word, exception.replacement)

    return new_words_string.split(",")
