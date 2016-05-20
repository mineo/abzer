


abzer
═════

  Install abzer as shown [here] , run it by either calling
  `/usr/bin/abzer' or `python -m abzer'.

  Until Read the Docs supports Python 3.5, I'll just dump `--help' here

  ┌────
  │ usage: abzer [-h] [-c CONFIG] [-p PROCESSES] [-v] FILENAME [FILENAME ...]
  │
  │ positional arguments:
  │   FILENAME
  │
  │ optional arguments:
  │   -h, --help            show this help message and exit
  │   -c CONFIG, --config CONFIG
  │                         The path to the config file. (default:
  │                         /home/<username>/.abzsubmit/abzsubmit.conf)
  │   -p PROCESSES, --processes PROCESSES
  │                         The number of processes to use for analyzing files.
  │                         (default: <number of cpus>)
  │   -v, --verbose         Be more verbose. (default: False)
  └────

  abzer uses the same config file as the [acousticbrainz-client]
  application, but only uses the `path' option in the `essentia'
  section. However, it doesn't require a config file to work, but just
  uses default values. If those don't work on your system, you'll be
  notified of that.


  [here] https://abzer.readthedocs.org/en/latest/setup.html

  [acousticbrainz-client] https://github.com/MTG/acousticbrainz-client
