# -*- coding: utf-8 -*-

# Copyright 2022 Adansons Inc.
# Please contact engineer@adansons.co.jp
import time
from click.testing import CliRunner
from base.cli import (
    list_project,
    remove_project,
)
from base.config import (
    get_user_id,
    register_user_id,
    get_access_key,
    register_access_key,
    get_project_uid,
    check_project_exists,
    register_project_uid,
    delete_project_config,
    update_project_info,
    get_user_id_from_db,
)
from base.project import create_project

PROJECT_NAME = "adansons_test_project"


def test_initialize():
    """
    If something went wrong past test session.
    You may have exsiting tables, so you have to clear them before below tests.
    """
    runner = CliRunner()
    result = runner.invoke(list_project, [])
    if PROJECT_NAME in result.output:
        result = runner.invoke(remove_project, [PROJECT_NAME])

    result = runner.invoke(list_project, ["--archived"])
    if PROJECT_NAME in result.output:
        result = runner.invoke(remove_project, [PROJECT_NAME, "--confirm"])


def test_get_access_key():
    get_access_key()


def test_register_access_key():
    access_key = get_access_key()
    register_access_key(access_key)


def test_get_user_id_from_db():
    access_key = get_access_key()
    get_user_id_from_db(access_key)


def test_register_user_id():
    access_key = get_access_key()
    user_id = get_user_id_from_db(access_key)
    register_user_id(user_id)


def test_get_user_id():
    get_user_id()


def test_register_project():
    user_id = get_user_id()
    create_project(user_id, PROJECT_NAME)
    time.sleep(20)


def test_check_project_exists():
    user_id = get_user_id()
    assert check_project_exists(user_id, PROJECT_NAME)


def test_get_project_uid():
    user_id = get_user_id()
    get_project_uid(user_id, PROJECT_NAME)


def test_register_project_uid():
    user_id = get_user_id()
    project_uid = get_project_uid(user_id, PROJECT_NAME)
    register_project_uid(user_id, PROJECT_NAME, project_uid)


def test_update_project_info():
    user_id = get_user_id()
    update_project_info(user_id)


def test_archive_project():
    runner = CliRunner()
    result = runner.invoke(remove_project, [PROJECT_NAME])
    assert result.exit_code == 0
    assert f"{PROJECT_NAME} was Archived" in result.output
    result = runner.invoke(list_project, [])
    assert result.exit_code == 0
    assert PROJECT_NAME not in result.output


# How to test delete project config itself?
def test_delete_project():
    runner = CliRunner()
    result = runner.invoke(remove_project, [PROJECT_NAME, "--confirm"])
    assert result.exit_code == 0
    assert f"{PROJECT_NAME} was Deleted" in result.output
    result = runner.invoke(list_project, ["--archived"])
    assert result.exit_code == 0
    assert PROJECT_NAME not in result.output


if __name__ == "__main__":
    test_initialize()
    test_get_access_key()
    test_register_access_key()
    test_get_user_id_from_db()
    test_register_user_id()
    test_get_user_id()
    test_check_project_exists()
    test_get_project_uid()
    test_register_project_uid()
    test_update_project_info()
    test_archive_project()
    test_delete_project()
