#!/usr/bin/env python
from __future__ import print_function
from codecs import open
from setuptools import setup


setup(name="abzer",
      author="Wieland Hoffmann",
      author_email="themineo@gmail.com",
      packages=["abzer"],
      package_dir={"abzer": "abzer"},
      download_url=["https://github.com/mineo/abzer/tarball/master"],
      url=["http://github.com/mineo/abzer"],
      license="MIT",
      classifiers=["Development Status :: 4 - Beta",
                   "License :: OSI Approved :: MIT License",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 3.5"],
      description="",
      long_description=open("README.txt", encoding="utf-8").read(),
      setup_requires=["setuptools_scm"],
      use_scm_version={"write_to": "abzer/version.py"},
      install_requires=["aiohttp"],
      extras_require={
          'docs': ['sphinx']},
      entry_points={
          'console_scripts': ['abzer=abzer.__main__:main']
      }
      )
