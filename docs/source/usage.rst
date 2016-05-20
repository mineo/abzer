Usage
=====

For now, here's the `--help` output::

  usage: abzer [-h] [-c CONFIG] [-p PROCESSES] [-v] FILENAME [FILENAME ...]

  positional arguments:
    FILENAME

  optional arguments:
    -h, --help            show this help message and exit
    -c CONFIG, --config CONFIG
                          The path to the config file. (default:
                          /home/<username>/.abzsubmit/abzsubmit.conf)
    -p PROCESSES, --processes PROCESSES
                          The number of processes to use for analyzing files.
                          (default: <number of cpus>)
    -v, --verbose         Be more verbose. (default: False)
