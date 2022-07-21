# -*- coding: utf-8 -*-

# Copyright 2022 Adansons Inc.
# Please contact engineer@adansons.co.jp
import os
import json
import requests
import configparser


CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".base", "config")
PROJECT_FILE = os.path.join(os.path.expanduser("~"), ".base", "projects")
LINKER_DIR = os.path.join(os.path.expanduser("~"), ".base", "linker")

HEADER = {"Content-Type": "application/json"}
BASE_API_ENDPOINT = "https://api.base.adansons.co.jp"


def get_user_id() -> str:
    """
    Get user id from config file.
    if you have 'BASE_USER_ID' on environment variables, Base will use it

    Returns
    -------
    user_id : str
        aquired user id from environment variable or config file
    """
    user_id = os.environ.get("BASE_USER_ID", None)
    if user_id is None:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)

        user_id = config["default"]["user_id"]

    return user_id


def register_user_id(user_id: str) -> None:
    """
    Register user id to local config file.

    Parameters
    ----------
    user_id : str
        target user id
    """
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    config["default"].update({"user_id": user_id})
    with open(CONFIG_FILE, "w") as f:
        config.write(f)


def get_access_key() -> str:
    """
    Get access key from config file
    if you have 'BASE_ACCESS_KEY' on environment variables, Base will use it

    Returns
    -------
    access_key : str
        aquired API access key from environment variable or config file
    """
    access_key = os.environ.get("BASE_ACCESS_KEY", None)
    if access_key is None:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)

        access_key = config["default"]["access_key"]

    return access_key


def register_access_key(access_key: str) -> None:
    """
    Register access key to local config file.

    Parameters
    ----------
    access_key : str
        API access key
    """
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    config["default"] = {"access_key": access_key}
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        config.write(f)


def get_project_uid(user_id: str, project_name: str) -> str:
    """
    Get project uid from project name.

    Parameters
    ----------
    user_id : str
        user id
    project_name : str
        target project name

    Returns
    -------
    project_uid : str
        project uid of given project name
    """
    config = configparser.ConfigParser()
    config.read(PROJECT_FILE)

    is_exist = check_project_exists(user_id, project_name)
    if not is_exist:
        raise KeyError(f"Project {project_name} does not exist.")
    else:
        project_uid = config[user_id][project_name]
        return project_uid


def check_project_exists(user_id: str, project_name: str) -> bool:
    """
    Check project is already exists or not

    Parameters
    ----------
    user_id : str
        user id
    project_name : str
        target project name

    Returns
    -------
    project_exists : bool
        project already exists or not
    """
    config = configparser.ConfigParser()
    config.read(PROJECT_FILE)

    project_exists = project_name in config[user_id]

    return project_exists


def register_project_uid(user_id: str, project: str, project_uid: str) -> None:
    """
    Register project uid to local config file.

    Parameters
    ----------
    user_id : str
        user id
    project : str
        target project name
    project_uid : str
        target project uid
    """
    config = configparser.ConfigParser()
    config.read(PROJECT_FILE)

    if config.has_section(user_id):
        config[user_id][project] = project_uid
    else:
        config[user_id] = {project: project_uid}
    with open(PROJECT_FILE, "w") as f:
        config.write(f)


def delete_project_config(user_id: str, project_name: str) -> None:
    """
    Delete config of specified project.

    Parameters
    ----------
    user_id : str
        user id
    project_name : str
        target project name
    """
    config = configparser.ConfigParser()
    config.read(PROJECT_FILE)

    config.remove_option(user_id, project_name)
    with open(PROJECT_FILE, "w") as f:
        config.write(f)


def update_project_info(user_id: str) -> None:
    """
    Update local project info with remote.

    Parameters
    ----------
    user_id : str
        target user id
    """
    config = configparser.ConfigParser()
    config.read(PROJECT_FILE)

    config.remove_section(user_id)

    access_key = get_access_key()
    HEADER.update({"x-api-key": access_key})

    url = f"{BASE_API_ENDPOINT}/projects?user={user_id}"
    res = requests.get(url, headers=HEADER)
    if res.status_code != 200:
        raise ValueError("Invalid user configuration")
    projects = res.json()["Projects"]

    url += "&archived=1"
    res = requests.get(url, headers=HEADER)
    if res.json()["Projects"]:
        projects.extend(res.json()["Projects"])

    project_info = {}
    for project in projects:
        project_name = project["ProjectName"]
        project_uid = project["ProjectUid"]
        project_info[project_name] = project_uid

    config[user_id] = project_info
    with open(PROJECT_FILE, "w") as f:
        config.write(f)


def get_user_id_from_db(access_key: str) -> str:
    """
    Get user id from remote db.

    Parameters
    ----------
    access_key : str
        API access key saved in config file
    """
    url = f"{BASE_API_ENDPOINT}/user/id"
    res = requests.get(url, data=json.dumps({"api_key": access_key}), headers=HEADER)

    if res.status_code != 200:
        raise ValueError(
            "Incorrect access key was specified. Please retry or ask support team via Slack. \nIf you have not joined our Slack yet, get your invite here!\n-> https://share.hsforms.com/16OxTF7eJRPK92oGCny7nGw8moen\n"
        )
    user_id = res.json()["user_id"]

    return user_id


if __name__ == "__main__":
    pass
