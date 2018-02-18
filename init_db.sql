CREATE TABLE chinese_translations (
  id INT NOT NULL AUTO_INCREMENT,
  definition TEXT NOT NULL,
  pos TEXT NOT NULL,
  chinese_sentence TEXT NOT NULL,
  english_sentence TEXT NOT NULL,
  PRIMARY KEY (id)
);

INSERT INTO chinese_translations (definition, pos, chinese_sentence, english_sentence) VALUES ("(indirect object)", "pronoun", "{我}是沙拉。", "{I} am Sarah.");
INSERT INTO chinese_translations (definition, pos, chinese_sentence, english_sentence) VALUES ("(verb)", "verb", "我{是}沙拉。", "I {am} Sarah");

CREATE TABLE chinese_entries (
  id INT NOT NULL AUTO_INCREMENT,
  chinese TEXT,
  english TEXT,
  pinyin TEXT,
  translations TEXT NOT NULL,
  PRIMARY KEY (id)
);

INSERT INTO chinese_entries (english, translations) VALUES ("I", "1");
INSERT INTO chinese_entries (chinese, pinyin, translations) VALUES ("我", "wǒ", "1");
INSERT INTO chinese_entries (english, translations) VALUES ("be", "2");
INSERT INTO chinese_entries (chinese, pinyin, translations) VALUES ("是", "shì", "2");
