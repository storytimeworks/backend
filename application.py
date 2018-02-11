from flask import Flask, render_template

# EB looks for an 'application' callable by default.
application = Flask(__name__,
                    static_folder="build/static",
                    template_folder="build")

# add a rule for the index page.
application.add_url_rule("/", "index", (lambda: render_template("index.html")))

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
