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

@application.route("/vocabulary/entries", methods=["GET"])
def get_entries():
    query = "%" + request.args.get("q") + "%"
    
    cursor = sql.connection.cursor()
    cursor.execute("SELECT * FROM chinese_entries WHERE chinese LIKE %s OR english LIKE %s OR pinyin LIKE %s", (query, query, query,))
    entries = [Entry(row).dict() for row in cursor.fetchall()]
    
    return jsonify(entries)

@application.route("/vocabulary/entries/<entry_id>", methods=["GET"])
def get_entry_specific(entry_id):
    cursor = sql.connection.cursor()
    cursor.execute("SELECT * FROM chinese_entries WHERE id = %s", (entry_id,))
    entry = Entry(cursor.fetchall()[0])
    
    cursor.execute("SELECT * FROM chinese_translations WHERE id IN (%s) ORDER BY FIELD(id, %s)", (entry.translation_ids, entry.translation_ids,))
    entry.translations = [Translation(row).dict() for row in cursor.fetchall()]
    
    return jsonify(entry.dict())

@application.route("/vocabulary/entries", methods=["POST"])
def create_entry():
    chinese = request.form["chinese"]
    english = request.form["english"]
    pinyin = request.form["pinyin"]
    source_is_chinese = request.form["source_is_chinese"]

    cursor = sql.connection.cursor()
    cursor.execute("INSERT INTO chinese_vocabulary (chinese, english, pinyin, source_is_chinese, translations) VALUES (%s, %s, %s, %s, \"\")", (chinese, english, pinyin, source_is_chinese,))
    sql.connection.commit()
    cursor.close()

    return ("", 204)

@application.route("/vocabulary/entries/<entry_id>", methods=["PUT"])
def update_entry(entry_id):
    key = list(request.json.keys())[0]
    value = request.json[key]
    
    cursor = sql.connection.cursor()
    cursor.execute("UPDATE chinese_entries SET " + key + " = %s WHERE id = %s", (value, entry_id,))
    sql.connection.commit()
    
    return get_entry_specific(entry_id)

@application.route("/vocabulary/translations/<translation_id>", methods=["GET"])
def get_translation_specific(translation_id):
    cursor = sql.connection.cursor()
    cursor.execute("SELECT * FROM chinese_translations WHERE id = %s", (translation_id,))
    translation = Translation(cursor.fetchall()[0])
    return jsonify(translation.dict())

@application.route("/vocabulary/translations/<translation_id>", methods=["PUT"])
def update_translation(translation_id):
    key = list(request.json.keys())[0]
    value = request.json[key]
    
    if key == "chineseSentence": key = "chinese_sentence"
    elif key == "englishSentence": key = "english_sentence"
    
    cursor = sql.connection.cursor()
    cursor.execute("UPDATE chinese_translations SET " + key + " = %s WHERE id = %s", (value, translation_id,))
    sql.connection.commit()
    
    return get_translation_specific(translation_id)

@application.route("/vocabulary/sentences")
def get_sentences():
    query = "%" + request.args.get("q") + "%"

    cursor = sql.connection.cursor()
    cursor.execute("SELECT * FROM chinese_sentences WHERE chinese LIKE %s LIMIT 10", (query,))
    result = cursor.fetchall()
    sentences = []

    for row in result:
        sentence = Sentence(row)
        sentences.append(sentence.dict())

    return jsonify(sentences)

if __name__ == "__main__":
    application.debug = True
    application.run()
