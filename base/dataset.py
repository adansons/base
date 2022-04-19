# -*- coding: utf-8 -*-

# Copyright 2022 Adansons Inc.
# Please contact engineer@adansons.co.jp
import numpy as np
from sklearn.model_selection import train_test_split
from typing import Callable, Optional, Tuple

from base.files import Files


class Dataset:
    """
    Dataset class

    Attributes
    ----------
    transform : function
        function for preprocessing
    target_key : str
        key you want to label
    files : list
        list of File class
    paths : list
        list of filepath
    convert_dict : dict
        dict to convert labels to numbers
    y : list of int
        target label
    y_train : list of int
        target label used to train
    y_test : list of int
        target label used to test
    x : list
        data
    x_train : list
        data used to train
    x_test : list
        data used to test
    train_path : list
        filepath used to train
    test_path : list
        filepath used to test
    """

    def __init__(
        self, files: Files, target_key: str, transform: Optional[Callable] = None
    ) -> None:
        """
        Make the dict to convert labels to numbers.

        files : list
            list of File class
        target_key : str
            key you want to label
        transform : function or None, default None
            function for preprocessing
        """

        self.transform = transform
        self.target_key = target_key
        if self.transform == None:
            self.transform = lambda x: x

        self.files = files
        self.paths = self.files.paths

        target_values = [getattr(file, target_key) for file in self.files]
        unique_target_values = list(set(target_values))
        numbers = [*range(len(unique_target_values))]
        self.convert_dict = dict(zip(unique_target_values, numbers))

    def train_test_split(self, split_rate: int = 0.25) -> Tuple[list]:
        """
        Split train data and test data.

        Parameters
        ----------
        split_rate : float
            the proportion of the dataset to include in the test data

        Returns
        -------
        x_train : list
            data used to train
        x_test : list
            data used to test
        y_train : list of int
            target label used to train
        y_test : list of int
            target label used to test
        """
        self.y = [getattr(i, self.target_key) for i in self.files]
        self.y = [self.convert_dict[i] for i in self.y]
        self.y = np.eye(len(self.convert_dict))[self.y]
        self.x = [self.transform(i) for i in self.paths]

        (
            self.train_path,
            self.test_path,
            self.y_train,
            self.y_test,
        ) = train_test_split(self.paths, self.y, test_size=split_rate, stratify=self.y)

        self.x_train = [self.transform(i) for i in self.train_path]
        self.x_test = [self.transform(i) for i in self.test_path]

        return self.x_train, self.x_test, self.y_train, self.y_test

    def __len__(self) -> int:
        return len(self.files)

    def __getitem__(self, idx: int) -> Tuple:
        path = self.paths[idx]
        data = self.transform(path)
        label = getattr(self.files[idx], self.target_key)
        label = self.convert_dict[label]

        return data, label


if __name__ == "__main__":
    pass
