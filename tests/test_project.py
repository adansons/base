# -*- coding: utf-8 -*-

# Copyright 2022 Adansons Inc.
# Please contact engineer@adansons.co.jp
from distutils import extension
import os
import time
from click.testing import CliRunner
from base.cli import (
    list_project,
    remove_project,
)
from base.config import (
    get_access_key,
    delete_project_config,
    get_user_id_from_db,
)
from base.project import (
    create_project,
    get_projects,
    archive_project,
    delete_project,
    Project,
)

PROJECT_NAME = "adansons_test_project"
USER_ID = get_user_id_from_db(get_access_key())
INVITE_USER_ID = "test_invite@adansons.co.jp"
TESTS_DIR = os.path.dirname(__file__)


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


def test_create_project():
    create_project(USER_ID, PROJECT_NAME)
    time.sleep(20)


def test_get_projects():
    project_list = get_projects(USER_ID)
    assert any([project["ProjectName"] == PROJECT_NAME for project in project_list])


def test_add_datafiles():
    project = Project(PROJECT_NAME)
    dir_path = TESTS_DIR
    extension = "jpeg"
    parsing_rule = "{_}/{title}.jpeg"
    file_num = project.add_datafiles(dir_path, extension, parsing_rule=parsing_rule)
    assert file_num == 1


def test_add_datafile():
    project = Project(PROJECT_NAME)
    file_path = TESTS_DIR + "/data/sample.jpeg"
    attributes = {"title": "sample"}
    file_num = project.add_datafile(file_path, attributes)


def test_add_metafile():
    project = Project(PROJECT_NAME)
    file_path = TESTS_DIR + "/data/sample.xlsx"
    project.add_metafile(file_path, auto=True)


def test_get_metadata_summary():
    project = Project(PROJECT_NAME)
    project.get_metadata_summary()


def test_link_datafiles():
    project = Project(PROJECT_NAME)
    dir_path = TESTS_DIR
    extension = "jpeg"
    project.link_datafiles(dir_path, extension)


def test_add_member():
    project = Project(PROJECT_NAME)
    project.add_member(INVITE_USER_ID, "Editor")


def test_update_member():
    project = Project(PROJECT_NAME)
    project.update_member(INVITE_USER_ID, "Admin")


def test_get_members():
    project = Project(PROJECT_NAME)
    project.get_members()


def test_remove_member():
    project = Project(PROJECT_NAME)
    project.remove_member(INVITE_USER_ID)


def test_archive_project():
    archive_project(USER_ID, PROJECT_NAME)


def test_delete_project():
    delete_project(USER_ID, PROJECT_NAME)
    delete_project_config(USER_ID, PROJECT_NAME)


if __name__ == "__main__":
    test_initialize()
    test_create_project()
    test_get_projects()
    test_add_datafiles()
    test_add_datafile()
    test_add_metafile()
    test_get_metadata_summary()
    test_link_datafiles()
    test_add_member()
    test_update_member()
    test_get_members()
    test_remove_member()
    test_archive_project()
    test_delete_project()
