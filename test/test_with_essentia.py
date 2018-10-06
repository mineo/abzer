#!/usr/bin/env python
# coding: utf-8
# Copyright © 2018 Wieland Hoffmann
# License: MIT, see LICENSE for details
import pytest


from abzer.abzer import Abzer
from abzer import const
from abzer.util import create_profile_file, read_config
from aiohttp import web
from shutil import which

essentia_path = which("streaming_extractor_music")

pytestmark = pytest.mark.skipif(essentia_path is None,
                                reason="streaming_extractor_music is required for these tests")


@pytest.fixture
def profilefile(tmpdir):
    profile = tmpdir.join("profile")
    create_profile_file(essentia_path, str(profile))
    return profile


@pytest.fixture
def configfile(tmpdir, profilefile):
    profilepath = str(profilefile)
    cfg = tmpdir.join("config")
    cfg.write_text("""
    [essentia]
    path = {essentiapath}
    profile = {profilepath}
    """.format(essentiapath=essentia_path,
               profilepath=profilepath),
        encoding="utf-8")


@pytest.fixture
def abzer_factory(configfile, musicdir):
    def make_abzer(session):
        config = read_config(str(configfile))
        all_files_in_dir = sorted(str(file_) for file_ in musicdir.visit()
                                  if file_.check(dir=0))
        return all_files_in_dir, Abzer(1,
                                       config.get("essentia", "path"),
                                       config.get("essentia", "profile"),
                                       all_files_in_dir,
                                       db=":memory:",
                                       session=session)
    return make_abzer


@pytest.fixture
def client_factory(loop, aiohttp_client):
    def make_client(routes):
        app = web.Application()
        app.add_routes(routes)
        return aiohttp_client(app)
    return make_client

async def test_no_request_for_only_failures(abzer_factory, client_factory):
    requests = 0

    @web.middleware
    async def responsecounter(request, handler):
        response = await handler(request)
        requests += 1
        return response


    client = await client_factory([])
    files, abzer = abzer_factory(client.session)
    app = client.app


    async with abzer as a:
        const.BASE_URL = client.make_url("%s/low-level")
        await a.run()

    assert requests == 0

    db = abzer.db

    with db as db:
        for (filename, reason) in db.execute("SELECT filename, reason from filelog"):
            assert filename in files
            prefix, rc = reason.split(" ", 1)
            assert prefix == "Ret"
            assert int(rc) != 0
