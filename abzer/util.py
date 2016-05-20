#!/usr/bin/env python
# coding: utf-8
# Copyright © 2016 Wieland Hoffmann
# License: MIT, see LICENSE for details
import argparse
import configparser
import logging

from . import const
from os import cpu_count, walk
from os.path import join


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
