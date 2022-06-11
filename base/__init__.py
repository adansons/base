# -*- coding: utf-8 -*-

# Copyright 2021 Adansons Inc.
# Please contact engineer@adansons.co.jp

from .project import Project
from .dataset import Dataset


# check exists local cache directory and files
import os

CACHE_DIR = os.path.join(os.path.expanduser("~"), ".base")
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".base", "config")
PROJECT_FILE = os.path.join(os.path.expanduser("~"), ".base", "projects")

os.makedirs(CACHE_DIR, exist_ok=True)

# initialize with empty file
if not os.path.exists(CONFIG_FILE):
    open(CONFIG_FILE, "w").close()
if not os.path.exists(PROJECT_FILE):
    open(PROJECT_FILE, "w").close()

VERSION = "0.1.2"
__version__ = VERSION
