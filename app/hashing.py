from hashlib import sha256


def _hash(*args) -> str:
    hashing_text = ""
    h = sha256()
    print("sha256() -> {}".format(type(h)))
    for arg in args:
        hashing_text += str(arg)
    h.update(hashing_text.encode("utf-8"))
    print("hexdigest() -> {}".format(type(h.hexdigest())))
    return h.hexdigest()