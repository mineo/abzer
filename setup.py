#!/usr/bin/env python
from __future__ import print_function
from codecs import open
from setuptools import setup


setup(name="abzer",
      author="Wieland Hoffmann",
      author_email="themineo@gmail.com",
      packages=["abzer"],
      package_dir={"abzer": "abzer"},
      download_url="https://github.com/mineo/abzer/tarball/master",
      url="https://github.com/mineo/abzer",
      license="MIT",
      classifiers=["Development Status :: 4 - Beta",
                   "License :: OSI Approved :: MIT License",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 3.6",
                   "Programming Language :: Python :: 3.7"
                   "Programming Language :: Python :: 3.8"
                   "Programming Language :: Python :: 3.9"],
      description="AcousticBrainz submission tool",
      long_description=open("README.txt", encoding="utf-8").read(),
      setup_requires=["pytest-runner", "setuptools_scm"],
      use_scm_version={"write_to": "abzer/version.py"},
      install_requires=["aiohttp"],
      tests_require=["pytest", "pytest-aiohttp"],
      extras_require={
          'docs': ['sphinx', 'sphinxcontrib-autoprogram']},
      python_requires='>=3.5',
      entry_points={
          'console_scripts': ['abzer=abzer.__main__:main']
      })
