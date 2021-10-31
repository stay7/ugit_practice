import argparse
import os

from . import data


def main():
    args = parse_args()
    args.func(args)


def parse_args():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command")
    commands.required = True

    init_parser = commands.add_parser("init")
    init_parser.set_defaults(func=init)
    return parser.parse_args()


# empty repository를 만드는 argument
def init(args):
    data.init()
    print(f"ugit repository가 {os.getcwd()}/{data.GIT_DIR}")
