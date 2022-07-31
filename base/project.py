# -*- coding: utf-8 -*-

# Copyright 2022 Adansons Inc.
# Please contact engineer@adansons.co.jp
import os
import json
import ruamel.yaml
import glob
import math
import base64
import requests
from typing import Optional, List, Union
import time
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from colorama import Fore, init

from base.files import Files
from base.spinner import Spinner
from base.parser import Parser
from base.hash import calc_file_hash
from base.config import (
    get_user_id,
    get_access_key,
    get_project_uid,
    check_project_exists,
    register_project_uid,
    delete_project_config,
    BASE_API_ENDPOINT,
)

# colorama settings
init(autoreset=True)

HEADER = {"Content-Type": "application/json"}
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".base", "projects")
LINKER_DIR = os.path.join(os.path.expanduser("~"), ".base", "linker")


def create_project(user_id: str, project_name: str, private: bool = True) -> str:
    """
    Create new project.

    Parameters
    ----------
    user_id : str
        registerd user id
    project_name : str
        project name wich you want to create
    private : bool, default True
        whether to publish the project or not

    Returns
    -------
    project_uid : str
        project unique hash

    Raises
    ------
    Exception
        raises if something went wrong on request to server
    """
    if check_project_exists(user_id, project_name):
        raise ValueError(f"Project {project_name} is already exists.")

    project_info = {"ProjectName": project_name, "PrivateProject": int(private)}
    access_key = get_access_key()
    HEADER.update({"x-api-key": access_key})
    res = requests.post(
        f"{BASE_API_ENDPOINT}/projects?user={user_id}",
        json.dumps(project_info),
        headers=HEADER,
    )
    if res.status_code == 200:
        project_uid = res.json()["ProjectUid"]
        register_project_uid(user_id, project_name, project_uid)
        return project_uid
    else:
        raise Exception(f"{res.status_code} : Something went wrong")


def get_projects(user_id: str, archived: bool = False) -> List[dict]:
    """
    Get list of projects.

    Parameters
    ----------
    user_id : str
        registerd user id
    private : bool, default True
        whether to publish the project or not

    Returns
    -------
    project_list : list
        list of project name you have

    Raises
    ------
    Exception
        raises if something went wrong on request to server
    """
    access_key = get_access_key()
    HEADER.update({"x-api-key": access_key})
    url = f"{BASE_API_ENDPOINT}/projects?user={user_id}"
    if archived:
        url += "&archived=1"
    res = requests.get(url, headers=HEADER)
    if res.status_code == 200:
        project_list = res.json()["Projects"]
        return project_list
    else:
        raise Exception(f"{res.status_code} : Something went wrong")


def archive_project(user_id: str, project_name: str):
    """
    Archive project.

    Parameters
    ----------
    user_id : str
        registerd user id
    project_name : str
        project name you want to archive

    Raises
    ------
    Exception
        raises if something went wrong on request to server
    """
    access_key = get_access_key()
    HEADER.update({"x-api-key": access_key})
    project_uid = get_project_uid(user_id, project_name)
    url = f"{BASE_API_ENDPOINT}/project/{project_uid}?user={user_id}"
    res = requests.delete(url, headers=HEADER)

    if res.status_code != 200:
        raise Exception(f"{res.status_code} : Something went wrong")


def delete_project(user_id: str, project_name: str):
    """
    Delete project.

    Parameters
    ----------
    user_id : str
        registerd user id
    project_name : str
        archived project name you want to delete

    Raises
    ------
    Exception
        raises if something went wrong on request to server
    """
    access_key = get_access_key()
    HEADER.update({"x-api-key": access_key})
    project_uid = get_project_uid(user_id, project_name)
    url = f"{BASE_API_ENDPOINT}/project/{project_uid}/confirm?user={user_id}"
    res = requests.delete(url, headers=HEADER)

    if res.status_code == 200:
        delete_project_config(user_id, project_name)
    else:
        raise Exception(f"{res.status_code} : Something went wrong")


class Project:
    """
    Project class

    Attributes
    ----------
    project_name : str
        Registerd project name
    user_id : str
        registerd user id
    project_uid : str
        project unique hash
    """

    def __init__(self, project_name: str) -> None:
        """
        Parameters
        ----------
        project_name : str
            Registerd project name
        """
        access_key = get_access_key()
        HEADER.update({"x-api-key": access_key})

        self.project_name = project_name
        self.user_id = get_user_id()
        self.project_uid = get_project_uid(self.user_id, project_name)
        self.attrs = self.__summarize_attributes()

    def files(
        self,
        conditions: Optional[str] = None,
        query: List[str] = [],
        sort_key: Optional[str] = None,
    ) -> Files:
        """
        Generate Files clase instance.

        Parameters
        ----------
        conditions : str, default None
            value of the condition to search for files
        query : list of str, default []
            conditional expression of key and value to search for files
        sort_key : str, default None
            key to sort files

        Returns
        -------
        files : Files class instance
        """
        files = Files(
            self.project_name,
            conditions=conditions,
            query=query,
            sort_key=sort_key,
        )
        return files

    def add_datafile(
        self,
        file_path: str,
        attributes: dict,
    ) -> None:
        """
        Import meta data of one file.

        1. Calculate the file hash.
        2. Create meta data record with the file hash, attributes, and parsed path data.
        3. Add that record into project database table.
        [record]
        {
            "FileHash": String,
            "MetaKey1": ...,
            ...
        }

        Parameters
        ----------
        file_path : str
            the file path
        attributes : dict
            meta data of the specified file

        Raises
        ------
        Exception
            raises if something went wrong on uploading request to server
        """
        meta_data = {}
        hash_dict = {}

        # calculation hash value and update meta data dictionary
        hash_value = calc_file_hash(file_path)
        meta_data["FileHash"] = hash_value
        hash_dict[hash_value] = (
            os.path.abspath(file_path).replace(os.sep, "/").replace("/", os.sep)
        )
        meta_data.update(attributes)

        # create local datafile linker
        linked_hash_location = os.path.join(
            LINKER_DIR, self.project_uid, "linked_hash.json"
        )
        os.makedirs(os.path.dirname(linked_hash_location), exist_ok=True)

        if os.path.exists(linked_hash_location):
            with open(linked_hash_location, "r", encoding="utf-8") as f:
                exist_hash_dict = json.loads(f.read())
                exist_hash_dict.update(hash_dict)
        else:
            exist_hash_dict = hash_dict

        with open(linked_hash_location, "w", encoding="utf-8") as f:
            json.dump(exist_hash_dict, f, ensure_ascii=False, indent=4)

        # upload into database
        item = {"Items": [meta_data]}
        url = f"{BASE_API_ENDPOINT}/project/{self.project_uid}?user={self.user_id}"
        res = requests.post(url, json.dumps(item), headers=HEADER)

        if res.status_code != 200:
            raise Exception("Failed to upload meta data.")

    def add_datafiles(
        self,
        dir_path: str,
        extension: str,
        attributes: dict = {},
        parsing_rule: Optional[str] = None,
        detail_parsing_rule: Optional[str] = None,
    ) -> int:
        """
        Import meta data related with datafile paths.

        1. Calculate the file hash.
        2. Parse the file path with `parsing-rule`.
        3. Create meta data records with the file hash, attributes, and parsed path data.
        4. Add that records into project database table.
        [record]
        {
            "FileHash": String,
            "MetaKey1": ...,
            ...
        }

        Parameters
        ----------
        dir_path : str
            the root directory path for datafiles
        extension : str
            the extension of datafiles
        attributes : dict (default {})
            the extra meta data (attributes) combined with whole datafiles
        parsing_rule : str (default None)
            the rule for extracting meta data from datafile path
            ex.) {_}/{disease}/{patient-id}-{part}-{iteration}.png
        detail_parsing_rule : str (default None)
            detail information about parsing rule
            ex.) {_}/{CancerA}/{1-123}-{1}-{100}.png

        Returns
        -------
        file_num : int
            number of imported datafiles

        Raises
        ------
        ValueError
            raises if invalid parsing rule was specified
        Exception
            raises if something went wrong on uploading request to server
        """
        if extension[0] == ".":
            extension = extension[1:]
        files = glob.glob(
            os.path.join(dir_path, "**", f"*.{extension}"), recursive=True
        )
        data_list = []
        hash_dict = {}

        parser = None
        if parsing_rule is not None:
            parser = Parser(parsing_rule)
            if detail_parsing_rule is not None:
                parser.update_rule(detail_parsing_rule)
            if not parser.validate_parsing_rule():
                raise Exception(
                    f"This parsing rule is not valid.\n\
Make sure that the key is enclosed with `{{}}` in the parsing_rule."
                )
            if not parser.is_path_parsable(
                files[0].split(dir_path)[-1].replace(os.sep, "/")
            ):
                raise ValueError(
                    "Failed to parse path with specified rule. tell me detail parsing rule."
                )

        def calc_hash(file):
            meta_data = {}

            # calculation hash value and update meta data dictionary
            hash_value = calc_file_hash(file)
            meta_data["FileHash"] = hash_value
            hash_dict[hash_value] = (
                os.path.abspath(file).replace(os.sep, "/").replace("/", os.sep)
            )
            meta_data.update(attributes)

            if parser is not None:
                meta_data_from_path = parser(
                    file.split(dir_path)[-1].replace(os.sep, "/")
                )
                meta_data.update(meta_data_from_path)

            data_list.append(meta_data)

        with Spinner(
            text="Calculating filehashs...", etext="Calculating filehashs... Done."
        ), ThreadPoolExecutor(max_workers=2) as executor:
            for file in files:
                executor.submit(calc_hash, file)

        # create local datafile linker
        linked_hash_location = os.path.join(
            LINKER_DIR, self.project_uid, "linked_hash.json"
        )
        os.makedirs(os.path.dirname(linked_hash_location), exist_ok=True)

        if os.path.exists(linked_hash_location):
            with open(linked_hash_location, "r", encoding="utf-8") as f:
                exist_hash_dict = json.loads(f.read())
                exist_hash_dict.update(hash_dict)
        else:
            exist_hash_dict = hash_dict

        with open(linked_hash_location, "w", encoding="utf-8") as f:
            json.dump(exist_hash_dict, f, ensure_ascii=False, indent=4)

        # divide and upload into database
        limit_record_size = 10000
        split_count = math.ceil(len(data_list) / limit_record_size)
        split_data_num = math.ceil(len(data_list) / split_count)
        file_num = len(data_list)

        lap_time = []
        for s in range(split_count):
            mean_lap_time = 25 if not lap_time else sum(lap_time) // len(lap_time)
            minute = (split_count - s) * mean_lap_time // 60
            second = (split_count - s) * mean_lap_time % 60
            text = f"{s*10000}/{file_num}, estimated time: {minute}m {second}s"

            items = {"Items": data_list[s * split_data_num : (s + 1) * split_data_num]}
            url = f"{BASE_API_ENDPOINT}/project/{self.project_uid}?user={self.user_id}"

            start = time.time()
            etext = (
                "Uploading data... Done." if len(lap_time) == split_count - 1 else ""
            )
            with Spinner(text=f"Uploading data... {text}", etext=etext):
                res = requests.post(url, json.dumps(items), headers=HEADER)
                if res.status_code != 200:
                    raise Exception("Failed to upload meta data.")

            end = time.time()
            lap_time.append(int(end - start))

        return file_num

    def extract_metafile(
        self,
        file_path: str,
        attributes: dict = {},
        verbose: int = 2,
    ):
        """
        Extract meta data from external file.

        Parameters
        ----------
        file_path : str
            the external file path
        attributes : dict (default {})
            the extra meta data (attributes) combined with whole datafiles
        verbose : int (default 2)
            if verbose==2, show detail of each action result
            if verbose==1, show summary of each action result

        Returns
        -------
        tables: list
            list of data extracted from external-file

        Raises
        ------
        ValueError
            raises if specified external file is not csv or excel file
        Exception
            raises if something went wrong on uploading request to server
        """
        _, ext = os.path.splitext(file_path)
        tmp_file_path = os.path.join(
            os.path.dirname(file_path), f"tmp_{os.path.basename(file_path)}"
        )
        if ext.lower() == ".csv":
            df = pd.read_csv(file_path, header=0)
            if "FilePath" in df:
                linked_hash_location = os.path.join(
                    LINKER_DIR, self.project_uid, "linked_hash.json"
                )
                with open(linked_hash_location, "r", encoding="utf-8") as f:
                    exist_hash_dict = json.loads(f.read())
                path_to_hash = {v: k for k, v in exist_hash_dict.items()}
                df["FileHash"] = df["FilePath"].apply(lambda x: path_to_hash[x])
                del df["FilePath"]
                df.to_csv(tmp_file_path, encoding="utf-8", index=False)
            else:
                tmp_file_path = file_path
        elif ext.lower() == ".xlsx":
            tmp_file_path = file_path
        else:
            raise ValueError(
                f"{ext} file is not supported. Currently only suports csv or xlsx file."
            )

        with open(tmp_file_path, "rb") as f:
            data = f.read()

        if tmp_file_path != file_path:
            os.remove(tmp_file_path)

        data = base64.b64encode(data).decode()
        item = {"Items": data}
        item["is_csv"] = 1 if ext == ".csv" else 0
        item["common_keyvalue"] = attributes

        with Spinner("extracting tables...", overwrite=False):
            _, ext = os.path.splitext(file_path)
            if ext.lower() not in [".csv", ".xlsx"]:
                raise ValueError(
                    f"{ext} file is not supported. Currently only suports csv or xlsx file."
                )

            with open(file_path, "rb") as f:
                data = f.read()

            data = base64.b64encode(data).decode()
            item = {"Items": data}
            item["is_csv"] = 1 if ext == ".csv" else 0
            item["common_keyvalue"] = attributes

            # extract and parse external file
            url = f"{BASE_API_ENDPOINT}/project/{self.project_uid}/meta_file?user={self.user_id}"
            res = requests.post(url, json.dumps(item), headers=HEADER)
            if res.status_code != 200:
                raise Exception("Failed to extract and parse external file.")

            s3_presigned_url = res.json()["URL"]
            res = requests.get(s3_presigned_url)
            tables = res.json()["Items"]

        if verbose != 0:
            print(f"{len(tables)} tables found! ({file_path})\n")
        if verbose == 2:
            for i, table in enumerate(tables, 1):
                print(f"===== New Table{i} =====\n{summarize_parsed_table(table)}\n")
        return tables

    def estimate_join_rule(
        self,
        tables: Optional[list] = None,
        file_path: Optional[str] = None,
        verbose: int = 2,
    ):
        """
        Estimate join rule from external file and existing table.

        Parameters
        ----------
        tables : list
            list of data extracted from external-file
        file_path : str
            the external file path
        verbose : bool (default True)
            if verbose==2, show detail of each action result
            if verbose==1, show summary of each action result

        Raises
        ------
        ValueError
            raises if specified external file is not csv or excel file
        Exception
            raises if something went wrong on uploading request to server
        """
        if not (tables or file_path):
            raise ValueError("You have to specify 'tables' or 'file_path'.")

        if tables is None:
            tables = []
            _, ext = os.path.splitext(file_path)
            if ext.lower() not in [".csv", ".xlsx"]:
                raise ValueError(
                    f"{ext} file is not supported. Currently only suports csv or xlsx file."
                )
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    csv_data = f.read()
                key = csv_data.split("\n")[0].split(",")
                values = csv_data.split("\n")[1:]
                table = []
                for value in values:
                    table.append({key[i]: v for i, v in enumerate(value.split(","))})
                tables.append(table)
            except:
                if verbose != 0:
                    print(
                        "Specified file looks like messy. Base will extract tables from it."
                    )
                extracted_tables = self.extract_metafile(file_path=file_path, verbose=1)
                tables += extracted_tables

        with Spinner("now estimating the rule for table joining...", overwrite=False):
            join_rules = []
            for table in tables:
                url = f"{BASE_API_ENDPOINT}/project/{self.project_uid}?user={self.user_id}"
                payload = {"Items": table}
                res = requests.put(url, json.dumps(payload), headers=HEADER)
                if res.status_code != 200:
                    raise Exception("Failed to estimate the joining rule")

                join_rule = res.json()["UpdateRule"]
                join_rules.append(json.dumps(join_rule, ensure_ascii=False))

        if verbose != 0:
            print(f"{len(join_rules)} table joining rule was estimated! ({file_path})")
        if verbose == 2:
            for i, join_rule in enumerate(join_rules):
                print(f"\nRule no.{i+1}")
                for new_key, exist_key in json.loads(join_rule).items():
                    if exist_key:
                        print(
                            f"\tkey '{new_key}'\t->\tconnected to '{exist_key}' key on exist table"
                        )
                    else:
                        print(f"\tkey '{new_key}'\t->\tnewly added")
                print(f"\nTable {i+1} sample record:\n\t{tables[i-1][0]}\n")

        return join_rules

    def add_metafile(
        self,
        file_path: Optional[tuple] = None,
        attributes: dict = {},
        join_rule: dict = {},
        auto: bool = False,
        join_rule_path: str = None,
        verbose: int = 1,
    ) -> None:
        """
        Import meta data from external file.

        Parameters
        ----------
        file_path : str
            the external file path
        attributes : dict (default {})
            the extra meta data (attributes) combined with whole datafiles
        join_rule : dict (default {})
            the rule for table joining
            {
                "New table key 1": "Exist table key 1", <- if you have same key on new and exist tables
                "New table key 2": "ADD:" + "Exist table key 2", <- if you have new value on exist key
                "New table key 3": None <- if you have new key
            }
        auto : bool (default False)
            if True, skip to get confirmation
        verbose : bool (default True)
            if True, show detail of each action result
            if you turn off auto mode, you will always get detail for confirmation

        Raises
        ------
        ValueError
            raises if specified external file is not csv or excel file or invalid YML file specified as join_rule_path
        Exception
            raises if something went wrong on uploading request to server
        """
        if join_rule_path:
            try:
                with open(join_rule_path, "r", encoding="utf-8") as yf:
                    join_rules = ruamel.yaml.safe_load(yf)["Body"]
                file_path = [rule["FilePath"] for rule in list(join_rules.values())]
                file_path = sorted(set(file_path), key=file_path.index)
            except:
                raise ValueError("Invalid YAML file. Unable to read FilePath.")

        tables = []
        tables_from_path = []
        for path in file_path:
            # extract table from meta file
            tables_ = self.extract_metafile(
                file_path=path, attributes=attributes, verbose=verbose
            )
            tables_from_path += [path] * len(tables_)
            tables += tables_

        # get update_rule for each table
        if not (join_rule or join_rule_path):
            join_rules = self.estimate_join_rule(tables=tables, verbose=0)
            table_rule_pair = {}
            for table, join_rule in zip(tables, join_rules):
                if join_rule in table_rule_pair:
                    table_rule_pair[join_rule].append(table)
                else:
                    table_rule_pair[join_rule] = [table]
        elif join_rule:
            if len(tables) != 1:
                raise ValueError(
                    "You can use join_rule option when you have only 1 table on external file."
                )
            table_rule_pair = {json.dumps(join_rule, ensure_ascii=False): tables}
        elif join_rule_path:
            try:
                with open(join_rule_path, "r", encoding="utf-8") as yf:
                    join_rules = ruamel.yaml.safe_load(yf)["Body"]

                join_rules = [
                    json.dumps(rule["JoinRules"], ensure_ascii=False)
                    for rule in list(join_rules.values())
                ]
                table_rule_pair = {}
                for table, join_rule in zip(tables, join_rules):
                    if join_rule in table_rule_pair:
                        table_rule_pair[join_rule].append(table)
                    else:
                        table_rule_pair[join_rule] = [table]
            except:
                raise ValueError("Invalid YAML file.Unable to read JoinRules.")

        if verbose == 1:
            print(f"{len(table_rule_pair)} table joining rule was estimated!\n")
            print("Below table joining rule will be applied...\n\n")
            for i, update_rule in enumerate(list(table_rule_pair.keys())):
                print(f"Rule no.{i+1}\n")
                for new_key, exist_key in json.loads(update_rule).items():
                    if exist_key:
                        print(
                            f"\tkey '{new_key}'\t->\tconnected to '{exist_key}' key on exist table"
                        )
                    else:
                        print(f"\tkey '{new_key}'\t->\tnewly added")
                tables = table_rule_pair[update_rule]
                print(f"\n{len(tables)} tables will be applied")
                for j, table in enumerate(tables):
                    print(f"Table {j+1} sample record:\n\t{table[0]}")
        if not auto:
            print(
                "\nDo you want to perform table join?\n\tBase will join tables with that rule described above.\n"
            )
            print("\t'y' will be accepted to approve.\n")
            if not join_rule_path:
                print(
                    "\tIf you need to modify it, please enter 'm'\n\t\tDefinition YML file with estimated table join rules will be downloaded, then you can modify it and apply the new join rule."
                )
            approved = input("\tEnter a value: ")
        else:
            approved = "y"

        # update records
        if approved == "y":
            for update_rule, tables in table_rule_pair.items():
                update_rule = json.loads(update_rule)
                update_rule_for_add = {}
                for key, value in update_rule.items():
                    if value:
                        update_rule_for_add[key] = value
                    else:
                        update_rule_for_add[key] = f"ADD:{key}"
                url = f"{BASE_API_ENDPOINT}/project/{self.project_uid}/files?user={self.user_id}"

                with Spinner(
                    text="Joining tables...",
                    etext=f"{len(tables)} tables have been joined!",
                ):
                    for i, table in enumerate(tables):
                        if i == 0:
                            payload = {"Items": table, "UpdateRule": update_rule}
                        else:
                            payload = {
                                "Items": table,
                                "UpdateRule": update_rule_for_add,
                            }
                        try:
                            res = requests.get(
                                url=url,
                                data=json.dumps(payload),
                                headers=HEADER,
                                timeout=20,
                            )
                        except:
                            is_completed = False
                            while not is_completed:
                                res = requests.get(
                                    url=f"{BASE_API_ENDPOINT}/project/{self.project_uid}/tables/status/contents?user={self.user_id}",
                                    headers=HEADER,
                                )
                                if res.status_code != 200:
                                    raise Exception(
                                        "Something went wrong. Please try again."
                                    )
                                status = res.json()["ContensStatus"]
                                if status == "Updating":
                                    time.sleep(2)
                                elif status == "Available":
                                    is_completed = True
                                else:  # Failure
                                    raise Exception("Failed to join the tables")

        elif approved == "m" and (not join_rule_path):
            join_rules_info = {
                "RequestedTime": time.time(),
                "ProjectName": self.project_name,
                "Body": {},
            }
            for i, rule in enumerate(join_rules, 1):
                join_rules_info["Body"][f"Table{i}"] = {
                    "FilePath": os.path.abspath(tables_from_path[i - 1]),
                    "JoinRules": json.loads(rule),
                }

            yaml_str = ruamel.yaml.round_trip_dump(
                join_rules_info, default_flow_style=False
            )
            yaml_str += """\n# [Description]
                        \n# By modifying the Body/Table/JoinRules section, you can define a new join rule.
                        \n# Fundamentally, this section consists of Key-Value Pairs. 
                        \n# Key is the key name from the new table. Value is the key name from the existing table.\n
                        \n# "New table key 1": "Exist table key 1", <- if you have same key on new and exist tables
                        \n# "New table key 2": "ADD:" + "Exist table key 2", <- if you have new value on exist key
                        \n# "New table key 3":   , <- if you have new key, no need to specify anything\n
                        \n# [Example]
                        \n#  JoinRules:
                        \n#   first_name: name
                        \n#   age: ADD:Age
                        \n#   height:\n
                        \n# The Key-Value above defines 3 join-rules. 
                        \n# 1. "first_name: name" means to join the new key named "first_name" with the existing key named "name".
                        \n#    If you have same key on the new and the existing tables, write like this.
                        \n# 2. "age: ADD:Age" means to add new values of the new key named 'age' on the existing key named 'Age'.
                        \n#    If you have new value on the existing key, write like this.
                        \n# 3. "height: " means to add the key named "height" as a new key.
                        \n#    If the new key is not in the existing table, write like this."""

            yaml = ruamel.yaml.YAML()
            yaml.default_flow_style = True
            yaml_str = yaml.load(yaml_str)
            file_name = f"joinrule_definition_{self.project_name}.yml"
            file_count = 1
            while True:
                if os.path.exists(file_name):
                    file_name = (
                        f"joinrule_definition_{self.project_name} ({file_count}).yml"
                    )
                    file_count += 1
                else:
                    break
            with open(file_name, "w", encoding="utf-8") as yf:
                yaml.dump(yaml_str, yf)

            print(
                Fore.BLUE
                + f"\nDownloaded a YAML file '{file_name}' in current directory.\n"
                f"Key information for the new table and the existing table is as follows.\n\n"
            )
            for i, table in enumerate(tables, 1):
                print(f"===== New Table{i} =====\n{summarize_parsed_table(table)}\n")

            print(f"===== Existing Table =====")
            summary_for_print = summarize_keys_information(self.get_metadata_summary())
            max_len_list = [
                summary_for_print["MaxCharCount"][column]
                for column in summary_for_print["Keys"][0]
            ]
            for row in summary_for_print["Keys"]:
                print(
                    "  ".join(
                        [
                            content + " " * (length - len(content))
                            for content, length in zip(row, max_len_list)
                        ]
                    )
                )

            attr_str = ""
            if attributes:
                for attr in list(attributes.items()):
                    attr_str += " --additional " + ":".join(attr)

            print(
                Fore.BLUE + f"\nYou can apply the new join-rule according to 2 steps.\n"
                f"1. Modify the file '{file_name}'. Open the file to see a detailed description.\n"
                f"2. Execute the following command.\n   base import {self.project_name} --external-file{attr_str} --join-rule {file_name}\n"
            )
        else:
            raise Exception("Aborted!")

    def get_metadata_summary(self) -> List[dict]:
        """
        Get list of meta data information.

        Returns
        -------
        key_list : list
            list of each key information
            [
                {
                    "KeyHash": String,
                    "KeyName": String,
                    "ValueHash": String,
                    "ValueType": String,
                    "RecordedCount": Integer,
                    "UpperValue": String,
                    "LowerValue": String,
                    "CreatedTime": String of unix time,
                    "LastModifiedTime": String of unix time,
                    "Creator": String,
                    "LastEditor": String,
                    "EditerList": List of String
                },
                ...
            ]

        Raises
        ------
        Exception
            raises if something went wrong with request to server
        """
        url = f"{BASE_API_ENDPOINT}/project/{self.project_uid}?user={self.user_id}"
        res = requests.get(url, headers=HEADER)

        if res.status_code == 200:
            key_list = res.json()["Items"]
            return key_list
        else:
            raise Exception("Failed to get meta data information.")

    def link_datafiles(self, dir_path: str, extension: str) -> int:
        """
        Create linker metadat to local datafiles.

        Parameters
        ----------
        dir_path : str
            the root directory path for datafiles
        extension : str
            the extension of datafiles

        Returns
        -------
        file_num : int
            number of linked datafiles
        """
        if extension[0] == ".":
            extension = extension[1:]
        files = glob.glob(
            os.path.join(os.path.abspath(dir_path), "**", f"*.{extension}"),
            recursive=True,
        )

        hash_dict = {}
        for f in files:
            hash_value = calc_file_hash(f)
            hash_dict[hash_value] = f.replace(os.sep, "/").replace("/", os.sep)

        linked_hash_location = os.path.join(
            LINKER_DIR, self.project_uid, "linked_hash.json"
        )
        os.makedirs(os.path.dirname(linked_hash_location), exist_ok=True)

        if os.path.exists(linked_hash_location):
            with open(linked_hash_location, "r", encoding="utf-8") as f:
                exist_hash_dict = json.loads(f.read())
                exist_hash_dict.update(hash_dict)
        else:
            exist_hash_dict = {}

        exist_hash_dict.update(hash_dict)

        with open(linked_hash_location, "w", encoding="utf-8") as f:
            json.dump(exist_hash_dict, f, ensure_ascii=False, indent=4)

        file_num = len(files)
        return file_num

    def add_member(self, member: str, permission_level: str) -> None:
        """
        Invite a new project member.

        Parameters
        ----------
        member : str
            the user id of new member
        permission_level : str
            new member's permission level
            - Viewer
                only read meta data on project database.
                viewer can not import data files or external files
                and can not control permission of other members.
            - Editor
                can read and write meta data into project database.
                editor can not control permission of other members.
            - Admin
                can read and write meta data into project database.
                admin can also control permission of other members,
                but can not transfer Owner permission level.

        Raises
        ------
        ValueError
            raises if invalid permission level was specified
        Exception
            raises if something went wrong on invite request to server
        """
        permission_level = permission_level.capitalize()
        if permission_level == "Owner":
            raise ValueError(
                "You can only change member's permission to 'Owner' with update_member method."
            )
        elif permission_level not in ["Viewer", "Editor", "Admin"]:
            raise ValueError(
                "Invalid permission level was specified. Please choose from Viewer, Editor or Admin"
            )

        member_info = {"TargetUserID": member, "NewUserRole": permission_level}
        url = (
            f"{BASE_API_ENDPOINT}/project/{self.project_uid}/member?user={self.user_id}"
        )
        res = requests.post(url, json.dumps(member_info), headers=HEADER)
        if res.status_code != 200:
            raise Exception(f"Failed to invite {member}.")

    def update_member(self, member: str, permission_level: str) -> None:
        """
        Update project member's permission.

        Parameters
        ----------
        member : str
            the user id of existing member
        permission_level : str
            member's permission level for update
            - Viewer
                only read meta data on project database.
                viewer can not import data files or external files
                and can not control permission of other members.
            - Editor
                can read and write meta data into project database.
                editor can not control permission of other members.
            - Admin
                can read and write meta data into project database.
                admin can also control permission of other members,
                but can not transfer Owner permission level.
            - Owner
                can transfer owner permission to others,
                and delete project completely.

        Raises
        ------
        ValueError
            raises if invalid permission level was specified
        Exception
            raises if something went wrong on invite request to server
        """
        permission_level = permission_level.capitalize()
        if permission_level not in ["Viewer", "Editor", "Admin", "Owner"]:
            raise ValueError(
                "Invalid permission level was specified. Please choose from Viewer, Editor, Admin or Owner"
            )

        member_info = {"NewUserRole": permission_level}
        url = f"{BASE_API_ENDPOINT}/project/{self.project_uid}/member/{member}?user={self.user_id}"
        res = requests.put(url, json.dumps(member_info), headers=HEADER)
        if res.status_code != 200:
            raise Exception(f"Failed to update {member}'s permission.")

    def get_members(self) -> List[dict]:
        """
        Get list of project members.

        Returns
        -------
        member_list : list
            list of each member information
            [
                {
                    "UserID": String,
                    "UserRole": String,
                    "CreatedTime": String of unix time
                },
                ...
            ]

        Raises
        ------
        Exception
            raises if something went wrong with request to server
        """
        url = (
            f"{BASE_API_ENDPOINT}/project/{self.project_uid}/member?user={self.user_id}"
        )
        res = requests.get(url, headers=HEADER)

        if res.status_code == 200:
            member_list = res.json()["Members"]
            return member_list
        else:
            raise Exception("Failed to get project members.")

    def remove_member(self, member: Union[str, List[str]]) -> None:
        """
        Remove project member.

        Parameters
        ----------
        member : list or str
            the target member for removing

        Raises
        ------
        Exception
            raises if something went wrong on removing request to server
        """
        if isinstance(member, str):
            member = [member]

        for m in member:
            url = f"{BASE_API_ENDPOINT}/project/{self.project_uid}/member/{m}?user={self.user_id}"
            res = requests.delete(url, headers=HEADER)

            if res.status_code != 200:
                raise Exception(f"Failed to remove {m} from {self.project_name}")

    def __summarize_attributes(self) -> dict:
        """
        Remove project member.

        Returns
        -------
        attrs : dict
            dict of summarized attrs
            {'key': {'LowerValue': 'LowerValue',
                'UpperValue': 'EditorList',
                'ValueType': 'Creator',
                'RecordedCount': 'ValueHash'},
                'body,weight': {'LowerValue': 'LowerValue',
                'UpperValue': 'EditorList',
                'ValueType': 'Creator',
                'RecordedCount': 'ValueHash'},
                'height,pet': {'LowerValue': 'LowerValue',
                'UpperValue': 'EditorList',
                'ValueType': 'Creator',
                'RecordedCount': 'ValueHash'},
                'pet,weight': {'LowerValue': 'LowerValue',
                'UpperValue': 'EditorList',
                'ValueType': 'Creator',
                'RecordedCount': 'ValueHash'}}
        """
        attr_list = self.get_metadata_summary()
        key_response = {}
        for attr in attr_list:
            if attr["KeyHash"] in key_response:
                key_response[attr["KeyHash"]].append(attr["KeyName"])
            else:
                key_response[attr["KeyHash"]] = [attr["KeyName"]]

        key_name_to_hash = {}
        for key_hash, key_names in key_response.items():
            created_keys = []
            count = 0
            for key_name in key_names:
                if key_name.startswith("BASE:"):
                    created_keys.append(key_name)
                else:
                    count += 1
            if created_keys and count > 0:
                for created_key in created_keys:
                    key_names.remove(created_key)
            for key_name in key_names:
                if key_name in key_name_to_hash:
                    key_name_to_hash[key_name].add(key_hash)
                else:
                    key_name_to_hash[key_name] = {key_hash}

        attrs = {}
        for key_hash, key_names in key_response.items():
            cache = []
            for key_name in key_names:
                if len(key_name_to_hash[key_name]) == 1:
                    attr = [i for i in attr_list if i["KeyHash"] == key_hash][0]
                    attrs[key_name] = {
                        "LowerValue": attr["LowerValue"],
                        "UpperValue": attr["UpperValue"],
                        "ValueType": attr["ValueType"],
                        "RecordedCount": attr["RecordedCount"],
                    }

                else:
                    pre_cache = []
                    for c in cache:
                        candidates = key_name_to_hash[key_name].copy()
                        pre_length = len(candidates)
                        for k in c:
                            candidates &= key_name_to_hash[k]
                        if len(candidates) == 1:
                            attr = [i for i in attr_list if i["KeyHash"] == key_hash][0]
                            attrs[",".join(sorted(c | {key_name}))] = {
                                "LowerValue": attr["LowerValue"],
                                "UpperValue": attr["UpperValue"],
                                "ValueType": attr["ValueType"],
                                "RecordedCount": attr["RecordedCount"],
                            }

                        elif len(candidates) == pre_length:
                            continue
                        else:
                            pre_cache.append(c | {key_name})
                    pre_cache.append({key_name})
                    cache = pre_cache
        return attrs


def summarize_keys_information(metadata_summary: List[dict]) -> dict:
    """
    Summarize information of keys on project for printing.

    Parameters
    ----------
    metadata_summary : list
        output of base.Project().get_metadata_summary() method
        it is raw output of MetaKeyTable on DynamoDB
        so some records will have a same KeyHash (separated)
        [
            {
                "KeyHash": String,
                "KeyName": String,
                "ValueHash": String,
                "ValueType": String,
                "RecordedCount": Integer,
                "UpperValue": String,
                "LowerValue": String,
                "CreatedTime": String of unix time,
                "LastModifiedTime": String of unix time,
                "Creator": String,
                "LastEditor": String,
                "EditerList": List of String
            },
            ...
        ]

    Returns
    -------
    summary_for_print : dict
        summarized key information for printing
        {
            "MaxRecordedCount": Integer,
            "UniqueKeyCount": Integer,
            "MaxCharCount": {
                "KEY NAME": Integer,
                "VALUE RANGE": Integer,
                "VALUE TYPE": Integer,
                "RECORDED COUNT": Integer
            },
            "Keys": [
                (
                    KeyName: String,
                    ValueRange: String,
                    ValueType: String,
                    RecordedCount: String
                )
            ]
        }
    """
    keyhash_to_summary = {}
    for key_record in metadata_summary:
        key_hash = key_record["KeyHash"]
        if key_hash in keyhash_to_summary:
            keyhash_to_summary[key_hash]["KeyName"].add(key_record["KeyName"])
            value_type = key_record["ValueType"]
            if value_type in keyhash_to_summary[key_hash]["ValueType"]:
                keyhash_to_summary[key_hash]["ValueType"][value_type].add(
                    "'{}'".format(key_record["KeyName"])
                )
            else:
                keyhash_to_summary[key_hash]["ValueType"][value_type] = {
                    "'{}'".format(key_record["KeyName"])
                }
        else:
            keyhash_to_summary[key_hash] = {
                "KeyName": {key_record["KeyName"]},
                "LowerValue": key_record["LowerValue"],
                "UpperValue": key_record["UpperValue"],
                "ValueType": {
                    key_record["ValueType"]: {"'{}'".format(key_record["KeyName"])}
                },
                "RecordedCount": key_record["RecordedCount"],
            }

    recorded_count_list = []
    char_count = {
        "KEY NAME": [8],  # length of "KEY NAME"
        "VALUE RANGE": [11],  # length of "VALUE RANGE"
        "VALUE TYPE": [10],  # length of "VALUE TYPE"
        "RECORDED COUNT": [14],  # length of "RECORDED COUNT"
    }
    summary_list = [("KEY NAME", "VALUE RANGE", "VALUE TYPE", "RECORDED COUNT")]
    for key_summary in keyhash_to_summary.values():
        key_name_summary = ",".join(
            sorted([f"'{name}'" for name in key_summary["KeyName"]])
        )
        value_range_summary = (
            f'{key_summary["LowerValue"]} ~ {key_summary["UpperValue"]}'
        )
        value_type_summary = ", ".join(
            [
                f"{vtype}({','.join(list(name_list))})"
                for vtype, name_list in key_summary["ValueType"].items()
            ]
        )

        summary = (
            key_name_summary,
            value_range_summary,
            value_type_summary,
            str(key_summary["RecordedCount"]),
        )
        summary_list.append(summary)

        char_count["KEY NAME"].append(len(key_name_summary))
        char_count["VALUE RANGE"].append(len(value_range_summary))
        char_count["VALUE TYPE"].append(len(value_type_summary))
        char_count["RECORDED COUNT"].append(len(str(key_summary["RecordedCount"])))

        recorded_count_list.append(key_summary["RecordedCount"])

    summary_for_print = {
        "MaxRecordedCount": max(recorded_count_list) if recorded_count_list else 0,
        "UniqueKeyCount": len(summary_list) - 1,
        "MaxCharCount": {
            "KEY NAME": max(char_count["KEY NAME"]),
            "VALUE RANGE": max(char_count["VALUE RANGE"]),
            "VALUE TYPE": max(char_count["VALUE TYPE"]),
            "RECORDED COUNT": max(char_count["RECORDED COUNT"]),
        },
        "Keys": summary_list,
    }

    return summary_for_print


def summarize_parsed_table(table: List[dict]) -> str:
    """
    Summarize information of extracted table from external file for printing.

    Parameters
    ----------
    tables : list
        list of data extracted from external-file

    Returns
    -------

    summary_for_print : str
        summarized table information
    """

    def select_vtype(vtype_list: list) -> str:
        if "str" in vtype_list:
            return "str"
        elif "float" in vtype_list:
            return "float"
        elif "int" in vtype_list:
            return "int"
        elif "bool" in vtype_list:
            return "bool"
        else:
            return "None"

    dic = {}
    for data in table:
        for k, v in data.items():
            if dic.get(k):
                dic[k].append(v)
            else:
                dic[k] = [v]

    table_summary = {}
    for k in dic.keys():
        unique_value = sorted(set(dic[k]))
        key_summary = {
            "UpperValue": unique_value[-1],
            "LowerValue": unique_value[0],
            "ValueType": select_vtype(
                list(set(vt.__class__.__name__ for vt in unique_value))
            ),
            "RecordedCount": len(dic[k]),
        }
        table_summary[k] = key_summary

    char_count = {
        "KEY NAME": [8],  # length of "KEY NAME"
        "VALUE RANGE": [11],  # length of "VALUE RANGE"
        "VALUE TYPE": [10],  # length of "VALUE TYPE"
        "RECORDED COUNT": [14],  # length of "RECORDED COUNT"
    }
    summary_list = [("KEY NAME", "VALUE RANGE", "VALUE TYPE", "RECORDED COUNT")]
    for key_name, key_summary in table_summary.items():
        value_range_summary = (
            f'{key_summary["LowerValue"]} ~ {key_summary["UpperValue"]}'
        )
        value_type_summary = f"{key_summary['ValueType']}('{key_name}')"
        summary = (
            f"'{key_name}'",
            value_range_summary,
            value_type_summary,
            str(key_summary["RecordedCount"]),
        )
        summary_list.append(summary)
        char_count["KEY NAME"].append(len(f"'{key_name}'"))
        char_count["VALUE RANGE"].append(len(value_range_summary))
        char_count["VALUE TYPE"].append(len(value_type_summary))
        char_count["RECORDED COUNT"].append(len(str(key_summary["RecordedCount"])))

    max_len_list = [max(char_count[column]) for column in summary_list[0]]
    summary_for_print = "\n".join(
        "  ".join(
            [
                content + " " * (length - len(content))
                for content, length in zip(row, max_len_list)
            ]
        )
        for row in summary_list
    )
    return summary_for_print


if __name__ == "__main__":
    pass
