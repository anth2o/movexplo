import hashlib
import json
import logging
from datetime import datetime
from functools import partial

import unidecode


def read_json(json_file):
    with open(json_file, "r") as f:
        lines = f.readlines()
    return [json.loads(line) for line in lines]


def write_json(json_file, lines):
    with open(json_file, "w+") as f:
        for line in lines:
            f.write(json.dumps(line) + "\n")


def remove_special_characters(_str):
    return unidecode.unidecode(u"{}".format(_str))


def get_logger(name, level=logging.INFO):
    logger = logging.getLogger()
    logging.basicConfig(level=level)
    return logger


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
        name = remove_special_characters(name.lower())
        if name in remove_special_characters(
            file.get("name", "").lower()
        ) or name in remove_special_characters(file.get("director", "").lower()):
            new_files.append(file)
    return new_files


def order_files(files, key=None):
    files = [file for file in files if not file.get("ignore")]
    if key is not None and key != "director":
        files_with_key = [file for file in files if file.get(key, "TOFIND") != "TOFIND"]
        return sorted(files_with_key, key=lambda x: x[key], reverse=key in ["added_on"]) + [
            file for file in files if file.get(key, "TOFIND") == "TOFIND"
        ]
    return sorted(
        files,
        key=lambda x: (
            x.get("director", "z").split(" ")[-1],  # last name
            x.get("director", "z"),
            datetime.strptime(x.get("date", "2100-01-01"), "%Y-%m-%d"),
        )
    )
