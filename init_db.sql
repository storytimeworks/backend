CREATE TABLE chinese_entries (
  id INT NOT NULL AUTO_INCREMENT,
  chinese TEXT NOT NULL,
  english TEXT NOT NULL,
  pinyin TEXT NOT NULL,
  source_is_chinese BOOLEAN NOT NULL,
  translations TEXT NOT NULL,
  categories TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) CHARACTER SET utf8 COLLATE utf8_unicode_ci;

INSERT INTO chinese_entries (chinese, english, pinyin, source_is_chinese, translations, categories) VALUES ("我", "I, me", "wǒ", 1, "[]", "[]");
INSERT INTO chinese_entries (chinese, english, pinyin, source_is_chinese, translations, categories) VALUES ("是", "to be", "shì", 1, "[]", "[]");
INSERT INTO chinese_entries (chinese, english, pinyin, source_is_chinese, translations, categories) VALUES ("我", "I", "wǒ", 0, "[]", "[]");
INSERT INTO chinese_entries (chinese, english, pinyin, source_is_chinese, translations, categories) VALUES ("是", "be", "shì", 0, "[]", "[]");

CREATE TABLE users (
  id INT NOT NULL AUTO_INCREMENT,
  username TEXT NOT NULL,
  email TEXT NOT NULL,
  password TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  groups TEXT NOT NULL,
  PRIMARY KEY (id)
);
