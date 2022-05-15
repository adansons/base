# -*- coding: utf-8 -*-

# Copyright 2022 Adansons Inc.
# Please contact engineer@adansons.co.jp
import os
import json
import glob
import math
import base64
import requests
from typing import Optional, List, Union

from base.files import Files
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
            self.project_name, conditions=conditions, query=query, sort_key=sort_key
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

            if not parser.is_path_parsable(
                files[0].split(dir_path)[-1].replace(os.sep, "/")
            ):
                raise ValueError(
                    "Failed to parse path with specified rule. tell me detail parsing rule."
                )

        for f in files:
            meta_data = {}

            # calculation hash value and update meta data dictionary
            hash_value = calc_file_hash(f)
            meta_data["FileHash"] = hash_value
            hash_dict[hash_value] = (
                os.path.abspath(f).replace(os.sep, "/").replace("/", os.sep)
            )
            meta_data.update(attributes)

            if parser is not None:
                meta_data_from_path = parser(f.split(dir_path)[-1].replace(os.sep, "/"))
                meta_data.update(meta_data_from_path)

            data_list.append(meta_data)
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

        for s in range(split_count):
            items = {"Items": data_list[s * split_data_num : (s + 1) * split_data_num]}
            url = f"{BASE_API_ENDPOINT}/project/{self.project_uid}?user={self.user_id}"
            res = requests.post(url, json.dumps(items), headers=HEADER)

            if res.status_code != 200:
                raise Exception("Failed to upload meta data.")

        file_num = len(data_list)
        return file_num

    def add_metafile(
        self,
        file_path: str,
        attributes: dict = {},
        join_rule: dict = {},
        auto: bool = False,
        verbose: bool = True,
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
                "New table key 2": "ADD:" + "Exist table key 2", <- if you have mew value on exist key
                "New table key 3": None <- if you have new key
            }
        auto : bool (default False)
            if True, skip to get confirmation
        verbose : bool (default True)
            if True, show detail of each actions result
            if you turn off auto mode, you will always get detail for confirmation

        Raises
        ------
        ValueError
            raises if specified external file is not csv or excel file
        Exception
            raises if something went wrong on uploading request to server
        """
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
        if verbose:
            print(f"{len(tables)} tables found!")
            print("now estimating the rule for table joining...\n")

        # get update_rule for each table
        if not join_rule:
            update_rules = []
            for table in tables:
                url = f"{BASE_API_ENDPOINT}/project/{self.project_uid}?user={self.user_id}"
                payload = {"Items": table}
                res = requests.put(url, json.dumps(payload), headers=HEADER)
                if res.status_code != 200:
                    raise Exception("Failed to estimate the joining rule")

                update_rule = res.json()["UpdateRule"]
                update_rules.append(json.dumps(update_rule, ensure_ascii=False))

            table_rule_pair = {}
            for table, update_rule in zip(tables, update_rules):
                if update_rule in table_rule_pair:
                    table_rule_pair[update_rule].append(table)
                else:
                    table_rule_pair[update_rule] = [table]
            if verbose:
                print(f"{len(table_rule_pair)} table joining rule was estimated!")
        else:
            if len(tables) != 1:
                raise ValueError(
                    "You can use join_rule option when you have only 1 table on external file."
                )
            table_rule_pair = {json.dumps(join_rule, ensure_ascii=False): tables}
        if verbose:
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
            approved = True if input("\tEnter a value: ") == "y" else False
        else:
            approved = True

        # update records
        if approved:
            for update_rule, tables in table_rule_pair.items():
                update_rule = json.loads(update_rule)
                update_rule_for_add = {}
                for key, value in update_rule.items():
                    if value:
                        update_rule_for_add[key] = value
                    else:
                        update_rule_for_add[key] = f"ADD:{key}"
                url = f"{BASE_API_ENDPOINT}/project/{self.project_uid}/files?user={self.user_id}"
                for i, table in enumerate(tables):
                    if i == 0:
                        payload = {"Items": table, "UpdateRule": update_rule}
                    else:
                        payload = {"Items": table, "UpdateRule": update_rule_for_add}
                    res = requests.put(
                        url, json.dumps(payload, ensure_ascii=False).encode('utf-8'), headers=HEADER
                    )
                    if res.status_code != 200:
                        raise Exception("Failed to join the tables")
        else:
            raise Exception("Aborted!")

    def get_metadata_summary(self) -> List[dict]:
        """
        Get list of meta data information.

        Returns
        -------
        key_list : list
            list of each keys information
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
            list of each members information
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
                        "ValueType": attr["UpperValue"],
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
                                "ValueType": attr["UpperValue"],
                                "RecordedCount": attr["RecordedCount"],
                            }

                        elif len(candidates) == pre_length:
                            continue
                        else:
                            pre_cache.append(c | {key_name})
                    pre_cache.append({key_name})
                    cache = pre_cache
        return attrs


if __name__ == "__main__":
    pass
