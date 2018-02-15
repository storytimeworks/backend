from flask import Flask, jsonify
from flask_cors import CORS, cross_origin

application = Flask(__name__)
cors = CORS(application)
application.config["CORS_HEADERS"] = "Content-Type"

@application.route("/vocabulary")
def vocabulary():
    data = {
        "source": "你好",
        "pinyin": "nǐ hǎo",
        "translation": "hello",
        "definitions": [
            {
                "meaning": "(greeting)",
                "source_sentence": "{你好}！我是沙拉。",
                "target_sentence": "{Hello}! I'm Sarah."
            }
        ]
    }

    return jsonify(data)

if __name__ == "__main__":
    application.debug = True
    application.run()
