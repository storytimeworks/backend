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

INSERT INTO users (username, email, password, groups, settings, verified) VALUES ("jack", "jack@storytime.works", "passwordstorytime", "[1]", "{}", 1);
INSERT INTO users (username, email, password, groups, settings, verified) VALUES ("hello", "test@test.com", "this is my password", "", "{}", 1);

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

CREATE TABLE passages (
  id INT NOT NULL AUTO_INCREMENT,
  chinese_name TEXT NOT NULL,
  english_name TEXT NOT NULL,
  description TEXT NOT NULL,
  story_id INT NOT NULL,
  data TEXT NOT NULL,
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
