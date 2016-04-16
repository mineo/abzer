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
from os import cpu_count, walk
from os.path import isfile, join
from sys import exit


def collect_files(dir):
    for dirpath, dirnames, filenames in walk(dir):
        for filename in filenames:
            yield join(dir, dirpath, filename)


def make_argparser():
    parser = argparse.ArgumentParser(prog="abzer",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)  # noqa
    parser.add_argument("filenames", metavar="FILENAME", nargs="+")
    parser.add_argument("-c", "--config",
                        help="The path to the config file.",
                        default=const.DEFAULT_CONFIG_PATH)
    parser.add_argument("-p", "--processes",
                        help="The number of processes to use for analyzing files.",  # noqa
                        default=cpu_count(),
                        type=int)
    parser.add_argument("-v", "--verbose",
                        help="Be more verbose.",
                        action="store_true",
                        default=False)
    return parser


def read_config(filename):
    """
    :param filename:
    """
    parser = configparser.ConfigParser(defaults=const.DEFAULTS)
    parser.read([filename])
    logging.debug("%s", parser["essentia"])
    return parser


def safety_check(config):
    for filename in [config.get("essentia", "path"),
                     config.get("essentia", "profile")]:
        if not isfile(filename):
            exit("%s does not exist" % filename)


def main():
    parser = make_argparser()
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

    safety_check(config)

    files = []

    for name in args.filenames:
        if isfile(name):
            files.append(name)
        else:
            files.extend(collect_files(name))

    loop = asyncio.get_event_loop()
    loop.set_debug(args.verbose)

    abzer = Abzer(args.processes,
                  config.get("essentia", "path"),
                  config.get("essentia", "profile"),
                  files)
    try:
        loop.run_until_complete(abzer.run())
    finally:
        abzer.session.close()
        loop.close()

if __name__ == "__main__":
    main()
