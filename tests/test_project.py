# -*- coding: utf-8 -*-

# Copyright 2022 Adansons Inc.
# Please contact engineer@adansons.co.jp
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
    summarize_keys_information,
)

PROJECT_NAME = "adansons_test_project"
USER_ID = get_user_id_from_db(get_access_key())
INVITE_USER_ID = "test_invite@adansons.co.jp"
TESTS_DIR = os.path.dirname(__file__)
TEST_METADATA_SUMMARY = [
    {
        "LowerValue": "0",
        "EditorList": ["xxxx@yyy.com"],
        "Creator": "xxxx@yyy.com",
        "ValueHash": "6dd1c6ef359fc0290897273dfee97dd6d1f277334b9a53f07056500409fd0f3a",
        "LastEditor": "xxxx@yyy.com",
        "UpperValue": "59999",
        "ValueType": "str",
        "CreatedTime": "1651429889.986235",
        "LastModifiedTime": "1651430744.0796146",
        "KeyHash": "a56145270ce6b3bebd1dd012b73948677dd618d496488bc608a3cb43ce3547dd",
        "KeyName": "id",
        "RecordedCount": 70000,
    },
    {
        "LowerValue": "0",
        "EditorList": ["xxxx@yyy.com"],
        "Creator": "xxxx@yyy.com",
        "ValueHash": "6dd1c6ef359fc0290897273dfee97dd6d1f277334b9a53f07056500409fd0f3a",
        "LastEditor": "xxxx@yyy.com",
        "UpperValue": "59999",
        "ValueType": "int",
        "CreatedTime": "1651429889.986235",
        "LastModifiedTime": "1651430744.0796146",
        "KeyHash": "a56145270ce6b3bebd1dd012b73948677dd618d496488bc608a3cb43ce3547dd",
        "KeyName": "index",
        "RecordedCount": 70000,
    },
    {
        "LowerValue": "0or6",
        "EditorList": ["xxxx@yyy.com"],
        "Creator": "xxxx@yyy.com",
        "ValueHash": "665c5c8dca33d1e21cbddcf524c7d8e19ec4b6b1576bbb04032bdedd8e79d95a",
        "LastEditor": "xxxx@yyy.com",
        "UpperValue": "-1",
        "ValueType": "str",
        "CreatedTime": "1651430744.0796146",
        "LastModifiedTime": "1651430744.0796146",
        "KeyHash": "34627e3242f2ca21f540951cb5376600aebba58675654dd5f61e860c6948bffa",
        "KeyName": "correction",
        "RecordedCount": 74,
    },
    {
        "LowerValue": "0",
        "EditorList": ["xxxx@yyy.com"],
        "Creator": "xxxx@yyy.com",
        "ValueHash": "0c2fb8f0d59d60a0a5e524c7794d1cf091a377e5c0d3b2cf19324432562555e1",
        "LastEditor": "xxxx@yyy.com",
        "UpperValue": "9",
        "ValueType": "str",
        "CreatedTime": "1651429889.986235",
        "LastModifiedTime": "1651430744.0796146",
        "KeyHash": "1aca80e8b55c802f7b43740da2990e1b5735bbb323d93eb5ebda8395b04025e2",
        "KeyName": "label",
        "RecordedCount": 70000,
    },
    {
        "LowerValue": "0",
        "EditorList": ["xxxx@yyy.com"],
        "Creator": "xxxx@yyy.com",
        "ValueHash": "0c2fb8f0d59d60a0a5e524c7794d1cf091a377e5c0d3b2cf19324432562555e1",
        "LastEditor": "xxxx@yyy.com",
        "UpperValue": "9",
        "ValueType": "int",
        "CreatedTime": "1651429889.986235",
        "LastModifiedTime": "1651430744.0796146",
        "KeyHash": "1aca80e8b55c802f7b43740da2990e1b5735bbb323d93eb5ebda8395b04025e2",
        "KeyName": "originalLabel",
        "RecordedCount": 70000,
    },
    {
        "LowerValue": "test",
        "EditorList": ["xxxx@yyy.com"],
        "Creator": "xxxx@yyy.com",
        "ValueHash": "0e546bb01e2c9a9d1c388fca8ce3fabdde16084aee10c58becd4767d39f62ab7",
        "LastEditor": "xxxx@yyy.com",
        "UpperValue": "train",
        "ValueType": "str",
        "CreatedTime": "1651429889.986235",
        "LastModifiedTime": "1651430744.0796146",
        "KeyHash": "9c98c4cbd490df10e7dc42f441c72ef835e3719d147241e32b962a6ff8c1f49d",
        "KeyName": "dataType",
        "RecordedCount": 70000,
    },
]
TEST_SUMMARY_OUTPUT = {
    "MaxRecordedCount": 70000,
    "UniqueKeyCount": 4,
    "MaxCharCount": {
        "KEY NAME": 23,
        "VALUE RANGE": 12,
        "VALUE TYPE": 34,
        "RECORDED COUNT": 14,
    },
    "Keys": [
        ("KEY NAME", "VALUE RANGE", "VALUE TYPE", "RECORDED COUNT"),
        ("'id','index'", "0 ~ 59999", "str('id'), int('index')", "70000"),
        ("'correction'", "0or6 ~ -1", "str('correction')", "74"),
        (
            "'label','originalLabel'",
            "0 ~ 9",
            "str('label'), int('originalLabel')",
            "70000",
        ),
        ("'dataType'", "test ~ train", "str('dataType')", "70000"),
    ],
}


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


def test_extract_metafile():
    project = Project(PROJECT_NAME)
    file_path = TESTS_DIR + "/data/sample.xlsx"
    project.extract_metafile(file_path)


def test_estimate_join_rule():
    project = Project(PROJECT_NAME)
    file_path = TESTS_DIR + "/data/sample.xlsx"
    project.estimate_join_rule(file_path=file_path)


def test_add_metafile():
    project = Project(PROJECT_NAME)
    file_path = [TESTS_DIR + "/data/sample.xlsx"]
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


def test_summarize_keys_information():
    result = summarize_keys_information(TEST_METADATA_SUMMARY)
    assert result == TEST_SUMMARY_OUTPUT


if __name__ == "__main__":
    test_initialize()
    test_create_project()
    test_get_projects()
    test_add_datafiles()
    test_add_datafile()
    test_extract_metafile()
    test_estimate_join_rule()
    test_add_metafile()
    test_get_metadata_summary()
    test_link_datafiles()
    test_add_member()
    test_update_member()
    test_get_members()
    test_remove_member()
    test_archive_project()
    test_delete_project()
