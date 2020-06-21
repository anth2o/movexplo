import os

from flask import Flask, render_template, request

from movexplo.utils import open_json, order_files, search_files

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    files = open_json("data.json")
    search = request.form
    if request.method == 'POST':
        files = search_files(files, search["title"])
    files = order_files(files)
    return render_template("template.html", data=files)
