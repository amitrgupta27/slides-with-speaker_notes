"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mfinal_project` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``final_project.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``final_project.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import argparse
from luigi import build
from final_project.tasks import MapTextToSlides

parser = argparse.ArgumentParser(description='Command description.')
parser.add_argument("-duration", "--duration", type=int, default=100)


def main(args=None):
    args = parser.parse_args(args=args)
    build([
        MapTextToSlides(lecture_duration=args.duration)
    ], local_scheduler=True)

