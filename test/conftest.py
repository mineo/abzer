#!/usr/bin/env python
# coding: utf-8
# Copyright © 2018 Wieland Hoffmann
# License: MIT, see LICENSE for details
import pytest


@pytest.fixture(scope="function",
                params=[[],
                        ["file.mp3", "dir/file.jpeg"]])
def musicdir(tmpdir, request):
    for file_ in request.param:
        f = tmpdir.join(file_)
        f.ensure()
    return tmpdir
