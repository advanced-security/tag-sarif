#!/usr/bin/env python3

"""Edit SARIF files.

Copyright (C) GitHub 2022
"""

from enum import Enum
import json
import argparse
import logging
from typing import Any

LOG = logging.getLogger(__name__)


class SeverityLevel(str, Enum):
    """Sub-severity level for a SARIF result."""
    CRITICAL = "critical"
    HIGH = "high"
    LOW = "low"


def edit_sarif(sarif: dict[str, Any], severity_list: list[tuple[str, str]], custom_tags: list[str]) -> dict[str, Any]:
    """Edit SARIF file.

    - Replace sub-severity with passed in level for matching rule ID.
    - Add custom tag(s) to each rule ID, to help with filtering in Code Scanning in GitHub Advanced Security 
    """
    try:
        for run in sarif["runs"]:
            for rule in run["tool"]["driver"]["rules"]:
                for rule_id, severity in severity_list:
                    # TODO: glob match on the rule ID
                    if rule["id"] == rule_id.strip():
                        rule["properties"]["sub-severity"] = SeverityLevel(severity.strip())
                        LOG.debug("Rule %s sub-severity set to %s", rule_id, severity)

                # add custom tags to each rule
                if "properties" not in rule:
                    rule["properties"] = {}

                if "tags" not in rule["properties"]:
                    rule["properties"]["tags"] = []

                rule["properties"]["tags"].extend(custom_tags)
    except KeyError as err:
        LOG.error("SARIF structure error: %s", err)
    return sarif


def add_args(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the parser."""
    parser.add_argument(
        '--rule_id_severity', '-r',
        type=lambda arg: arg.split(",", maxsplit=2), nargs='+',
        help='List of Rule IDs to edit, with sub-severity, comma-separated, e.g. py/code-injection,low'
    )
    parser.add_argument('--custom-tags', '-t', nargs='+', help='List of custom tags to add to each rule')
    parser.add_argument('sarif', help='SARIF file to edit')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug logging')


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Edit SARIF file sub-severity level for named rules.")
    add_args(parser)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.debug:
        LOG.setLevel(logging.DEBUG)

    with open(args.sarif, 'r') as f:
        sarif = json.load(f)
        print(json.dumps(
            edit_sarif(
                sarif,
                args.rule_id_severity if args.rule_id_severity else [],
                args.custom_tags if args.custom_tags else []
            )
            , indent=2
        ))


if __name__ == "__main__":
    main()
