from writer import open_json, write_json
import argparse
import logging

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Resume a folder or enrich a file inside a json')
    parser.add_argument('--md5_file',
                        type=str, help='the json file where the md5 are present')
    parser.add_argument('--enriched_file',
                        type=str, help='the file with additional data')
    args = parser.parse_args()

    md5_lines = open_json(args.md5_file)
    enriched_lines = open_json(args.enriched_file)
    for enriched_line in enriched_lines:
        md5_list = [md5_line["md5"]
                    for md5_line in md5_lines if md5_line["name"] == enriched_line["name"]]
        if len(md5_list):
            enriched_line["md5"] = md5_list[0]
        else:
            enriched_line["md5"] = "TOFIND"
            logger.warning("No md5 found for {}".format(enriched_line["name"]))

    write_json(args.enriched_file, enriched_lines)
