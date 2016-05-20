#!/usr/bin/env python
# coding: utf-8
# Copyright © 2016 Wieland Hoffmann
# License: MIT, see LICENSE for details
import asyncio
import configparser
import logging


from .abzer import Abzer
from .util import (collect_files, create_profile_file, ensure_default_path,
                   make_argparser, read_config)
from os.path import isfile
from sys import exit


def safety_check(config):
    filename = config.get("essentia", "path")
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

    ensure_default_path()
    create_profile_file(config.get("essentia", "path"),
                        config.get("essentia", "profile"))
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
