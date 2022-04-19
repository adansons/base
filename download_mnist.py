# -*- coding: utf-8 -*-

# Copyright 2022 Adansons Inc.
# Please contact higuchi@adansons.co.jp
# This script is cited from https://github.com/myleott/mnist_png/blob/master/convert_mnist_to_png.py

import os
import struct
import sys

from array import array

import png

import gzip
import urllib.request


original_sources_list = [
    "train-images-idx3-ubyte",
    "train-labels-idx1-ubyte",
    "t10k-images-idx3-ubyte",
    "t10k-labels-idx1-ubyte",
]


def download_original_sources(path: str = "."):
    for s in original_sources_list:
        fname = f"{s}.gz"
        url = f"http://yann.lecun.com/exdb/mnist/{fname}"

        s_path = os.path.join(path, s)
        fname_path = os.path.join(path, fname)
        urllib.request.urlretrieve(url, fname_path)
        with gzip.open(fname_path, mode="rb") as gzfile:
            with open(s_path, mode="wb") as f:
                f.write(gzfile.read())

        os.remove(fname_path)


def remove_original_sources(path: str = "."):
    for s in original_sources_list:
        s_path = os.path.join(path, s)
        os.remove(s_path)


# source: http://abel.ee.ucla.edu/cvxopt/_downloads/mnist.py
def read(dataset: str = "train", path: str = "."):
    if dataset == "train":
        fname_img = os.path.join(path, "train-images-idx3-ubyte")
        fname_lbl = os.path.join(path, "train-labels-idx1-ubyte")
    elif dataset == "test":
        fname_img = os.path.join(path, "t10k-images-idx3-ubyte")
        fname_lbl = os.path.join(path, "t10k-labels-idx1-ubyte")
    else:
        raise ValueError("dataset must be 'test' or 'train'")

    flbl = open(fname_lbl, "rb")
    magic_nr, size = struct.unpack(">II", flbl.read(8))
    lbl = array("b", flbl.read())
    flbl.close()

    fimg = open(fname_img, "rb")
    magic_nr, size, rows, cols = struct.unpack(">IIII", fimg.read(16))
    img = array("B", fimg.read())
    fimg.close()

    return lbl, img, size, rows, cols


def write_dataset(labels, data, size, rows, cols, output_dir):
    # create output directories
    output_dirs = [os.path.join(output_dir, str(i)) for i in range(10)]
    for dir in output_dirs:
        os.makedirs(dir, exist_ok=True)

    # write data
    for (i, label) in enumerate(labels):
        output_filename = os.path.join(output_dirs[label], str(i) + ".png")
        with open(output_filename, "wb") as h:
            w = png.Writer(cols, rows, greyscale=True)
            data_i = [
                data[(i * rows * cols + j * cols) : (i * rows * cols + (j + 1) * cols)]
                for j in range(rows)
            ]
            w.write(h, data_i)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <output_path>")
        sys.exit()

    data_root_dir = sys.argv[1]
    os.makedirs(data_root_dir, exist_ok=True)
    download_original_sources(data_root_dir)

    for dataset in ["train", "test"]:
        labels, data, size, rows, cols = read(dataset, data_root_dir)
        write_dataset(
            labels, data, size, rows, cols, os.path.join(data_root_dir, dataset)
        )

    remove_original_sources(data_root_dir)
