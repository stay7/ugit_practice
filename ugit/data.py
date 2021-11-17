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


# oid로 파일을 읽어서 content를 return
# 1. oid를 이용해 file을 읽음
# 2. type을 분리 후 content를 return
def get_object(oid, expected="blob"):
    with open(f"{GIT_DIR}/objects/{oid}", "rb") as f:
        obj = f.read()

    type_, _, content = obj.partition(b"\x00")
    type_ = type_.decode()

    # file의 타입과 expected type이 다르면 error
    if expected is not None:
        assert type_ == expected, f"Expected {expected}, got {type_}"
    return content


def update_ref(ref, oid):
    ref_path = f"{GIT_DIR}/{ref}"
    os.makedirs(os.path.dirname(ref_path), exist_ok=True)
    with open(ref_path, "w") as f:
        f.write(oid)


def get_ref(ref):
    ref_path = f"{GIT_DIR}/{ref}"
    if os.path.isfile(ref_path):
        with open(ref_path) as f:
            return f.read().strip()
