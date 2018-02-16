def normalize(text):
    pinyin_letters = {
        "ǎ": "a",
        "á": "a",
        "ī": "i",
        "ǐ": "i",
        "ǚ": "u"
    }

    for letter in text:
        if letter in pinyin_letters:
            text.replace(letter, pinyin_letters[letter])

    return text
