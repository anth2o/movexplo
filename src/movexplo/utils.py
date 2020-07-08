import hashlib
import json
import logging
from collections import defaultdict
from datetime import datetime
from functools import partial
from typing import Dict, List

import unidecode


def read_json(json_file: str) -> List[Dict]:
    with open(json_file, "r") as f:
        lines = f.readlines()
    return [json.loads(line) for line in lines]


def write_json(json_file: str, lines: List[Dict]):
    with open(json_file, "w+") as f:
        for line in lines:
            f.write(json.dumps(line) + "\n")


def remove_special_characters(_str: str) -> str:
    return unidecode.unidecode(u"{}".format(_str))


def get_logger(name: str, level=logging.INFO):
    logger = logging.getLogger(name)
    logging.basicConfig(level=level)
    return logger


def md5(filename: str) -> str:
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 4096), b''):
            d.update(buf)
            break
    return d.hexdigest()


def duration_to_int(duration: str) -> int:
    split = duration.split(" h ")
    if len(split) == 1:
        if duration.endswith("h"):
            return int(duration.replace(" h", "")) * 60
        return int(split[0].replace(" ", "").replace("min", ""))
    else:
        hours = int(split[0].replace(" ", ""))
        minutes = int(split[1].replace(" ", "").replace("min", ""))
        return 60 * hours + minutes


def search_files(files: List[Dict], name: str) -> List[Dict]:
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


def filter_files(files: List[Dict], genre: str = None) -> List[Dict]:
    files = [file for file in files if not file.get("ignore")]
    if genre is not None:
        genre = remove_special_characters(genre).lower()
        files = [
            file for file in files
            if genre in [remove_special_characters(g).lower() for g in file.get("genres", [])]
        ]
    return files


def order_files(files: List[Dict]) -> List[Dict]:
    return sorted(
        files,
        key=lambda x: (
            x.get("director", "z").split(" ")[-1],  # last name
            x.get("director", "z"),
            datetime.strptime(x.get("date", "2100-01-01"), "%Y-%m-%d"),
        )
    )


def group_by(files: List[Dict], field_name: str) -> Dict[str, List[Dict]]:
    field_to_files = defaultdict(list)
    for file in files:
        fields = file.get(field_name, [])
        for field in fields:
            field = remove_special_characters(field).lower()
            field_to_files[field].append(file)
    return dict(field_to_files)
