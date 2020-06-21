import argparse
import os
from pathlib import Path
from typing import Dict, List

from movexplo.constants import TOFIND, VIDEO_EXTENSIONS
from movexplo.scrapper import (FIELD_TO_METHOD, get_link_from_file, get_soup_from_url)
from movexplo.utils import get_logger, md5, open_json, write_json

logger = get_logger("writer")


def get_files_info(input_file: str, input_folder: str) -> List[Dict]:
    if input_file is None and input_folder is None:
        raise ValueError("You must define at least input_file or input_folder")

    if input_file is None:
        return list_files_info_from_folder(input_folder)

    input_path = Path(input_file)
    if not input_path.is_file():
        raise FileNotFoundError(input_path)

    files_info = open_json(input_path)
    if input_folder is None:
        return files_info

    files_info_from_folder = list_files_info_from_folder(Path(input_folder))
    for file_info_from_folder in files_info_from_folder:
        updated = False
        for i in range(len(files_info)):
            if files_info[i]["md5"] == file_info_from_folder["md5"]:
                file_info_from_folder.pop("name")
                files_info[i].update(file_info_from_folder)
                updated = True
                break
        if not updated:
            logger.warning("{} is new".format(file_info_from_folder["name"]))
            files_info.append(file_info_from_folder)
    return files_info


def list_files_info_from_folder(folder: str) -> List[Dict]:
    folder = Path(folder)
    folders = [x for x in folder.iterdir() if x.is_dir()]
    files_info = []
    for sub_folder in folders:
        sub_folder_files_info = list_files_info_from_folder(sub_folder)
        if len(sub_folder_files_info) == 1:  # unique movie in folder
            if sub_folder_files_info[0].get("renamed"):
                # this happens if there is folder/single_folder/single_movie.mp4
                # we want to keep single_folder as a name in this situation
                sub_folder_files_info[0].pop("renamed", None)
            else:
                # this happens if there is folder/single_movie.mp4
                # we want to keep folder as a name in this situation
                sub_folder_files_info[0]["name"] = sub_folder.name
                sub_folder_files_info[0]["renamed"] = True
        files_info += sub_folder_files_info
    video_files = [
        x for x in folder.iterdir()
        if x.name.split(".")[-1] in VIDEO_EXTENSIONS and x.name[0] != "."
    ]
    files_info += [
        {
            "name": format_video_file_name(x.name),
            "size": x.stat().st_size,
            "md5": md5(x)
        } for x in video_files
    ]
    return files_info


def format_video_file_name(video_file_name: str) -> str:
    video_file_name = str(video_file_name)
    for extension in VIDEO_EXTENSIONS:
        if video_file_name.endswith(extension):
            video_file_name = "".join(video_file_name.rsplit(".{}".format(extension), 1))
            # replace last occurence
            break
    return video_file_name


def enrich_files(files_info: List[Dict], force_enrich: bool = False) -> List[Dict]:
    for file_info in files_info:
        if force_enrich or not file_info.get("enriched", False):
            logger.info("Enriching {}".format(file_info["name"]))
            file_info = enrich_file(file_info)
    return files_info


def enrich_file(file_info: Dict):
    if file_info.get("link") is None:
        file_info["link"] = get_link_from_file(file_info)
    soup = get_soup_from_url(file_info["link"])
    for field, method in FIELD_TO_METHOD.items():
        if not file_info.get(field):
            try:
                file_info[field] = method(soup)
            except (IndexError, ValueError, AttributeError) as e:
                logger.warning("No {} found for {}".format(field, file_info["link"]))
                logger.error(e)
                file_info[field] = TOFIND
    file_info["enriched"] = True
    return file_info


def get_args():
    parser = argparse.ArgumentParser(description='Resume a folder or enrich a file inside a json')
    parser.add_argument(
        '--output_file',
        default="data.json",
        type=str,
        help='the json file where to write the results'
    )
    parser.add_argument('--input_folder', default=None, type=str, help='the folder to process')
    parser.add_argument('--input_file', default=None, type=str, help='the file to enrich')
    parser.add_argument(
        '--enrich',
        dest='enrich',
        action='store_true',
        help='add this flag to enrich the data with external database'
    )
    parser.set_defaults(enrich=False)
    parser.add_argument(
        '--force_enrich',
        dest='force_enrich',
        action='store_true',
        help='add this flag to force enrich'
    )
    parser.set_defaults(enrich=False)
    args = parser.parse_args()
    if args.input_file is None and args.input_folder is None:
        raise ValueError("You must define at least input_file or input_folder")
    return args


if __name__ == "__main__":
    args = get_args()
    output_path = Path(args.output_file)
    if output_path.is_file() and Path(args.input_file) != output_path:
        raise FileExistsError(output_path)
    files_info = get_files_info(args.input_file, args.input_folder)
    if args.enrich or args.force_enrich:
        files_info = enrich_files(files_info, args.force_enrich)

    write_json(args.output_file, files_info)
