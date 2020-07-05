import os

from flask import Flask, render_template, request

from movexplo.utils import read_json, order_files, search_files

app = Flask(__name__)
BASEDIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASEDIR, 'static/data.json')


@app.route('/', methods=['GET', 'POST'])
def index():
    files = read_json(DATA_PATH)
    search = request.form
    if request.method == 'POST':
        files = search_files(files, search["title"])
    files = order_files(files)
    return render_template("template.html", data=files)
