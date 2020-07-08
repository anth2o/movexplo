import os

from flask import Flask, redirect, render_template, request

from movexplo.utils import filter_files, order_files, read_json, search_files, group_by

app = Flask(__name__)
BASEDIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASEDIR, "static/data.json")


@app.route("/")
def index():
    return redirect("/movies")


@app.route("/movies/<genre>", methods=["GET", "POST"])
def movies(genre=None):
    files = read_json(DATA_PATH)
    search = request.form
    files = filter_files(files, genre=genre)
    if request.method == "POST":
        files = search_files(files, search["title"])
    files = order_files(files)
    return render_template("movies.html", movies=files)


@app.route("/genres", methods=["GET", "POST"])
def genres():
    files = read_json(DATA_PATH)
    files = filter_files(files)
    genre_to_files = group_by(files, "genres")
    genre_to_files = {genre: order_files(files) for genre, files in genre_to_files.items()}
    print(genre_to_files["road movie"])
    if request.method == "POST":
        for genre in genre_to_files:
            if genre in request.form:
                print(genre)
                return redirect(f"/movies/{genre.lower()}")
    return render_template("genres.html", data=genre_to_files)


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
