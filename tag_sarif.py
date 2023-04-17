#!/usr/bin/env python3

"""
Tag rules in SARIF files, to help with filtering in GitHub Code Scanning.

Copyright (C) GitHub 2022
"""

from enum import Enum
import json
import argparse
import logging
import sys
from typing import Any

LOG = logging.getLogger(__name__)


def add_tags(object, tags: list[str]) -> None:
    """Add tags to a SARIF object."""
    if "properties" not in object:
        object["properties"] = {}

    if "tags" not in object["properties"]:
        object["properties"]["tags"] = []

    object["properties"]["tags"].extend(tags)


def tag_sarif(sarif: dict[str, Any], custom_tags: list[str]) -> dict[str, Any]:
    """
    Tag SARIF file.

    - Add custom tag(s) to each rule ID, to help with filtering in Code Scanning in GitHub Advanced Security 
    """
    try:
        for run in sarif["runs"]:
            if "tool" in run:
                if "driver" in run["tool"]:
                    if "rules" in run["tool"]["driver"]:
                        for rule in run["tool"]["driver"]["rules"]:
                            add_tags(rule, custom_tags)
                if "extensions" in run["tool"]:
                    for extension in run["tool"]["extensions"]:
                        if "rules" in extension:
                            for rule in extension["rules"]:
                                add_tags(rule, custom_tags)
    except KeyError as err:
        LOG.error("SARIF structure error: %s", err)
    return sarif


def add_args(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the parser."""
    parser.add_argument('--custom-tags', '-t', type=lambda arg: arg.split(","), help='List of custom tags to add to each rule')
    parser.add_argument('input_sarif', help='SARIF file to edit')
    parser.add_argument('--output-sarif', '-o', help='SARIF file to write')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug logging')


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Edit SARIF file tags.")
    add_args(parser)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.debug:
        LOG.setLevel(logging.DEBUG)

    with open(args.input_sarif, 'r') as in_f:
        try:
            data = in_f.read()
            sarif = json.loads(data)
        except json.JSONDecodeError as err:
            LOG.error("Error parsing SARIF file as JSON (%s): %s", args.sarif, err)
            LOG.error("Could not parse as JSON: %s", data)
            return
        # NOTE: closes STDOUT after the context manager if no output file is specified
        with open(args.output_sarif, 'w') if args.output_sarif else sys.stdout as out_f:
            print(json.dumps(
                tag_sarif(
                    sarif,
                    args.custom_tags if args.custom_tags else []
                ), indent=2)
                , file=out_f)


if __name__ == "__main__":
    main()
