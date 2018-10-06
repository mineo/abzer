#!/usr/bin/env python
# coding: utf-8
# Copyright © 2018 Wieland Hoffmann
# License: MIT, see LICENSE for details
from abzer.util import collect_files


def test_file_discovery(musicdir):
    """Test all files in the directory are found."""
    all_files_in_dir = sorted(str(file_) for file_ in musicdir.visit()
                              if file_.check(dir=0))
    found_files_in_dir = sorted(collect_files(str(musicdir)))
    assert all_files_in_dir == found_files_in_dir
