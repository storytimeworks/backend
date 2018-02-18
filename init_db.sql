CREATE TABLE chinese_entries (
  id INT NOT NULL AUTO_INCREMENT,
  chinese TEXT NOT NULL,
  english TEXT NOT NULL,
  pinyin TEXT NOT NULL,
  source_is_chinese BOOLEAN NOT NULL,
  translations TEXT NOT NULL,
  PRIMARY KEY (id)
);

INSERT INTO chinese_entries (chinese, english, pinyin, source_is_chinese, translations) VALUES ("我", "I, me", "wǒ", 1, "1");
INSERT INTO chinese_entries (chinese, english, pinyin, source_is_chinese, translations) VALUES ("是", "to be", "shì", 1, "2");
INSERT INTO chinese_entries (chinese, english, pinyin, source_is_chinese, translations) VALUES ("我", "I", "wǒ", 0, "1");
INSERT INTO chinese_entries (chinese, english, pinyin, source_is_chinese, translations) VALUES ("是", "be", "shì", 0, "2");

CREATE TABLE chinese_translations (
  id INT NOT NULL AUTO_INCREMENT,
  chinese TEXT NOT NULL,
  english TEXT NOT NULL,
  pinyin TEXT NOT NULL,
  definition TEXT NOT NULL,
  pos TEXT NOT NULL,
  chinese_sentence TEXT NOT NULL,
  english_sentence TEXT NOT NULL,
  PRIMARY KEY (id)
);

INSERT INTO chinese_translations (chinese, english, pinyin, definition, pos, chinese_sentence, english_sentence) VALUES ("我", "I", "wǒ", "(pronoun)", "pronoun", "{我}是沙拉。", "{I} am Sarah.");
INSERT INTO chinese_translations (chinese, english, pinyin, definition, pos, chinese_sentence, english_sentence) VALUES ("是", "be", "shì", "(verb)", "verb", "我{是}沙拉。", "I {am} Sarah");
