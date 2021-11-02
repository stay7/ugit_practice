import os

from . import data

# 현재 버전을 object/에 tree타입으로 저장해두는 것
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


def _iter_tree_entries(oid):
    if not oid:
        return
    tree = data.get_object(oid, "tree")
    for entry in tree.decode().splitlines():
        type_, oid, name = entry.split(" ", 2)
        yield type_, oid, name


def get_tree(oid, base_path=""):
    result = {}
    for type_, oid, name in _iter_tree_entries(oid):
        assert "/" not in name
        assert name not in ("..", ".")
        path = base_path + name
        if type_ == "blob":
            result[path] = oid
        elif type_ == "tree":
            result.update(get_tree(oid, f"{path}/"))
        else:
            assert False, f"Unknown tree entry {type_}"
    return result


# 현재 directory를 비운다
def _empty_current_directory():
    for root, dirnames, filenames in os.walk(".", topdown=False):
        for filename in filenames:
            path = os.path.relpath(f"{root}/{filename}")
            if is_ignored(path) or not os.path.isfile(path):
                continue
            os.remove(path)
        for dirname in dirnames:
            path = os.path.relpath(f"{root}/{dirname}")
            if is_ignored(path):
                continue
            try:
                os.rmdir(path)
            except (FileNotFoundError, OSError):
                pass


# _empty_current_directory로 현재 directory를 비우고
# 예전 tree의 파일들을 생성한다
def read_tree(tree_oid):
    _empty_current_directory()
    for path, oid in get_tree(tree_oid, base_path="./").items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data.get_object(oid))


# commit 메시지를 작성
# HEAD가 있으면 parent를 oid를 추가
# HEAD를 새로 추가한 oid로 변경
def commit(message):
    commit = f"tree {write_tree()}\n"

    HEAD = data.get_HEAD()
    if HEAD:
        commit += f"parent {HEAD}\n"

    commit += "\n"
    commit += f"{message}\n"

    oid = data.hash_object(commit.encode(), "commit")
    data.set_HEAD(oid)
    return oid


# .ugit은 user file이 아니므로 무시
def is_ignored(path):
    return ".ugit" in path.split("/")
