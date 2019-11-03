import json
import unidecode
from datetime import datetime
import hashlib
from functools import partial


def open_json(json_file):
    with open(json_file, "r") as f:
        lines = f.readlines()
    return [json.loads(line) for line in lines]


def write_json(json_file, lines):
    with open(json_file, "w+") as f:
        for line in lines:
            f.write(json.dumps(line) + "\n")


def remove_accent(_str):
    return unidecode.unidecode(u"{}".format(_str))


def md5(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 4096), b''):
            d.update(buf)
            break
    return d.hexdigest()


def duration_to_int(duration):
    split = duration.split(" h ")
    if len(split) == 1:
        if duration.endswith("h"):
            return int(duration.replace(" h", "")) * 60
        return int(split[0].replace(" ", "").replace("min", ""))
    else:
        hours = int(split[0].replace(" ", ""))
        minutes = int(split[1].replace(" ", "").replace("min", ""))
        return 60 * hours + minutes


def search_files(files, name):
    if not name:
        return files
    new_files = []
    for file in files:
        name = remove_accent(name.lower())
        if name in remove_accent(
                file["name"].lower()) or name in remove_accent(
                    file["director"].lower()):
            new_files.append(file)
    return new_files


def order_files(files):
    return sorted(files,
                  key=lambda x: (
                      x["director"].split(" ")[-1],
                      x["director"],
                      datetime.strptime(x["date"], "%Y-%m-%d"),
                  ))
