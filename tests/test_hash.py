# -*- coding: utf-8 -*-

# Copyright 2022 Adansons Inc.
# Please contact engineer@adansons.co.jp

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from base.hash import calc_file_hash

PATH = os.path.join(os.path.dirname(__file__), "data", "sample.jpeg")
MD5HASH = "93304c750cf3dd4e8e91d374d60b9734"
SHA224HASH = "c9462ddf27c8aefbf74f70ca13fd113f304e46d1359cde3f3aa8908a"
SHA256HASH = "09e300d993f62d0e623e0d631a468e6126881b0e9152547ca8b369e7233e5717"
SHA384HASH = "eb2e4a765e17f666122bb30f13a40e843fbfb32d6f6b3f96b5d8614c2761f3827ef5c374b5078c651d31ac549feed8f2"
SHA512HASH = "c9414d9abf93f278457d9d31a0eef74a57644f7431aa9132a3ac5e7642b29a6b2f27976ff19700cca0bd9b902f8e4d5bfcfb4733b8b79e9b8c85d40fc796e7d6"
SHA1HASH = "ec33c6e4dbe7a84f177899f6aac29bb718cb0451"


def test_calc_file_hash_md5():
    digest = calc_file_hash(PATH, algorithm="md5", split_chunk=False)
    assert digest == MD5HASH


def test_calc_file_hash_sha224():
    digest = calc_file_hash(PATH, algorithm="sha224", split_chunk=False)
    assert digest == SHA224HASH


def test_calc_file_hash_sha256():
    digest = calc_file_hash(PATH, algorithm="sha256", split_chunk=False)
    assert digest == SHA256HASH


def test_calc_file_hash_sha384():
    digest = calc_file_hash(PATH, algorithm="sha384", split_chunk=False)
    assert digest == SHA384HASH


def test_calc_file_hash_sha512():
    digest = calc_file_hash(PATH, algorithm="sha512", split_chunk=False)
    assert digest == SHA512HASH


def test_calc_file_hash_sha1():
    digest = calc_file_hash(PATH, algorithm="sha1", split_chunk=False)
    assert digest == SHA1HASH


def test_split_chunk():
    digest = calc_file_hash(PATH, algorithm="sha256", split_chunk=True)
    assert digest == SHA256HASH


if __name__ == "__main__":
    test_calc_file_hash_md5()
    test_calc_file_hash_sha224()
    test_calc_file_hash_sha256()
    test_calc_file_hash_sha384()
    test_calc_file_hash_sha512()
    test_calc_file_hash_sha1()
    test_split_chunk()
