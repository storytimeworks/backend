import json, os
from sentence import Sentence
from entry import Entry

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL

application = Flask(__name__)

cors = CORS(application)
application.config["CORS_HEADERS"] = "Content-Type"

db = SQLAlchemy(application)

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
    cursor.execute("SELECT * FROM chinese_entries WHERE (chinese LIKE %s OR pinyin LIKE %s AND source_is_chinese = 1) OR (english LIKE %s AND source_is_chinese = 0)", (query, query, query,))
    entries = [Entry(row).dict() for row in cursor.fetchall()]

    return jsonify(entries)

@application.route("/vocabulary/entries/<entry_id>", methods=["GET"])
def get_entry_specific(entry_id):
    cursor = sql.connection.cursor()
    cursor.execute("SELECT * FROM chinese_entries WHERE id = %s", (entry_id,))
    entry = Entry(cursor.fetchall()[0])
    return jsonify(entry.dict())

@application.route("/vocabulary/entries", methods=["POST"])
def create_entry():
    chinese = request.json["chinese"]
    english = request.json["english"]
    pinyin = request.json["pinyin"]
    source_is_chinese = request.json["source_is_chinese"]
    translations = json.dumps(request.json["translations"])
    categories = json.dumps(request.json["categories"])

    cursor = sql.connection.cursor()
    cursor.execute("INSERT INTO chinese_entries (chinese, english, pinyin, source_is_chinese, translations, categories) VALUES (%s, %s, %s, %s, %s, %s)", (chinese, english, pinyin, source_is_chinese, translations, categories,))
    sql.connection.commit()

    entry_id = cursor.lastrowid
    cursor.close()

    return get_entry_specific(entry_id)

@application.route("/vocabulary/entries/<entry_id>", methods=["PUT"])
def update_entry(entry_id):
    key = list(request.json.keys())[0]
    value = request.json[key]

    if key == "translations":
        value = json.dumps(value)

    cursor = sql.connection.cursor()
    cursor.execute("UPDATE chinese_entries SET " + key + " = %s WHERE id = %s", (value, entry_id,))
    sql.connection.commit()

    return get_entry_specific(entry_id)

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
