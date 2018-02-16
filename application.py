import json, os
from normalize import normalize
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
    query = "%" + normalize(request.args.get("q")) + "%"

    cursor = sql.connection.cursor()
    cursor.execute("SELECT * FROM chinese_vocabulary WHERE pinyin LIKE %s OR source LIKE %s OR target LIKE %s", (query, query, query,))
    result = cursor.fetchall()
    translations = []

    for row in result:
        translation = Translation(row)
        translations.append(translation.dict())

    return jsonify(translations)

@application.route("/vocabulary", methods=["POST"])
def create_vocabulary():
    source = request.form["source"]
    target = request.form["target"]
    pinyin = request.form["pinyin"]
    meaning = request.form["meaning"]
    source_sentence = request.form["source_sentence"]
    target_sentence = request.form["target_sentence"]

    translation = [{
        "meaning": meaning,
        "source_sentence": source_sentence,
        "target_sentence": target_sentence
    }]

    translation_json = json.dumps(translation, ensure_ascii=False)

    cursor = sql.connection.cursor()
    cursor.execute("INSERT INTO chinese_vocabulary (source, target, pinyin, definitions) VALUES (%s, %s, %s, %s)", (source, target, pinyin, translation_json,))
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
