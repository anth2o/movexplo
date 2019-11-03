from flask import flash, render_template, request, redirect, Flask
import os
import unidecode

from utils import open_json, remove_accent, search_files, order_files

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    files = open_json("data.json")
    search = request.form
    if request.method == 'POST':
        files = search_files(files, search["title"])
    files = order_files(files)
    return render_template("template.html", data=files)


if __name__ == "__main__":
    debug = False
    if os.environ.get("ENV", "PROD") == "DEV":
        app.jinja_env.auto_reload = True
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        debug = True
    app.run(threaded=True, port=5000, debug=debug)
