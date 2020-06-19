from pathlib import Path
import argparse
import os
import logging

from scrapper import get_link_from_file, get_soup_from_url, FIELD_TO_METHOD, TOFIND
from utils import open_json, write_json, md5

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

VIDEO_EXTENSIONS = ["mp4", "mkv", "avi", "m4v"]


def list_files_info_from_folder(folder):
    folders = [x for x in folder.iterdir() if x.is_dir()]
    files_info = []
    for sub_folder in folders:
        sub_folder_files_info = list_files_info_from_folder(sub_folder)
        if len(sub_folder_files_info) == 1:  # unique movie in folder
            if "renamed" in sub_folder_files_info[0] and sub_folder_files_info[0]["renamed"]:
                sub_folder_files_info[0].pop("renamed", None)
            else:
                sub_folder_files_info[0]["name"] = sub_folder.name
                sub_folder_files_info[0]["renamed"] = True
        files_info += sub_folder_files_info
    video_files = [x for x in folder.iterdir() if x.name.split(".")
                   [-1] in VIDEO_EXTENSIONS and x.name[0] != "."]
    files_info += [{"name": format_video_file_name(x.name), "size": x.stat().st_size, "md5": md5(x)}
                   for x in video_files]
    del video_files
    return files_info


def format_video_file_name(video_file_name):
    video_file_name = str(video_file_name)
    for extension in VIDEO_EXTENSIONS:
        video_file_name = video_file_name.replace(".{}".format(extension), "")
    return video_file_name


def enrich_file(file):
    if "link" not in file or file["link"] is None:
        file = get_link_from_file(file)
    soup = get_soup_from_url(file["link"])
    for field, method in FIELD_TO_METHOD.items():
        if field not in file or file[field] is None:
            try:
                file[field] = method(soup)
            except (IndexError, ValueError) as e:
                logger.warning(
                    "No {} found for {}".format(field, file["link"]))
                logger.error(e)
                file[field] = TOFIND
    file["enriched"] = True
    return file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Resume a folder or enrich a file inside a json')
    parser.add_argument('--output_file', default="data.json",
                        type=str, help='the json file where to write the results')
    parser.add_argument('--input_folder', default=None,
                        type=str, help='the folder to process')
    parser.add_argument('--input_file', default=None,
                        type=str, help='the file to enrich')
    parser.add_argument('--enrich', dest='enrich', action='store_true',
                        help='add this flag to enrich the data with external database')
    parser.set_defaults(enrich=False)
    parser.add_argument('--force_enriche', dest='force_enrich', action='store_true',
                        help='add this flag to force enrich')
    parser.set_defaults(enrich=False)
    args = parser.parse_args()

    output_path = Path(args.output_file)
    if output_path.is_file() and Path(args.input_file) != output_path:
        raise FileExistsError(output_path)

    if args.input_file is None:
        if args.input_folder is None:
            args.input_folder = "/Users/antoine/Movies"
        input_path = Path(args.input_folder)
        files_info = list_files_info_from_folder(input_path)
    else:
        input_path = Path(args.input_file)
        if not input_path.is_file():
            raise FileNotFoundError(input_path)
        files_info = open_json(input_path)
        if args.input_folder is not None:
            files_info_from_folder = list_files_info_from_folder(
                Path(args.input_folder))
            for file_info_from_folder in files_info_from_folder:
                updated = False
                for i in range(len(files_info)):
                    if files_info[i]["md5"] == file_info_from_folder["md5"]:
                        file_info_from_folder.pop("name")
                        files_info[i].update(file_info_from_folder)
                        updated = True
                        break
                if not updated:
                    logger.warning("{} is new".format(
                        file_info_from_folder["name"]))
                    files_info.append(file_info_from_folder)

    if args.enrich or args.force_enrich:
        for file_info in files_info:
            if args.force_enrich or "enriched" not in file_info or not file_info["enriched"]:
                logger.info("Enriching {}".format(file_info["name"]))
                file_info = enrich_file(file_info)

    write_json(args.output_file, files_info)
