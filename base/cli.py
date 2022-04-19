# -*- coding: utf-8 -*-

# Copyright 2022 Adansons Inc.
# Please contact engineer@adansons.co.jp
import os
import sys
import time
import glob
import json

import click
from datetime import datetime

from base.project import (
    Project,
    create_project,
    get_projects,
    archive_project,
    delete_project,
)
from base.config import (
    get_user_id,
    get_access_key,
    register_access_key,
    register_user_id,
    update_project_info,
    get_user_id_from_db,
)


def base_config(func):
    def wrapper(*args, **kwargs):
        # Try get user_id
        try:
            access_key = get_access_key()
            user_id = get_user_id()
            update_project_info(user_id)
        except:
            click.echo(
                "Welcome to Adansons Base!!\n\nLet's start with your access key provided on our slack.\n(if you don't have access key, please press ENTER.)\n"
            )
            while True:
                try:
                    access_key = click.prompt(
                        "Please register your access key", type=str, default="none"
                    )
                    if access_key == "none":
                        print(
                            "\nGet invitation from here!\n-> https://share.hsforms.com/16OxTF7eJRPK92oGCny7nGw8moen\n"
                        )
                        sys.exit()
                except click.exceptions.Abort:
                    click.echo("\nAborted!")
                    sys.exit()

                try:
                    register_access_key(access_key)
                    user_id = get_user_id_from_db(access_key)
                    register_user_id(user_id)
                    update_project_info(user_id)
                except click.exceptions.Abort:
                    click.echo("\nAborted!")
                    sys.exit()
                except:
                    click.echo(
                        "\nIncorrect access key was specified, please re-configure or ask support team.\n"
                    )
                else:
                    click.echo(f"\nSuccessfully configured as {user_id}\n")
                    time.sleep(3)
                    kwargs["user_id"] = user_id
                    break
        else:
            kwargs["user_id"] = user_id

        func(*args, **kwargs)

    return wrapper


@click.group()
def main():
    """Adansons Database Command Line Interface"""
    pass


@main.command(name="new", help="create new project")
@click.argument("project")
@base_config
def create_table(project, user_id):
    """
    Create a new project table command
    Usage
    -----
    $ base new sample-project
    Arguments
    ---------
    project: str
        new project name
    parameters
    ----------
    user_id : str
        registerd user id
    Returns
    -------
    project_uid : str
        project unique hash
    """
    try:
        project_uid = create_project(user_id, project)
    except Exception as e:
        print(e)
    else:
        click.echo(
            f"Your Project UID\n----------------\n{project_uid}\n\nsave Project UID in local file (~/.base/projects)"
        )
        return project_uid


@main.command(name="list", help="show project list")
@click.option("--archived", is_flag=True)
@base_config
def list_project(archived, user_id):
    """
    Show project list command
    Usage
    -----
    $ base list
    Parameters
    ----------
    user_id : str
        registerd user id
    archived : bool
        if you want show archived projects
    """

    try:
        project_list = get_projects(user_id, archived=archived)
    except Exception as e:
        print(e)
    else:
        click.echo("projects\n========")
        for project in project_list:
            private = "yes" if project["PrivateProject"] == "1" else "no"
            created_date = datetime.fromtimestamp(
                float(project["CreatedTime"])
            ).strftime("%Y-%m-%d %H:%M:%S")
            click.echo(
                f"[{project['ProjectName']}]\nProject UID: {project['ProjectUid']}\nRole: {project['UserRole']}\nPrivate Project: {private}\nCreated Date: {created_date}"
            )


@main.command(name="rm", help="remove project")
@click.argument("project")
@click.option("--confirm", is_flag=True)
@click.option(
    "-m",
    "--member",
    type=str,
    help="member id you want to remove from project",
    required=False,
    default=None,
    multiple=True,
)
@base_config
def remove_project(confirm, project, user_id, member):
    """
    Delete a project command
    Usage
    -----
    $ base rm sample-project
    Arguments
    ---------
    project : str
        project name wich you want to delete
    Parameters
    ----------
    user_id : str
        registerd user id
    Options
    -------
    confirm : bool
        if you want delete archived projects
    member : list
        if you want remove project member from project
    """
    if not member:
        if confirm:
            try:
                delete_project(user_id, project)
            except Exception as e:
                print(e)

            else:
                click.echo(f"{project} was Deleted")
        else:

            try:
                archive_project(user_id, project)
            except Exception as e:
                print(e)
            else:
                click.echo(f"{project} was Archived")
    else:

        pjt = Project(project)
        try:
            pjt.remove_member(member)
        except Exception as e:
            print(e)
        else:
            click.echo(f"{','.join(member)} was removed from {project}")


@main.command(name="show", help="show project detail")
@click.argument("project")
@click.option("--member-list", is_flag=True)
@base_config
def show_project_detail(project, user_id, member_list):
    """

    Show project detail command
    Usage
    -----
    $ base show sample-project
    Arguments
    ---------
    project : str
        project name wich you are interested in
    Parameters
    ----------
    user_id : str
        registerd user id
    Optinons
    --------
    member_list : bool
        if you want see about project members
    """
    pjt = Project(project)
    if not member_list:

        try:
            key_list = pjt.get_metadata_summary()
        except Exception as e:
            print(e)
        else:
            click.echo(f"projects {project}\n===============")
            for column in key_list:
                click.echo(column)
    else:
        try:
            member_list = pjt.get_members()
        except Exception as e:
            print(e)
        else:
            click.echo("project Members\n===============")
            for column in member_list:
                created_date = datetime.fromtimestamp(
                    float(column["CreatedTime"])
                ).strftime("%Y-%m-%d %H:%M:%S")
                click.echo(
                    f'{column["UserID"]} ({column["UserRole"]}, invited at {created_date})'
                )


@main.command(name="import", help="import dataset into project")
@click.argument("project")
@click.option(
    "-m",
    "--external-file",
    help="flag for external meta-data file",
    is_flag=True,
    default=False,
)
@click.option(
    "-p",
    "--path",
    help="path for external meta-data file",
    required=False,
    default=None,
)
@click.option(
    "-d",
    "--directory",
    type=str,
    help="target directory path",
    required=False,
    default=None,
)
@click.option(
    "-e",
    "--extension",
    type=str,
    help="target file extensions",
    required=False,
    default=None,
)
@click.option(
    "-c", "--parse", type=str, help="path parsing rule", required=False, default=None
)
@click.option(
    "-a",
    "--additional",
    type=str,
    help="additional key and value",
    required=False,
    default=None,
    multiple=True,
)
@click.option("--auto-approve", is_flag=True)
@base_config
def import_data(
    project,
    external_file,
    path,
    directory,
    extension,
    parse,
    additional,
    auto_approve,
    user_id,
):
    """
    Import data file command
    Usage
    -----
    $ base import sample-project -d ../dataset -e wav -c {timestamp}/{UID}-{condition}-{iteration}.wav
    If you want to import meta-data from an external file :
    $ base import sample-project --external-file your/path/to_data
    Arguments
    ---------
    project : str
        project name wich you are interested in
    Parameters
    ----------
    user_id : str
        registerd user id
    directory : str, default=None
    extension : str, default=None
    parse : str, default=None
    additional : tuple of str, default=None
    auto_approve : bool, default=False
        approve estimated table joining rule
    """
    if additional is None:
        additional = {}
    else:
        try:
            additional = {
                element.split(":")[0]: element.split(":")[1] for element in additional
            }
        except:
            click.echo(
                "Found invalid argument in -x. The argument must be : -x key:value"
            )
        else:
            import_metafile(
                project, path, additional, auto_approve
            ) if external_file else import_dataset(
                project, directory, extension, parse, additional
            )


def import_dataset(project, directory, extension, parse, additional):
    pjt = Project(project)
    if directory is None:
        directory = click.prompt(
            "Where is your dataset? (select root of dataset directory)", type=str
        )
    if extension is None:
        extension = []
        extension = click.prompt(
            "What is your data file extension? (ex: csv, jpg, png, wav)", type=str
        )
        if extension[0] == ".":
            extension = extension[1:]

    click.echo("Check datafiles...")
    files = glob.glob(os.path.join(directory, "**", f"*.{extension}"), recursive=True)
    click.echo(f"found {len(files)} files with {extension} extension.")

    if parse is None:
        sample_file_path = files[0].split(directory)[-1]
        if sample_file_path[0] == os.sep:
            sample_file_path = sample_file_path[1:]
        click.echo(
            f"\nTell me parsing rule for get meta data from file path with '{extension}'.\n\
* you can use {{key-name}} to parse phrases with key.\n\
* you can use {{_}} to ignore some phrases.\n\
* you have to use '/' as separator.\n\
** sample parsing rule: {{_}}/{{name}}/{{timestamp}}/{{sensor}}-{{condition}}_{{iteration}}.csv\n\
path to your file: {sample_file_path}"
        )
        parse = click.prompt("Parsing rule", type=str)

    try:
        pjt.add_datafiles(
            directory,
            extension,
            attributes=additional,
            parsing_rule=parse,
            detail_parsing_rule=None,
        )
    except ValueError as e:
        print(e)
        click.echo(
            f"\nCan't parse uniquely with parsing rule: {parse}.\n\
Please tell me detail parsing rule in accordance with the actual path.\n\
* use {{value}} to parse phrases with value in the actual path\n\
* put {{}} before/after the value corresponding to {{_}} on the original parsing rule.\n\
** original parsing rule: {{_}}/{{name}}/{{timestamp}}/{{sensor}}-{{condition}}_{{iteration}}.csv\n\
** example path: Origin/suzuki/2020-04-07/A200-C_50.csv\n\
** sample detail parsing rule: {{Origin}}/{{suzuki}}/{{2022-04-07}}/{{A200}}-{{C}}_{{50}}.csv\n\
path to your file: {files[0].split(directory)[-1]}"
        )
        detail_parse = click.prompt("Detail parsing rule", type=str)

        try:
            pjt.add_datafiles(
                directory,
                extension,
                attributes=additional,
                parsing_rule=parse,
                detail_parsing_rule=detail_parse,
            )
        except Exception as e:
            print(e)
        else:
            click.echo("Success!")
    except Exception as e:
        print(e)
    else:
        click.echo("Success!")


def import_metafile(project, path, additional, auto_approve):
    pjt = Project(project)

    if path is None:
        path = click.prompt(
            "Where is your meta-data file? (select a path for an external meta-data file)",
            type=str,
        )
    try:
        pjt.add_metafile(
            file_path=path, attributes=additional, auto=auto_approve, verbose=True
        )
    except Exception as e:
        print(e)
    else:
        click.echo("Success!")


@main.command(name="search", help="search files")
@click.argument("project")
@click.option(
    "-q",
    "--query",
    type=str,
    help="query key value pair and operator. you have to specify like 'key >= value'",
    required=False,
    multiple=True,
)
@click.option(
    "-c",
    "--conditions",
    type=str,
    help="query value. you have to specify as 'value1,value2,...'",
    required=False,
)
@click.option("-e", "--export", type=str, help="export file type", required=False)
@click.option("-o", "--output", type=str, help="output file path", required=False)
@click.option("-s", "--summary", is_flag=True)
@base_config
def search_files(
    project,
    query,
    conditions,
    export,
    output,
    user_id,
    summary,
):
    """
    Query database
    Usage
    -----
    $ base search sample-project -q "key >= xxxxx" -c yyy,zzz
    Arguments
    ---------
    project : str
        project name wich you are interested in
    Parameters
    ----------
    user_id : str
        registerd user id
    query : str
    conditions : str
    Options
    -------
    summary : bool
        if you want hide detail
    """
    pjt = Project(project)
    try:
        if conditions is not None:
            result = pjt.files(conditions=conditions, query=query).result
        else:
            result = pjt.files(query=query).result
    except Exception as e:
        print(e)
    else:
        click.echo(f"{len(result)} files")
        if not summary:
            click.echo("========")
            for r in result:
                click.echo(r)
        if export is not None:
            if export.lower() == "json":
                output_json = json.dumps({"Data": result}, indent=4, ensure_ascii=False)

                output_path = os.path.join(".", "dataset.json")
                if output is not None:
                    output_path = output
                    os.makedirs(os.path.dirname(output), exist_ok=True)

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(output_json)
            elif export.lower() == "csv":
                result_keys = list(result[0].keys())
                output_csv = ",".join(result_keys)
                for r in result:
                    result_values = [r[k] for k in result_keys]
                    output_csv += "\n" + ",".join(result_values)

                output_path = os.path.join(".", "dataset.csv")
                if output is not None:
                    output_path = output
                    os.makedirs(os.path.dirname(output), exist_ok=True)

                with open(output_path, "w") as f:
                    f.write(output_csv)
            else:
                click.echo(f"Sorry, export file type: {export} was not supprted yet...")


@main.command(name="invite", help="invite project member")
@click.argument("project")
@click.option(
    "-m", "--member", type=str, help="member id you want to invite", required=True
)
@click.option(
    "-p",
    "--permission",
    type=str,
    help="permission level, select from 'Viewer', 'Editor', 'Admin', 'Owner'",
    required=True,
)
@click.option("-u", "--update", is_flag=True)
@base_config
def invite_member(project, member, permission, update, user_id):
    """
    Invite project member
    Usage
    -----
    $ base invite sample-project -m MEMBER -p Editor
    Arguments
    ---------
    project : str
        project name wich you want to invite to
    Parameters
    ----------
    user_id : str
        registerd user id
    member : str
        user id who you want invite
    permission : str
        permission level you want to give the member
    Options
    -------
    update : bool
        if you want update permission exsisting project member
    """
    pjt = Project(project)
    if not update:
        try:
            pjt.add_member(member, permission)
        except Exception as e:
            print(e)
        else:
            click.echo(f"Successfully invited {member} into {project} as {permission}")
    else:
        try:
            pjt.update_member(member, permission)
        except Exception as e:
            print(e)
        else:
            click.echo(f"Successfully update {member}'s permission to {permission}")


@main.command(name="link", help="import dataset into project")
@click.argument("project")
@click.option(
    "-d",
    "--directory",
    type=str,
    help="target directory path",
    required=False,
    default=None,
)
@click.option(
    "-e",
    "--extension",
    type=str,
    help="target file extensions",
    required=False,
    default=None,
)
@base_config
def data_link(project, directory, extension, user_id):
    """
    Create linker metadat to local datafiles.
    Usage
    -----
    $ base link sample-project -d ../dataset -e wav
    Arguments
    ---------
    project : str
        project name wich you are interested in
    Parameters
    ----------
    user_id : str
        registerd user id
    directory : str, default=None
    extension : str, default=None
    """
    pjt = Project(project)
    if directory is None:
        directory = click.prompt(
            "Where is your dataset? (select root of dataset directory)", type=str
        )
    if extension is None:
        extension = []
        extension = click.prompt(
            "What is your data file extension? (ex: csv, jpg, png, wav)", type=str
        )
        if extension[0] == ".":
            extension = extension[1:]

    try:
        file_num = pjt.link_datafiles(directory, extension)
    except Exception as e:
        print(e)
    else:
        click.echo("Check datafiles...")
        click.echo(f"found {file_num} files with {extension} extension.")
        click.echo("linked!")


if __name__ == "__main__":
    main()
