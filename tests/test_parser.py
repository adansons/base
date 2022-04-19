# -*- coding: utf-8 -*-

# Copyright 2022 Adansons Inc.
# Please contact engineer@adansons.co.jp

import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from base.parser import Parser


INPUT_PATH1 = "Origin/左声帯嚢胞/1-055-E-a01.wav"
PARSING_RULE1 = "{_}/{disease}/{_}-{patient-id}-{part}-{iteration}.wav"
PARSING_KEYS1 = ["_", "disease", "_", "patient-id", "part", "iteration"]
PARSED_DICT1 = {
    "disease": "左声帯嚢胞",
    "patient-id": "055",
    "part": "E",
    "iteration": "a01",
}

INPUT_PATH2 = "Origin/hoge1/fugasuzukipiyo_03.csv"
PARSING_RULE2 = "{_}/hoge{num1}/fuga{name}piyo_{month}.csv"
CONVERTED_PARSING_RULE2 = "{_}/{_}/{num1}/{_}/{name}/{_}_{month}.csv"
PARSING_KEYS2 = ["_", "_", "num1", "_", "name", "_", "month"]
PARSED_DICT2 = {"num1": "1", "name": "suzuki", "month": "03"}

INPUT_PATH3 = "Origin/hoge1/fugasuzukipiyo_2022_03_02.csv"
PARSING_RULE3 = "{_}/hoge{num1}/fuga{name}piyo_{timestamp}.csv"
DETAIL_PARSING_RULE = "{Origin}/hoge{1}/fuga{suzuki}piyo_{2022_03_02}.csv"
PARSING_KEYS3 = ["_", "_", "num1", "_", "name", "_", "timestamp"]
PARSED_DICT3 = {"num1": "1", "name": "suzuki", "timestamp": "2022_03_02"}


def test_generate_parser_pattern1():
    parser = Parser(PARSING_RULE1)
    assert parser.parsing_keys == PARSING_KEYS1


def test_parse_pattern1():
    parser = Parser(PARSING_RULE1)
    parsed_dict = parser(INPUT_PATH1)
    assert parsed_dict == PARSED_DICT1


def test_generate_parser_pattern2():
    parser = Parser(PARSING_RULE2)
    assert parser.parsing_keys == PARSING_KEYS2
    assert parser.parsing_rule == CONVERTED_PARSING_RULE2


def test_parse_pattern2():
    parser = Parser(PARSING_RULE2)
    parsed_dict = parser(INPUT_PATH2)
    assert parsed_dict == PARSED_DICT2


def test_generate_parser_pattern3():
    parser = Parser(PARSING_RULE3)
    parser.update_rule(DETAIL_PARSING_RULE)
    assert parser.parsing_keys == PARSING_KEYS3


def test_parse_pattern3():
    parser = Parser(PARSING_RULE3)
    parser.update_rule(DETAIL_PARSING_RULE)
    parsed_dict = parser(INPUT_PATH3)
    assert parsed_dict == PARSED_DICT3


def test_is_path_parsable():
    parser = Parser(PARSING_RULE3)

    # Check for `IndexError` when parsing the file path with invalid `parsing_rule`.
    with pytest.raises(Exception) as e:
        _ = parser(INPUT_PATH3)
    assert str(e.value) == "list index out of range"

    # Test `is_path_parsable` with non-parsable path.
    parsable_frag = parser.is_path_parsable(INPUT_PATH3)
    assert parsable_frag == False


if __name__ == "__main__":
    test_generate_parser_pattern1()
    test_parse_pattern1()
    test_generate_parser_pattern2()
    test_parse_pattern2()
    test_generate_parser_pattern3()
    test_parse_pattern3()
    test_is_path_parsable()
