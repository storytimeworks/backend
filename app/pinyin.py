import jieba
from pypinyin import pinyin as pypinyin

def pinyin(text):
    # Separate Chinese sentences into separate words
    word_generator = jieba.cut(text, cut_all=False)
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
