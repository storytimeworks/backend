import os
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

@application.route("/vocabulary")
def vocabulary():
    cursor = sql.connection.cursor()
    cursor.execute("SELECT * FROM chinese_vocabulary WHERE pinyin LIKE \"%" + request.args.get("q") + "%\" collate utf8_general_ci")
    result = cursor.fetchall()
    translations = []

    for row in result:
        translation = Translation(row)
        translations.append(translation.dict())

    return jsonify(translations)

@application.route("/vocabulary/<vocabulary_id>")
def vocabulary_specific(vocabulary_id):
    cursor = sql.connection.cursor()
    cursor.execute("SELECT * FROM chinese_vocabulary WHERE id = %s", vocabulary_id)
    data = Translation(cursor.fetchall()[0]).dict()
    return jsonify(data)

if __name__ == "__main__":
    application.debug = True
    application.run()
