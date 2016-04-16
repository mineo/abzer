#!/usr/bin/env python
# coding: utf-8
# Copyright © 2016 Wieland Hoffmann
# License: MIT, see LICENSE for details
import aiohttp
import asyncio
import json
import logging
import sqlite3


from . import const
from tempfile import NamedTemporaryFile


class FileHandler():
    """Takes care of analyzing an audio file and submitting the features to
    acousticbrainz.org.

    """
    def __init__(self, filename):
        self.filename = filename
        self.tempfile = NamedTemporaryFile(mode="r+b")

    async def process(self, essentia, profile):
        """Analyze the file."""
        logging.info("%s: Starting essentia", self.filename)
        process = await asyncio.create_subprocess_exec(
            essentia, self.filename, self.tempfile.name, profile,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        (stdout, stderr) = await process.communicate()
        rc = process.returncode
        if rc != const.SUBPROCESS_OK:
            logging.error("%s: The file could not be analyzed.", self.filename)
            logging.error("Here is essentias stdout: %s",
                          stdout.decode("utf-8"))
            logging.error("Here is essentias stderr: %s",
                          stderr.decode("utf-8"))
        return rc

    async def submit_features(self, session):
        """Submit the results of the analysis."""
        # Ugh, we read the whole file here in a blocking manner :/
        logging.info("%s: Submitting features", self.filename)
        content = self.tempfile.read()
        data = json.loads(content.decode("utf-8"))

        if "musicbrainz_trackid" not in data["metadata"]["tags"]:
            raise ValueError("%s does not have a recording id" % self.filename)

        mbid = data["metadata"]["tags"]["musicbrainz_trackid"][0]
        url = const.URL_BASE % mbid
        status = 0
        async with session.post(url, data=content) as resp:
            status = resp.status
            if status != const.HTTP_OK:
                logging.error("%s: Feature submission failed with HTTP %i",
                              self.filename)
        return status


class Abzer():
    def __init__(self, num_processes, essentia_path, profile_path, filenames):
        self.db = sqlite3.connect(const.LOGFILE)
        self._setup_db()
        self.essentia_path = essentia_path
        self.filenames = filenames
        self.num_processes = num_processes
        self.profile_path = profile_path
        self.session = aiohttp.ClientSession(headers=const.HEADERS)
        # Set the queue size to double the amount of processes. That way, more
        # filenames than subprocesses are in the queue, but not all of them
        # (which might be hundreds of thousands).
        self.queue = asyncio.Queue(num_processes * 2)

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
        logging.debug("Files to process: %s", to_process)
        already_processed = set(self._processed_files_from_log())
        to_process.difference_update(already_processed)
        return to_process

    def _setup_db(self):
        with self.db:
            self.db.execute("""create table if not exists filelog (id integer primary key, filename text not null, reason text)""")  # noqa
            self.db.execute("""create index if not exists filelog_filename on filelog(filename)""")  # noqa

    async def _process(self, file):
        fp = FileHandler(file)
        rc = await fp.process(self.essentia_path, self.profile_path)

        if rc != 0:
            status = "Ret %i" % rc
        else:
            try:
                http = await fp.submit_features(self.session)
                status = "HTTP %i" % http
            except ValueError:
                status = "No MBID"

        # Let's hope this doesn't take too long for now :-)
        self._log_completion(file, status)
        logging.info("%s: Done", fp.filename)

    async def consumer(self):
        while True:
            filename = await self.queue.get()
            try:
                await self._process(filename)
            finally:
                self.queue.task_done()
            if self.queue.empty():
                break

    async def producer(self, to_process):
        for filename in to_process:
            logging.debug("Putting %s into the queue", filename)
            await self.queue.put(filename)

    async def run(self):
        to_process = self._files_to_process()
        if to_process:
            tasks = []
            tasks.append(self.producer(to_process))
            num_tasks = min(len(to_process), self.num_processes)
            for i in range(0, num_tasks):
                tasks.append(self.consumer())
            tasks.append(self.queue.join())
            await asyncio.gather(*tasks)
        else:
            logging.info("All files have already been processed")
