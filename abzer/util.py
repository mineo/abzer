#!/usr/bin/env python
# coding: utf-8
# Copyright © 2016 Wieland Hoffmann
# License: MIT, see LICENSE for details
import argparse
import configparser
import logging

from . import const
from hashlib import sha1
from os import cpu_count, walk
from os.path import join


def create_profile_file(essentia_path, profile_path):
    """
    :param str essentia_path:
    :param str profile_path:
    """
    hash_ = sha1()
    with open(essentia_path, "rb") as fp:
        hash_.update(fp.read())
    digest = hash_.hexdigest()
    profile = const.PROFILE_TEMPLATE.format(sha=digest)
    logging.debug("Writing a profile with SHA1 %s to %s", digest, profile_path)
    with open(profile_path, "w") as fp:
        fp.write(profile)


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
    read = parser.read([filename])
    if not (read or parser.has_section("essentia")):
        # We can do everything we want by just using the default values.
        # However, we do need an "essentia" section in the parser for the
        # default values to be used.
        parser.add_section("essentia")
    return parser
