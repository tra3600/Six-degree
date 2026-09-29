"""Lanceur historique : `python 6degre.py` équivaut à `python -m six_degrees`."""

import sys

from six_degrees.cli import main

if __name__ == "__main__":
    sys.exit(main())
