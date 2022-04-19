# -*- coding: utf-8 -*-

# Copyright 2022 Adansons Inc.
# Please contact engineer@adansons.co.jp
import hashlib


HASH_FUNCS = {
    "md5": hashlib.md5,
    "sha224": hashlib.sha224,
    "sha256": hashlib.sha256,
    "sha384": hashlib.sha384,
    "sha512": hashlib.sha512,
    "sha1": hashlib.sha1,
}


def calc_file_hash(
    path: str,
    algorithm: str = "sha256",
    split_chunk: bool = True,
    chunk_size: int = 2048,
) -> str:
    """
    Calculate hash value of each file

    Parameters
    ----------
    path : str
        target file path
    algorithm : {"md5", "sha224", "sha256", "sha384", "sha512", "sha1"}, default="sha256"
        hash algorithm name
    split_chunk : bool, default=True
        if True, split large file to byte chunks
    chunk_size : int, default=2048
        block byte size of chunk

    Returns
    -------
    digest : str
        hash string of inputed file
    """
    hash_func = HASH_FUNCS[algorithm]()

    with open(path, "rb") as f:
        if split_chunk:
            while True:
                chunk = f.read(chunk_size * hash_func.block_size)
                if len(chunk) == 0:
                    break

                hash_func.update(chunk)
        else:
            chunk = f.read()
            hash_func.update(chunk)

    digest = hash_func.hexdigest()
    return digest


if __name__ == "__main__":
    pass
