# -*- coding: utf-8 -*-

# Copyright 2022 Adansons Inc.
# Please contact engineer@adansons.co.jp
import re
from typing import List, Optional


class Parser:
    """
    The class of path parsing.
    Instance Args
    -----------------
    self.sep: str
        Path separator

    self.parsing_rule: str
        Path parsing rule

    self.splitters: List
        The list of splitters in the parsing rule.
        ex.) `["-", "/", "_"]`

    self.split_counts: List
        The list of the number of splitters included in each value of detail parsing rule.
        You input the detail parsing rule ({Origin}/{2022_04_05}-{dog}_{1}.png).
        Then, self.split_counts is `[0, 2, 0, 0]`.

    self.unuse_strs: List
        The list of the number of unuse strings in the parsing rule.
        You input the parsing rule (hoge{num1}/fuga{num2}.txt).
        Then, self.unuse_strs is `["hoge", "fuga"]`.
    """

    def __init__(self, parsing_rule: str, extension: str, sep: Optional[str] = None) -> None:
        """
        Parameters
        ----------
        parsing_rule : str
            specified parsing rule
            ex.) {_}/{name}/{timestamp}/{sensor}-{condition}_{iteration}.csv
            * phrase in "{}" will be interpretered as key
            * "{_}" will be ignored
        sep : str, default={"/", "¥"}
            path separator char. this depends on the Operating System
        """
        if sep is None:
            self.sep = "/"
        else:
            self.sep = sep

        self.parsing_rule = parsing_rule
        self.extension = extension
        self.__generate_parser()

    def __generate_parser(self, is_update: bool = False) -> None:
        """
        Generate parsing keys and pattern from parsing rule
        Parameters (instance vars)
        --------------------------
        self.parsing_rule : str
            specified parsing rule
            ex.) {_}/{name}/{timestamp}/{sensor}-{condition}_{iteration}.csv
            * phrase in "{}" will be interpretered as key
            * "{_}" will be ignored
        is_update : bool
            whether to update the parse rule
        Returns (instance vars)
        -----------------------
        self.parsing_keys : list
            list of keys
            ex.) ["_", "name", "timestamp", "sensor", "condition", "iteration"]
        """
        # 正規表現"(.*)"は任意の文字の任意回数の繰り返し
        # "{(.*)}"とすることで、{}に囲まれた文字列を抽出できる
        # しかし、複数{}がある時に、どの"{"と"}"の組み合わせを取れば良いかわからない
        # "{(.*?)}"と?をつけることで、最小文字数の文字列を囲んだ{}をpickupできる
        self.parsing_rule = self.convert_parsable_parse_rule()

        parsing_keys = re.findall("{(.*?)}", self.parsing_rule)
        splitters = self.extract_splitter()

        if is_update:
            split_counts = self.count_splitter_in_each_key(parsing_keys)
        else:
            split_counts = [0] * len(parsing_keys)

        self.splitters = splitters
        self.split_counts = split_counts

        if not is_update:
            self.parsing_keys = parsing_keys

    def __call__(self, path: str) -> dict:
        """
        Parse path with generated parser
        Parameters
        ----------
        path : str
            required the file path
        Returns
        -------
        parsed_dict : dict
            meta data dictionary
        Example
        -------
        >>> from base.parser import Parser
        >>> parser = Parser("your parsing rule")
        >>> result = parser("your target path for parse")
        """
        if path.startswith(self.sep):
            path = (self.sep).join(path.split(self.sep)[1:])

        # ユーザーから取得したparsing_ruleを元に
        # hoge/2022-03-14/A-200-A-a-01 から
        # {hoge}/{2022-03-14}/{A-200}-{A}-{a-01}　に変換する
        # "{(.*?)}"で{}内の値を抽出できるので良きみ
        path = self.convert_path_to_parsable_format(path)
        parsed_values = re.findall("{(.*?)}", path)

        parsed_dict = {}
        for key, value in zip(self.parsing_keys, parsed_values):
            if key in ["_", "[UnuseToken]"]:
                continue
            parsed_dict[key] = value

        return parsed_dict

    def update_rule(self, parsing_rule: str) -> None:
        """
        Update parsing rule and re-generate parsing keys and pattern
        Parameters
        ----------
        parsing_rule : str
            specified parsing rule
            ex.) {_}/{name}/{timestamp}/{sensor}-{condition}_{iteration}.csv
            * phrase in "{}" will be interpretered as key
            * "{_}" will be ignored
        """
        self.parsing_rule = parsing_rule
        self.__generate_parser(is_update=True)

    def is_path_parsable(self, path: str) -> bool:
        """
        Check path is parsable
        Parameters
        ---------------------
        path : str
            ex) `dataset/dog/2022_12_04-A.png`
        Return
        ---------------------
        parsable_flag : bool
        """
        if path.startswith(self.sep):
            path = (self.sep).join(path.split(self.sep)[1:])

        parsable_flag = True
        try:
            path = self.convert_path_to_parsable_format(path)
        except:
            parsable_flag = False

        return parsable_flag

    def convert_parsable_parse_rule(self) -> str:
        """
        Replace unused strings in `parsing_rule` with `{_}`

        Return
        ---------------------
        parsable_parsing_rule: str
            ex.) `{_}/{num1}/{fuga}/{num2}.txt`
        """
        if not self.parsing_rule.endswith("."+self.extension):
            self.parsing_rule += "."+self.extension

        self.unuse_strs = self.extract_unuse_str()

        for not_use_str in self.unuse_strs:
            self.parsing_rule = self.parsing_rule.replace(not_use_str, "{[UnuseToken]}")

        self.parsing_rule = self.parsing_rule.replace("}{", "}" + self.sep + "{")

        parsable_parsing_rule = self.parsing_rule
        return parsable_parsing_rule

    def convert_path_to_parsable_format(self, path: str) -> str:
        """
        Convert path to parsable format
        1. Insert separators before and after unuse strings.
        2. Enclose the value to be extracted in the path with  `{}`.
            - Add `{` after separator `/` to `parsable_format_path`.
            - The condition of adding `}` to `parsable_format_path`.
                - Before the separator was added.
                - When the number of splitters, added to the `parsable_format_path` after `{`,
                 is the number determined by parsing_rule

        Parameters
        ---------------
        path : str
            ex.) `Origin/suzuki/2022_12_03/A-20-C-100.csv`
        Return
        --------------
        parsable_format_path : str
            strings converted for path-parse
            ex.) `{Origin}/{suzuki}/{2022_12_03}/{A-200}-{C}-{100}.csv`
        """
        closure_cnt, split_cnt = 0, 0

        path = self.insert_sep_to_path(path)

        parsable_format_path = "{"
        for s in path:
            if (s in self.splitters) and (split_cnt == self.split_counts[closure_cnt]):
                parsable_format_path += "}" + s + "{"
                closure_cnt += 1
                split_cnt = 0

            else:
                if s in self.splitters:
                    split_cnt += 1
                parsable_format_path += s

        return parsable_format_path

    def extract_sub_splitters(self) -> List:
        """
        Extract strings not enclosed in `{}`
        Returns
        -----------------
        candidate_splitters : List
            ex) `["hoge", "/fuga"]`
        """
        parsing_rule_ = self.parsing_rule

        # switch `{XX}` to `}XX{`
        parsing_rule_ = parsing_rule_.replace("{", "[RPTRight]").replace(
            "}", "[RPTLeft]"
        )
        parsing_rule_ = parsing_rule_.replace("[RPTRight]", "}").replace(
            "[RPTLeft]", "{"
        )
        parsing_rule_ = "{" + parsing_rule_ + "}"

        sub_splitters = re.findall(r"\{(.*?)\}", parsing_rule_)

        return sub_splitters

    def extract_splitter(self) -> List:
        """
        Find splitters such as '/', '-' or '_' etc...

        Return
        ---------------------
        splitters : list
            ex) `["/", "/", "/", "-", "_", "."]`
        """
        sub_splitters = self.extract_sub_splitters()

        code_pattern = re.compile("[!-/:-@[-`{-~]")

        splitters = []
        for sub_sp in sub_splitters:
            sp = re.findall(code_pattern, sub_sp)
            splitters.extend(sp)

        return splitters

    def extract_unuse_str(self) -> List:
        """
        Find not use strings for value.
        Return
        ---------------------
        unuse_strs : List
            ex) `["hoge", "fuga"]`
        """
        sub_splitters = self.extract_sub_splitters()
        str_pattern = re.compile("[^!-/:-@[-`{-~]+")

        unuse_strs = []
        for sub_sp in sub_splitters:
            strs = re.findall(str_pattern, sub_sp)
            unuse_strs.extend(strs)

        return unuse_strs

    def count_splitter_in_each_key(self, values: List) -> List:
        """
        Count the number of splitters in each keys
        Parameters
        ----------------
        values : List
            The list of values extracted from the `path`
            ex.) `["hoge", "/fuga"]` (path: hoge{num1}/fuga{num2}.txt)

        Retern
        ---------------
        split_cnts : List
            The list of the number of splitters in each key
            ex.) `
        """
        split_cnts = []
        for value in values:
            split_in_value = 0
            if value != "_":
                for split in set(self.splitters):
                    split_in_value += value.count(split)
            split_cnts.append(split_in_value)

        return split_cnts

    def insert_sep_to_path(self, path: str) -> str:
        """
        Insert splitter before/after `unuse_str` in the path
        Parameters
        ------------------
        path : str
            ex.) `Origin/hoge1/fugasuzukipiyo_03.csv`
        Returns
        ------------------
        path : str
            ex.) `{Origin}/{hoge}/{1}/{fuga}/{suzuki}/{piyo}_{03}.csv`
        """
        for unuse_str in self.unuse_strs:
            path = path.replace(unuse_str, self.sep + unuse_str + self.sep)

        path = path.replace(self.sep * 3, self.sep)
        
        splitters = sorted(list(set(self.splitters)))

        # Put "/" at the last position in `splitters`        
        if self.sep in splitters:
            splitters.remove(self.sep)
            splitters.append(self.sep)

        for splitter in splitters:
            path = path.replace(splitter + self.sep, self.sep).replace(
                self.sep + splitter, self.sep
            )

        return path

    def validate_parsing_rule(self) -> bool:
        """
        Check that the parsing_rule is valid
        Parameter
        ----------------
        self.parsing_keys

        Return
        ----------------
        is_valid : bool
        """
        if len(self.parsing_keys) == 0:
            is_valid = False
        elif len(self.parsing_keys) == 1 and self.parsing_keys[0] == "[UnuseToken]":
            is_valid = False
        else:
            is_valid = True
        return is_valid


if __name__ == "__main__":
    pass
