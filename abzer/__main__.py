#!/usr/bin/env python
# coding: utf-8
# Copyright © 2016 Wieland Hoffmann
# License: MIT, see LICENSE for details
import argparse
import asyncio
import configparser
import logging


from . import const
from .abzer import Abzer
from os import walk
from os.path import isfile, join


def collect_files(dir):
    for dirpath, dirnames, filenames in walk(dir):
        for filename in filenames:
            yield join(dir, dirpath, filename)


def read_config(filename):
    """
    :param filename:
    """
    parser = configparser.ConfigParser(defaults=const.DEFAULTS)
    parser.read([filename])
    logging.debug("%s", parser["essentia"])
    return parser


def main():
    parser = argparse.ArgumentParser(prog="abzer",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)  # noqa
    parser.add_argument("filenames", metavar="FILENAME", nargs="+")
    parser.add_argument("-c", "--config",
                        help="The path to the config file.",
                        default=const.DEFAULT_CONFIG_PATH)
    parser.add_argument("-v", "--verbose",
                        help="Be more verbose.",
                        action="store_true",
                        default=False)
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    try:
        config = read_config(args.config)
    except configparser.Error:
        logging.exception("Could not read the configuration file.")
        exit(1)

    files = []

    for name in args.filenames:
        if isfile(name):
            files.append(name)
        else:
            files.extend(collect_files(name))

    loop = asyncio.get_event_loop()
    abzer = Abzer(config.get("essentia", "path"),
                  config.get("essentia", "profile"),
                  files)
    loop.run_until_complete(abzer.run())
    abzer.session.close()
    loop.close()

if __name__ == "__main__":
    main()
