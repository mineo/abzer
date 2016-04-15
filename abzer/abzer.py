#!/usr/bin/env python
# coding: utf-8
# Copyright © 2016 Wieland Hoffmann
# License: MIT, see LICENSE for details
import aiohttp
import asyncio
import json
import sqlite3
from tempfile import NamedTemporaryFile

from os import listdir
from os.path import join

ESSENTIA = "/usr/bin/streaming_extractor_music"
PROFILE = "/home/wieland/.abzsubmit/profile.yaml"
URL_BASE = "http://acousticbrainz.org/%s/low-level"


class FileHandler():
    """Takes care of analyzing an audio file and submitting the features to
    acousticbrainz.or

    """
    def __init__(self, filename):
        self.filename = filename
        self.tempfile = NamedTemporaryFile(mode="r+b")

    async def process(self):
        """Analyze the file."""
        print("Analyzing %s" % self.filename)
        process = await asyncio.create_subprocess_exec(
            ESSENTIA, self.filename, self.tempfile.name, PROFILE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        (stdout, stderr) = await process.communicate()
        return (self, process.returncode)

    async def submit_features(self, session):
        """Submit the results of the analysis."""
        # Ugh, we read the whole file here in a blocking manner :/
        content = self.tempfile.read()
        data = json.loads(content.decode("utf-8"))

        if "musicbrainz_trackid" not in data["metadata"]["tags"]:
            raise ValueError("%s does not have a recording id" % self.filename)

        mbid = data["metadata"]["tags"]["musicbrainz_trackid"][0]
        url = URL_BASE % mbid
        status = 0
        async with session.post(url, data=content) as resp:
            status = resp.status
        return status


class Abzer():
    def __init__(self, filenames):
        self.db = sqlite3.connect("/home/wieland/.abzsubmit/filelog.sqlite")
        self.filenames = filenames
        self.cpusem = asyncio.BoundedSemaphore(2)
        self.session = aiohttp.ClientSession()

    def _log_completion(self, filename, status):
        with self.db:
            self.db.execute(
                "INSERT INTO filelog (filename, reason) VALUES (?, ?);",
                (filename, status))

    def _processed_files_from_log(self):
        with self.db:
            tuples = self.db.execute(
                "select filename from filelog;").\
                fetchall()
        filenames = [tuple[0] for tuple in tuples]
        return filenames

    def _files_to_process(self):
        to_process = set(self.filenames)
        already_processed = set(self._processed_files_from_log())
        to_process.difference_update(already_processed)
        return to_process

    async def process(self, file):
        await self.cpusem.acquire()
        fp = FileHandler(file)
        await fp.process()
        self.cpusem.release()
        try:
            http = await fp.submit_features(self.session)
            status = "HTTP %i" % http
        except ValueError:
            status = "No MBID"
        # Let's hope this doesn't take too long for now :-)
        self._log_completion(file, status)

    async def run(self):
        to_process = self._files_to_process()
        if to_process:
            tasks = [self.process(f) for f in to_process]
            await asyncio.wait(tasks)
        else:
            print("All files have already been processed")

files = (join("/home/wieland/Musik", filename) for filename in
         listdir("/home/wieland/Musik")[-3:])
loop = asyncio.get_event_loop()
abzer = Abzer(files)
loop.run_until_complete(abzer.run())
abzer.session.close()
loop.close()
