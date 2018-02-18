import json, os
from sentence import Sentence
from entry import Entry
from translation import Translation

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_mysqldb import MySQL

application = Flask(__name__)

cors = CORS(application)
application.config["CORS_HEADERS"] = "Content-Type"

sql = MySQL()
application.config["MYSQL_USER"] = os.environ["RDS_USERNAME"]
application.config["MYSQL_PASSWORD"] = os.environ["RDS_PASSWORD"]
application.config["MYSQL_DB"] = os.environ["RDS_DB_NAME"]
application.config["MYSQL_HOST"] = os.environ["RDS_HOSTNAME"]
sql.init_app(application)

@application.route("/vocabulary", methods=["GET"])
def vocabulary():
    query = "%" + request.args.get("q") + "%"

    cursor = sql.connection.cursor()
    cursor.execute("SELECT * FROM chinese_entries WHERE chinese LIKE %s OR english LIKE %s OR pinyin LIKE %s", (query, query, query,))
    result = cursor.fetchall()
    entries = []

    for row in result:
        entry = Entry(row)
        entries.append(entry.dict())

    return jsonify(entries)

@application.route("/vocabulary/<vocabulary_id>")
def vocabulary_specific(vocabulary_id):
    cursor = sql.connection.cursor()
    cursor.execute("SELECT * FROM chinese_entries WHERE id = %s", (vocabulary_id,))
    entry = Entry(cursor.fetchall()[0])
    
    cursor.execute("SELECT * FROM chinese_translations WHERE id IN (%s) ORDER BY FIELD(id, %s)", (entry.translation_ids, entry.translation_ids,))
    result = cursor.fetchall()
    translations = []
    
    for row in result:
        translation = Translation(row)
        translations.append(translation.dict())
    
    entry.translations = translations
    return jsonify(entry.dict())

@application.route("/vocabulary", methods=["POST"])
def create_vocabulary():
    chinese = request.form["chinese"]
    english = request.form["english"]
    pinyin = request.form["pinyin"]
    meaning = request.form["meaning"]
    chinese_sentence = request.form["chinese_sentence"]
    english_sentence = request.form["english_sentence"]

    translation = [{
        "meaning": meaning,
        "chinese_sentence": chinese_sentence,
        "english_sentence": english_sentence
    }]

    translation_json = json.dumps(translation, ensure_ascii=False)

    cursor = sql.connection.cursor()
    cursor.execute("INSERT INTO chinese_vocabulary (chinese, english, pinyin, definitions) VALUES (%s, %s, %s, %s)", (chinese, english, pinyin, translation_json,))
    sql.connection.commit()
    cursor.close()

    return ("", 204)

@application.route("/sentences")
def sentences():
    query = "%" + request.args.get("q") + "%"
    
    cursor = sql.connection.cursor()
    cursor.execute("SELECT * FROM chinese_sentences WHERE chinese LIKE %s OR english LIKE %s LIMIT 10", (query, query,))
    result = cursor.fetchall()
    sentences = []

    for row in result:
        sentence = Sentence(row)
        sentences.append(sentence.dict())

    return jsonify(sentences)

if __name__ == "__main__":
    application.debug = True
    application.run()
