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
  password CHAR(60) NOT NULL,
  groups TEXT NOT NULL,
  settings TEXT NOT NULL,
  pending_email TEXT,
  saved_entry_ids TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
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
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  story_id INT NOT NULL,
  data TEXT NOT NULL,
  new_words TEXT NOT NULL,
  notes TEXT NOT NULL,
  parts TEXT NOT NULL,
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

CREATE TABLE logs (
  id INT NOT NULL AUTO_INCREMENT,
  ip VARCHAR(15) NOT NULL,
  method VARCHAR(7) NOT NULL,
  path TEXT NOT NULL,
  status_code SMALLINT NOT NULL,
  user_id INT,
  timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE TABLE path_actions (
  id INT NOT NULL AUTO_INCREMENT,
  passage_id INT NOT NULL,
  part TINYINT NOT NULL,
  user_id INT NOT NULL,
  timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE TABLE characters (
  id INT NOT NULL AUTO_INCREMENT,
  english_name VARCHAR(20) NOT NULL,
  chinese_name VARCHAR(20) NOT NULL,
  gender TINYINT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE TABLE chinese_name_characters (
  id INT NOT NULL AUTO_INCREMENT,
  name_character CHAR(1) NOT NULL,
  position TINYINT NOT NULL,
  attribute TINYINT,
  meaning VARCHAR(50),
  gender BOOLEAN,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE TABLE nlp_apps (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(30) NOT NULL,
  passage_id INT NOT NULL,
  access_token CHAR(32) NOT NULL,
  app_id CHAR(36) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE TABLE expressions_questions (
  id INT NOT NULL AUTO_INCREMENT,
  prompt VARCHAR(255) NOT NULL,
  choice_1 VARCHAR(255) NOT NULL,
  choice_2 VARCHAR(255) NOT NULL,
  choice_3 VARCHAR(255),
  choice_4 VARCHAR(255),
  choice_1_correct BOOLEAN NOT NULL,
  choice_2_correct BOOLEAN NOT NULL,
  choice_3_correct BOOLEAN,
  choice_4_correct BOOLEAN,
  followed_by INT,
  preceded_by INT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE TABLE masteries (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  entry_id INT NOT NULL,
  mastery TINYINT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  INDEX (user_id)
);

CREATE TABLE game_results (
  id INT NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  game TINYINT NOT NULL,
  score INT NOT NULL,
  timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  INDEX (user_id)
);

CREATE TABLE mad_minute_results (
  id INT NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  game_id INT NOT NULL,
  correct_answers TINYINT NOT NULL,
  wrong_answers TINYINT NOT NULL,
  timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  INDEX (user_id)
);

CREATE TABLE scribe_questions (
  id INT NOT NULL AUTO_INCREMENT,
  chinese VARCHAR(255) NOT NULL,
  english VARCHAR(255) NOT NULL,
  other_english_answers TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE TABLE scribe_results (
  id INT NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  game_id INT NOT NULL,
  correct_answers TINYINT NOT NULL,
  wrong_answers TINYINT NOT NULL,
  correct_question_ids VARCHAR(255) NOT NULL,
  wrong_question_ids VARCHAR(255) NOT NULL,
  timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  INDEX (user_id)
);

CREATE TABLE invitations (
  id INT NOT NULL AUTO_INCREMENT,
  email VARCHAR(255) NOT NULL,
  timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE TABLE writer_answers (
  id INT NOT NULL AUTO_INCREMENT,
  name CHAR(36) NOT NULL,
  timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

-- $2b$12$vdNVmXFt/rJ1csHcYvW1SeYXwXb.PLTGgjy0MIAIkCbhcLu2g9E0q is a bcrypt hash of "this is my password"
INSERT INTO users (username, email, password, groups, settings, pending_email, saved_entry_ids) VALUES ("admin", "admin@storytime.works", "$2b$12$vdNVmXFt/rJ1csHcYvW1SeYXwXb.PLTGgjy0MIAIkCbhcLu2g9E0q", "[1]", "{}", NULL, "[]");
INSERT INTO users (username, email, password, groups, settings, pending_email, saved_entry_ids) VALUES ("user", "user@storytime.works", "$2b$12$vdNVmXFt/rJ1csHcYvW1SeYXwXb.PLTGgjy0MIAIkCbhcLu2g9E0q", "[]", "{}", NULL, "[]");

INSERT INTO entries (chinese, english, pinyin, translations, categories) VALUES ("我", "I, me", "wǒ", "[]", "[]");

INSERT INTO stories (name, description, passage_ids, position) VALUES ("Basics", "Sarah introduces herself to the reader.", "[1]", 1);
INSERT INTO passages (name, description, story_id, data, new_words, notes) VALUES ("Hello", "Sarah introduces herself to the reader.", 1, '{"components": []}', "[]", "# Grammar Notes");
