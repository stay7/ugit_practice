import argparse
import os
import sys
import textwrap

from . import base
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

    hash_object_parser = commands.add_parser("hash-object")
    hash_object_parser.set_defaults(func=hash_object)
    hash_object_parser.add_argument("file")

    cat_file_parser = commands.add_parser("cat-file")
    cat_file_parser.set_defaults(func=cat_file)
    cat_file_parser.add_argument("object")

    write_tree_parser = commands.add_parser("write-tree")
    write_tree_parser.set_defaults(func=write_tree)

    read_tree_parser = commands.add_parser("read-tree")
    read_tree_parser.set_defaults(func=read_tree)
    read_tree_parser.add_argument("tree")

    commit_parser = commands.add_parser("commit")
    commit_parser.set_defaults(func=commit)
    commit_parser.add_argument("-m", "--message", required=True)

    log_parser = commands.add_parser("log")
    log_parser.set_defaults(func=log)
    log_parser.add_argument("oid", nargs="?")

    checkout_parser = commands.add_parser("checkout")
    checkout_parser.set_defaults(func=checkout)
    checkout_parser.add_argument("oid")

    tag_parser = commands.add_parser("tag")
    tag_parser.set_defaults(func=tag)
    tag_parser.add_argument("name")
    tag_parser.add_argument("oid", nargs="?")

    return parser.parse_args()


# empty repository를 만드는 argument
def init(args):
    data.init()
    print(f"ugit repository가 {os.getcwd()}/{data.GIT_DIR}")


def hash_object(args):
    with open(args.file, "rb") as f:
        print(data.hash_object(f.read()))


def cat_file(args):
    sys.stdout.flush()
    sys.stdout.buffer.write(data.get_object(args.object, expected=None))


def write_tree(args):
    print(base.write_tree())


def read_tree(args):
    base.read_tree(args.tree)


def commit(args):
    print(base.commit(args.message))


def checkout(args):
    base.checkout(args.oid)


def tag(args):
    oid = args.oid or data.get_HEAD()
    base.create_tag(args.name, oid)


# file을 이용해 구현한 linked list처럼 연결되어있는 구조
# HEAD의 oid로부터 commit을 가져와서 출력
# commit의 부모가 있으면 oid = commit.parent
def log(args):
    # args에 입력된 oid가 없으면 HEAD부터
    oid = args.oid or data.get_HEAD()
    while oid:
        commit = base.get_commit(oid)
        print(f"commit {oid}\n")
        print(textwrap.indent(commit.message, "    "))
        print("")

        oid = commit.parent
