# -*- coding: utf-8 -*-

# Copyright 2022 Adansons Inc.
# Please contact engineer@adansons.co.jp

import os

import time
from unittest import result, runner
from click.testing import CliRunner
from base.cli import (
    create_table,
    import_data,
    list_project,
    remove_project,
    show_project_detail,
    import_data,
    data_link,
    search_files,
    invite_member,
)


PROJECT_NAME = "adansons_test_project"
INVITE_USER_ID = "test_invite@adansons.co.jp"


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


def test_create_table():
    runner = CliRunner()
    result = runner.invoke(create_table, [PROJECT_NAME])
    assert result.exit_code == 0
    assert "Your Project UID" in result.output


def test_list_project():
    runner = CliRunner()
    result = runner.invoke(list_project, [])
    assert result.exit_code == 0
    assert PROJECT_NAME in result.output


def test_show_project_detail():
    # wait create table
    time.sleep(20)
    runner = CliRunner()
    result = runner.invoke(show_project_detail, [PROJECT_NAME])
    assert result.exit_code == 0
    assert f"project {PROJECT_NAME}" in result.output


def test_import_dataset_with_invalid_rule():
    runner = CliRunner()
    result = runner.invoke(
        import_data,
        [
            PROJECT_NAME,
            "-d",
            os.path.dirname(__file__),
            "-e",
            "png",
            "-c",
            "{_}/{date}_{key}.png",
        ],
        input="{data}/{2022_04_14}_{rocket}.png",
    )
    assert result.exit_code == 0
    assert "Success!" in result.output


def test_import_dataset():
    runner = CliRunner()
    result = runner.invoke(
        import_data,
        [
            PROJECT_NAME,
            "-d",
            os.path.dirname(__file__),
            "-e",
            "jpeg",
            "-c",
            "{_}/{title}.jpeg",
        ],
    )
    assert result.exit_code == 0
    assert "Success!" in result.output


def test_import_metafile_extract():
    runner = CliRunner()
    result = runner.invoke(
        import_data,
        [
            PROJECT_NAME,
            "-m",
            "-p",
            os.path.join(os.path.dirname(__file__), "data", "sample.xlsx"),
            "--extract",
        ],
    )
    assert result.exit_code == 0
    assert "Success!" in result.output


def test_import_metafile_estimate_rule():
    runner = CliRunner()
    result = runner.invoke(
        import_data,
        [
            PROJECT_NAME,
            "-m",
            "-p",
            os.path.join(os.path.dirname(__file__), "data", "sample.xlsx"),
            "--estimate-rule",
        ],
    )
    assert result.exit_code == 0
    assert "Success!" in result.output


def test_import_metafile():
    runner = CliRunner()
    result = runner.invoke(
        import_data,
        [
            PROJECT_NAME,
            "-m",
            "-p",
            os.path.join(os.path.dirname(__file__), "data", "sample.xlsx"),
            "--auto-approve",
        ],
    )
    assert result.exit_code == 0
    assert "Success!" in result.output


def test_import_metafile_modify():
    runner = CliRunner()
    result = runner.invoke(
        import_data,
        [
            PROJECT_NAME,
            "-m",
            "-p",
            os.path.join(os.path.dirname(__file__), "data", "sample.xlsx"),
        ],
        input="m",
    )
    assert result.exit_code == 0
    assert "Success!" in result.output


def test_import_metafile_modify_join_rule_file():
    runner = CliRunner()
    result = runner.invoke(
        import_data,
        [
            PROJECT_NAME,
            "-m",
            "--join-rule",
            "joinrule_definition_adansons_test_project.yml",
        ],
        input="y",
    )
    assert result.exit_code == 0
    assert "Success!" in result.output


def test_import_metafile_exkeyvalue():
    runner = CliRunner()
    result = runner.invoke(
        import_data,
        [
            PROJECT_NAME,
            "-m",
            "-p",
            os.path.join(os.path.dirname(__file__), "data", "sample.xlsx"),
            "-a",
            "key1:value1",
            "--auto-approve",
        ],
    )
    assert result.exit_code == 0
    assert "Success!" in result.output


def test_import_metafile_exkeyvalue_multiple():
    runner = CliRunner()
    result = runner.invoke(
        import_data,
        [
            PROJECT_NAME,
            "-m",
            "-p",
            os.path.join(os.path.dirname(__file__), "data", "sample.xlsx"),
            "-a",
            "key1:value1",
            "-a",
            "key2:value2",
            "--auto-approve",
        ],
    )
    assert result.exit_code == 0
    assert "Success!" in result.output


def test_import_metafile_exkeyvalue_invalid():
    runner = CliRunner()
    result = runner.invoke(
        import_data,
        [
            PROJECT_NAME,
            "-m",
            "-p",
            os.path.join(os.path.dirname(__file__), "data", "sample.xlsx"),
            "-a",
            "key1-value1",
            "--auto-approve",
        ],
    )
    assert result.exit_code == 0
    assert "invalid" in result.output


def test_import_metafile_csv():
    runner = CliRunner()
    result = runner.invoke(
        import_data,
        [
            PROJECT_NAME,
            "-m",
            "-p",
            os.path.join(os.path.dirname(__file__), "data", "sample.csv"),
            "--auto-approve",
        ],
    )
    assert result.exit_code == 0
    assert "Success!" in result.output


def test_import_metafile_csv_exkeyvalue():
    runner = CliRunner()
    result = runner.invoke(
        import_data,
        [
            PROJECT_NAME,
            "-m",
            "-p",
            os.path.join(os.path.dirname(__file__), "data", "sample.csv"),
            "-a",
            "key1:value1",
            "--auto-approve",
        ],
    )
    assert result.exit_code == 0
    assert "Success!" in result.output


def test_import_metafile_csv_exkeyvalue_multiple():
    runner = CliRunner()
    result = runner.invoke(
        import_data,
        [
            PROJECT_NAME,
            "-m",
            "-p",
            os.path.join(os.path.dirname(__file__), "data", "sample.csv"),
            "-a",
            "key1:value1",
            "-a",
            "key2:value2",
            "--auto-approve",
        ],
    )
    assert result.exit_code == 0
    assert "Success!" in result.output


def test_data_link():
    runner = CliRunner()
    result = runner.invoke(
        data_link,
        [
            PROJECT_NAME,
            "-d",
            os.path.dirname(__file__),
            "-e",
            "jpeg",
        ],
    )
    assert result.exit_code == 0
    assert "linked!" in result.output


def test_import_metafile_csv_exkeyvalue_invalid():
    runner = CliRunner()
    result = runner.invoke(
        import_data,
        [
            PROJECT_NAME,
            "-m",
            "-p",
            os.path.join(os.path.dirname(__file__), "data", "sample.csv"),
            "-a",
            "key1-value1",
        ],
    )
    assert result.exit_code == 0
    assert "invalid" in result.output


def test_search_files():
    time.sleep(5)
    runner = CliRunner()
    result = runner.invoke(search_files, [PROJECT_NAME, "-q", "title == sample"])
    assert result.exit_code == 0
    assert "1 files" in result.output


def test_search_files_export_exception():
    time.sleep(5)
    runner = CliRunner()
    result = runner.invoke(search_files, [PROJECT_NAME, "--export"])
    assert "You can specify ‘json’" or "‘csv’ as export-file-type" in result.output


def test_get_project_member():
    runner = CliRunner()
    result = runner.invoke(show_project_detail, [PROJECT_NAME, "--member-list"])
    assert result.exit_code == 0
    assert "project Members" in result.output


def test_invite_project_member():
    runner = CliRunner()
    result = runner.invoke(
        invite_member, [PROJECT_NAME, "-m", INVITE_USER_ID, "-p", "Editor"]
    )
    assert result.exit_code == 0
    assert "Successfully" in result.output
    runner = CliRunner()
    result = runner.invoke(show_project_detail, [PROJECT_NAME, "--member-list"])
    assert result.exit_code == 0
    assert f"{INVITE_USER_ID} (Editor" in result.output


def test_change_permission():
    runner = CliRunner()
    result = runner.invoke(
        invite_member, [PROJECT_NAME, "-m", INVITE_USER_ID, "-p", "Admin", "-u"]
    )
    assert result.exit_code == 0
    assert "Successfully" in result.output
    runner = CliRunner()
    result = runner.invoke(show_project_detail, [PROJECT_NAME, "--member-list"])
    assert result.exit_code == 0
    assert f"{INVITE_USER_ID} (Admin" in result.output


# skip test_change_project_owner because it difficult to handle multi user in CLI
def test_delete_project_member():
    runner = CliRunner()
    result = runner.invoke(remove_project, [PROJECT_NAME, "-m", INVITE_USER_ID])
    assert result.exit_code == 0
    assert f"{INVITE_USER_ID} was removed from {PROJECT_NAME}" in result.output
    runner = CliRunner()
    result = runner.invoke(show_project_detail, [PROJECT_NAME, "--member-list"])
    assert result.exit_code == 0
    assert f"{INVITE_USER_ID} (Admin" not in result.output


def test_archive_project():
    runner = CliRunner()
    result = runner.invoke(remove_project, [PROJECT_NAME])
    assert result.exit_code == 0
    assert f"{PROJECT_NAME} was Archived" in result.output
    result = runner.invoke(list_project, [])
    assert result.exit_code == 0
    assert PROJECT_NAME not in result.output


def test_list_archived_project():
    runner = CliRunner()
    result = runner.invoke(list_project, ["--archived"])
    assert result.exit_code == 0
    assert PROJECT_NAME in result.output


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
    test_create_table()
    test_list_project()
    test_show_project_detail()
    test_import_dataset()
    test_import_metafile_extract()
    test_import_metafile_estimate_rule()
    test_import_metafile()
    test_import_metafile_modify()
    test_import_metafile_modify_join_rule_file()
    test_import_metafile_exkeyvalue()
    test_import_metafile_exkeyvalue_multiple()
    test_import_metafile_csv_exkeyvalue()
    test_import_metafile_csv_exkeyvalue_multiple()
    test_import_metafile_csv()
    test_data_link()
    test_import_metafile_csv_exkeyvalue_invalid()
    test_import_metafile_exkeyvalue_invalid()
    test_search_files()
    test_get_project_member()
    test_invite_project_member()
    test_change_permission()
    test_delete_project_member()
    test_archive_project()
    test_list_archived_project()
    test_delete_project()
