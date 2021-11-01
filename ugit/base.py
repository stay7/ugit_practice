import os

from . import data


def write_tree(directory="."):
    entires = []
    with os.scandir(directory) as it:
        for entry in it:
            full = f"{directory}/{entry.name}"
            if is_ignored(full):
                continue
            if entry.is_file(follow_symlinks=False):
                type_ = "blob"
                with open(full, "rb") as f:
                    oid = data.hash_object(f.read())
                print(full)
            elif entry.is_dir(follow_symlinks=False):
                type_ = "tree"
                oid = write_tree(full)
            entires.append((entry.name, oid, type_))

    tree = "".join(f"{type_} {oid} {name}\n" for name, oid, type_ in sorted(entires))
    return data.hash_object(tree.encode(), "tree")


# .ugit은 user file이 아니므로 무시
def is_ignored(path):
    return ".ugit" in path.split("/")
