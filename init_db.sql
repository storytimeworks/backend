DROP DATABASE IF EXISTS storytime_test;

CREATE DATABASE storytime_test;
USE storytime_test;

CREATE TABLE entries (
  id INT NOT NULL AUTO_INCREMENT,
  chinese TEXT NOT NULL,
  english TEXT NOT NULL,
  pinyin TEXT NOT NULL,
  translations TEXT NOT NULL,
  categories TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) CHARACTER SET utf8 COLLATE utf8_unicode_ci;

CREATE TABLE users (
  id INT NOT NULL AUTO_INCREMENT,
  username TEXT NOT NULL,
  email TEXT NOT NULL,
  password TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  groups TEXT NOT NULL,
  settings TEXT NOT NULL,
  verified BOOLEAN NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE chinese_speech (
  id INT NOT NULL AUTO_INCREMENT,
  source TEXT NOT NULL,
  filename CHAR(40) NOT NULL,
  voice TINYINT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) CHARACTER SET utf8;

CREATE TABLE english_speech (
  id INT NOT NULL AUTO_INCREMENT,
  source TEXT NOT NULL,
  filename CHAR(40) NOT NULL,
  voice TINYINT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) CHARACTER SET utf8;

CREATE TABLE stories (
  id INT NOT NULL AUTO_INCREMENT,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  passage_ids TEXT NOT NULL,
  position INT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE TABLE passages (
  id INT NOT NULL AUTO_INCREMENT,
  chinese_name TEXT NOT NULL,
  english_name TEXT NOT NULL,
  description TEXT NOT NULL,
  story_id INT NOT NULL,
  data TEXT NOT NULL,
  new_words TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE TABLE email_verifications (
  id INT NOT NULL AUTO_INCREMENT,
  code CHAR(32) NOT NULL,
  user_id INT NOT NULL,
  email TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE TABLE password_resets (
  id INT NOT NULL AUTO_INCREMENT,
  code CHAR(32) NOT NULL,
  user_id INT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE TABLE flashcard_attempts (
  id INT NOT NULL AUTO_INCREMENT,
  entry_id INT NOT NULL,
  user_id INT NOT NULL,
  correct BOOLEAN NOT NULL,
  attempted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE TABLE copy_edit_sentences (
  id INT NOT NULL AUTO_INCREMENT,
  sentence TEXT NOT NULL,
  explanation TEXT NOT NULL,
  correct_sentence TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

-- $2b$12$vdNVmXFt/rJ1csHcYvW1SeYXwXb.PLTGgjy0MIAIkCbhcLu2g9E0q is a bcrypt hash of "this is my password"
INSERT INTO users (username, email, password, groups, settings, verified) VALUES ("admin", "admin@storytime.works", "$2b$12$vdNVmXFt/rJ1csHcYvW1SeYXwXb.PLTGgjy0MIAIkCbhcLu2g9E0q", "[1]", "{}", 1);
INSERT INTO users (username, email, password, groups, settings, verified) VALUES ("user", "user@storytime.works", "$2b$12$vdNVmXFt/rJ1csHcYvW1SeYXwXb.PLTGgjy0MIAIkCbhcLu2g9E0q", "[]", "{}", 1);

INSERT INTO entries (chinese, english, pinyin, translations, categories) VALUES ("我", "I, me", "wǒ", "[]", "[]");

INSERT INTO stories (name, description, passage_ids, position) VALUES ("Basics", "Sarah introduces herself to the reader.", "[1]", 1);
INSERT INTO passages (chinese_name, english_name, description, story_id, data, new_words) VALUES ("你好", "Hello", "Sarah introduces herself to the reader.", 1, '{"components": []}', "[]");
