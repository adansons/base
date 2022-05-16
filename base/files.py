# -*- coding: utf-8 -*-

# Copyright 2022 Adansons Inc.
# Please contact engineer@adansons.co.jp
import os
import re
import json
import copy
import requests
import urllib.parse
from typing import Optional, List, Any

from base.config import (
    get_user_id,
    get_access_key,
    get_project_uid,
    BASE_API_ENDPOINT,
)

HEADER = {"Content-Type": "application/json"}
LINKER_DIR = os.path.join(os.path.expanduser("~"), ".base", "linker")


class File(str):
    """
    File class

    Attributes
    ----------
    path : str
        path of file
    attrs : dict
        dict of attributes (metadata) which related with this file

    Note
    ----
    The metadata of the file are added to the attribute.
    """

    def __new__(cls, file_path: str, attrs: dict):
        self = super().__new__(cls, file_path)
        self.path = file_path
        self.__dict__.update(attrs)
        return self

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]


class Files:
    """
    Files class

    Attributes
    ----------
    project_name : str
        registerd project name
    user_id : str
        registerd user id
    project_uid : str
        project unique hash
    conditions : str, default None
        value of the condition to search for files
    query : list of str, default []
        conditional expression of key and value to search for files
    sort_key : str, default None
        key to sort files
    result : list of dict
        search result
    files : list
        list of File class
    paths : list
        list of filepath
    items : list of dict
        metadata other than filepath
    """

    def __init__(
        self,
        project_name: str,
        conditions: Optional[str] = None,
        query: List[str] = [],
        sort_key: Optional[str] = None,
    ) -> None:
        """
        Parameters
        ----------
        project_name : str
            registerd project name
        conditions : str, default None
            value of the condition to search for files
        query : list of str, default []
            conditional expression of key and value to search for files
        sort_key : str, default None
            key to sort files
        """
        access_key = get_access_key()
        HEADER.update({"x-api-key": access_key})

        self.project_name = project_name
        self.user_id = get_user_id()
        self.project_uid = get_project_uid(self.user_id, project_name)

        self.sort_key = sort_key
        self.conditions = conditions
        self.query = query

        self.__export(conditions=conditions, query=query, sort_key=sort_key)

        self.reprtext = self.__reprtext_generator()
        self.expression = self.__class__.__name__

    def __search(
        self, conditions: Optional[str] = None, query: List[str] = []
    ) -> List[dict]:
        """
        Get metadata of filtered files from DynamoDB.

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
        result : list of dict
            search result of metadata
        """
        url = f"{BASE_API_ENDPOINT}/project/{self.project_uid}/files"
        if conditions is not None:
            url += "/" + "/".join(map(urllib.parse.quote_plus, conditions.split(",")))
        url += "?user=" + self.user_id

        res = requests.get(url=url, headers=HEADER)
        if res.status_code == 200:
            result_url = res.json()["URL"]
            result = requests.get(result_url)
            result = json.loads(result.content.decode("utf-8"))["Items"]
        else:
            raise Exception("Undefined error happend.")

        result = self.__query_filter(result, query)

        linked_hash_location = os.path.join(
            LINKER_DIR, self.project_uid, "linked_hash.json"
        )
        with open(linked_hash_location, "r", encoding="utf-8") as f:
            hash_dict = json.loads(f.read())
            result = [{"FilePath": hash_dict[i.pop("FileHash")], **i} for i in result]

        return result

    def __export(
        self,
        conditions: Optional[str] = None,
        query: List[str] = [],
        sort_key: Optional[str] = None,
    ):
        """
        Get metadata and return the File class.

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
        self : Files class instance
        """
        # arguments varidation
        self.__validate_args(conditions, query, sort_key)

        result = self.__search(conditions, query)
        if sort_key is not None:
            result = sorted(result, key=lambda x: x[sort_key])

        self.result = result
        self.__set_attributes(result)

        return self

    def filter(
        self,
        conditions: Optional[str] = None,
        query: List[str] = [],
        sort_key: Optional[str] = None,
    ):
        """
        Filter metadata and return the File class.

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
        self : Files class instance
        """
        # arguments varidation
        self.__validate_args(conditions, query, sort_key)

        filtered_files = copy.copy(self)
        filtered_files.sort_key = (
            sort_key or self.sort_key
        )  # value1 or value2 <==> value2 if value1 is None else value1
        filtered_files.conditions = conditions or self.conditions
        filtered_files.query = query + self.query

        result = filtered_files.result
        if conditions is not None:
            result = filtered_files.__conditions_filter(
                result, filtered_files.conditions
            )
        if len(query) > 0:
            result = filtered_files.__query_filter(result, filtered_files.query)
        if sort_key is not None:
            result = sorted(result, key=lambda x: x[sort_key])

        filtered_files.result = result
        filtered_files.__set_attributes(result)

        return filtered_files

    def __query_filter(self, result: List[dict], query: List[str] = []) -> List[dict]:
        """
        Filter metadata with query.

        Parameters
        ----------
        result : list of dict
            search result of metadata
        query : list of str, default []
            conditional expression of key and value to search for files

        Returns
        -------
        result : list of dict
            metadata filterd with query
        """
        for q in query:
            queried_result = []
            try:
                query_split = q.split()
                key = query_split[0]
                value = query_split[-1]
                operator = " ".join(query_split[1:-1])

                if operator in ["==", ">", ">=", "<", "<="]:
                    for data in result:
                        if key in data and eval(f"'{data[key]}' {operator} '{value}'"):
                            queried_result.append(data)
                elif operator == "!=":
                    for data in result:
                        if key in data and not eval(
                            f"'{data[key]}' {operator} '{value}'"
                        ):
                            continue
                        else:
                            queried_result.append(data)
                elif operator in ["is", "is not"]:
                    for data in result:
                        if key in data and eval(f"{data[key]} {operator} {value}"):
                            queried_result.append(data)
                elif operator in ["in", "not in"]:
                    for data in result:
                        if key in data and eval(f"'{data[key]}' {operator} {value}"):
                            queried_result.append(data)
                else:
                    raise ValueError(
                        f"Specified operator '{operator}' was blocked for the security."
                    )
            except:
                raise ValueError("Invalid query parameters.")
            else:
                result = queried_result
        return result

    def __conditions_filter(
        self, result: List[dict], conditions: Optional[str] = None
    ) -> List[dict]:
        """
        Filter metadata with conditions.

        Parameters
        ----------
        result : list of dict
            search result of metadata
        conditions : str, default None
            value of the condition to search for files

        Returns
        -------
        result : list of dict
            metadata filterd with conditions
        """
        conditions = set(conditions.split(","))
        result = [recode for recode in result if set(recode.values()) & conditions]
        return result

    def __set_attributes(self, result: List[dict]) -> None:
        """
        Set instance variables.

        Parameters
        ----------
        result : list of dict
            search result of metadata

        Returns
        -------
        None
        """
        files = []
        paths = []
        items = []
        for res in result:
            attrs = {}
            for k, v in res.items():
                if k == "FilePath":
                    path = v
                else:
                    attrs[k] = v
            file = File(path, attrs)
            files.append(file)
            paths.append(path)
            items.append(attrs)

        self.files = files  # list of File_class objects
        self.paths = paths  # list of filepaths
        self.items = items  # list of metadata_dict other than filepath

    def __validate_args(self, conditions, query, sort_key):
        if conditions is not None:
            if not isinstance(conditions, str):
                raise TypeError(
                    f'Argument "conditions" must be str, not {conditions.__class__.__name__}.'
                )
        if not hasattr(query, "__iter__"):
            raise TypeError(
                f'Argument "query" must be list, not {query.__class__.__name__}.'
            )
        if sort_key is not None:
            if not isinstance(sort_key, str):
                raise TypeError(
                    f'Argument "sort_key" must be str, not {sort_key.__class__.__name__}.'
                )

    def __getitem__(self, idx: int) -> File:
        return self.files[idx]

    def __len__(self) -> int:
        return len(self.files)

    def __repr_formatter(self, string: Optional[str]) -> Optional[str]:
        return "'" + string + "'" if string is not None else None

    def __reprtext_generator(self) -> str:
        project_name = self.__repr_formatter(self.project_name)
        conditions = self.__repr_formatter(self.conditions)
        query = self.query
        sort_key = self.__repr_formatter(self.sort_key)
        reprtext = f"{self.__class__.__name__}(project_name={project_name}, conditions={conditions}, query={query}, sort_key={sort_key}, file_num={len(self.files)})\n"
        return reprtext

    def __repr__(self) -> str:
        # if this instance is operated,
        if self.reprtext.count(self.__class__.__name__) >= 2:
            repr_header = "======Files======\n"
            expres_header = "===Expressions===\n"
            # number each File instance
            self.reprtext = re.sub(
                f"{self.__class__.__name__}[0-9]*", "{}", self.reprtext
            )
            self.expression = re.sub(
                f"{self.__class__.__name__}[0-9]*", "{}", self.expression
            )
            self.reprtext = self.reprtext.format(
                *[
                    f"{self.__class__.__name__}{i+1}"
                    for i in range(self.reprtext.count("{}"))
                ]
            )
            self.expression = self.expression.format(
                *[
                    f"{self.__class__.__name__}{i+1}"
                    for i in range(self.expression.count("{}"))
                ]
            )
            return repr_header + self.reprtext + expres_header + self.expression
        else:
            return self.reprtext

    def __add__(self, other: "Files") -> "Files":
        if isinstance(other, self.__class__):
            files = copy.copy(self)
            files.result = self.result + other.result
            files.__set_attributes(files.result)
            files.reprtext = files.reprtext + other.reprtext
            files.expression += " + " + other.expression
            files.conditions = self.conditions + "," + other.conditions
            files.query = sorted(
                set([*(self.query), *(other.query)]),
                key=[*(self.query), *(other.query)].index,
            )
            return files
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: '{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )

    def __or__(self, other: "Files") -> "Files":
        if isinstance(other, self.__class__):
            files = copy.copy(self)
            uniq_result = list(
                set(
                    map(
                        lambda x: json.dumps(sorted(x.items())),
                        [*(self.result), *(other.result)],
                    )
                ),
            )
            files.result = [dict(json.loads(result)) for result in uniq_result]
            files.__set_attributes(files.result)

            files.reprtext = files.reprtext + other.reprtext
            files_expression_count = files.expression.count(files.__class__.__name__)
            other_expression_count = other.expression.count(other.__class__.__name__)
            if files_expression_count >= 2 and other_expression_count >= 2:
                files.expression = f"({files.expression}) or ({other.expression})"
            elif files_expression_count == 1 and other_expression_count >= 2:
                files.expression = f"{files.expression} or ({other.expression})"
            elif files_expression_count >= 2 and other_expression_count == 1:
                files.expression = f"({files.expression}) or {other.expression}"
            elif files_expression_count == 1 and other_expression_count == 1:
                files.expression = f"{files.expression} or {other.expression}"
            files.conditions = self.conditions + "," + other.conditions
            files.query = sorted(
                set([*(self.query), *(other.query)]),
                key=[*(self.query), *(other.query)].index,
            )
            return files
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: '{self.__class__.__name__}' and '{other.__class__.__name__}'."
            )


if __name__ == "__main__":
    pass
