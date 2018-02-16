CREATE TABLE chinese_vocabulary (
  id INT NOT NULL AUTO_INCREMENT,
  source VARCHAR(12) NOT NULL,
  target VARCHAR(24) NOT NULL,
  pinyin VARCHAR(24) NOT NULL,
  definitions TEXT NOT NULL,
  PRIMARY KEY (id)
) DEFAULT CHARSET=utf8;

INSERT INTO chinese_vocabulary (source, target, pinyin, definitions) VALUES ("你好", "hello", "nǐ hǎo", "[{\"meaning\": \"(greeting)\", \"source_sentence\": \"{你好}！我说啥啦。\", \"target_sentence\": \"{Hello}! I'm Sarah.\"}]");
INSERT INTO chinese_vocabulary (source, target, pinyin, definitions) VALUES ("女孩", "girl", "nǚ hái", "[{\"meaning\":\"(child)\",\"source_sentence\":\"沙拉是{女孩}。\",\"target_sentence\":\"Sarah is a {girl}.\"}]");
