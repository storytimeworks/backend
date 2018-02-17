import json, os
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
    cursor.execute("SELECT * FROM chinese_vocabulary WHERE pinyin LIKE %s OR chinese LIKE %s OR english LIKE %s", (query, query, query,))
    result = cursor.fetchall()
    translations = []

    for row in result:
        translation = Translation(row)
        translations.append(translation.dict())

    return jsonify(translations)

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

@application.route("/vocabulary/<vocabulary_id>")
def vocabulary_specific(vocabulary_id):
    cursor = sql.connection.cursor()
    cursor.execute("SELECT * FROM chinese_vocabulary WHERE id = %s", (vocabulary_id,))
    data = Translation(cursor.fetchall()[0]).dict()
    return jsonify(data)

if __name__ == "__main__":
    application.debug = True
    application.run()
