import hashlib
import os

GIT_DIR = ".ugit"


def init():
    os.makedirs(GIT_DIR)
    os.makedirs(f"{GIT_DIR}/objects")


# 저장할 때 file type을 앞에 붙인다. default 는 blob
# oid는 file data를 hash한 값
def hash_object(data, type_="blob"):
    obj = type_.encode() + b"\x00" + data
    oid = hashlib.sha1(data).hexdigest()
    with open(f"{GIT_DIR}/objects/{oid}", "wb") as out:
        out.write(obj)
    return oid


# oid를 이용해 file을 찾아서 저장
def get_object(oid, expected="blob"):
    with open(f"{GIT_DIR}/objects/{oid}", "rb") as f:
        obj = f.read()

    type_, _, content = obj.partition(b"\x00")
    type_ = type_.decode()

    if expected is not None:
        assert type_ == expected, f"Expected {expected}, got {type_}"
    return content
