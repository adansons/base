# -*- coding: utf-8 -*-

# Copyright 2022 Adansons Inc.
# Please contact engineer@adansons.co.jp
import time
import itertools
import threading


class Spinner:
    """
    Spinner class

    Attributes
    ----------
    text : str
        text to be displayed with a spinner when the process is started
    etext : str
        text to be displayed when the process is terminated
    overwrite : bool
        whether `etext` overwrites `text` or not
    """

    def __init__(
        self, text: str = "Please wait...", etext: str = "", overwrite: bool = True
    ) -> None:
        """
        Parameters
        ----------
        text : str
            text to be displayed with a spinner when the process is started
        etext : str
            text to be displayed when the process is terminated
        overwrite : bool
            whether `etext` overwrites `text` or not
        """
        self.text = text
        self.etext = etext
        self.overwrite = overwrite

        self._stop_flag = False

    def _spinner(self) -> None:
        """
        Display the `text` and a spinner during processing.
        """
        chars = itertools.cycle(r"/-\|")
        while not self._stop_flag:
            print(f"\r{self.text} {next(chars)}", end="")
            time.sleep(0.2)

    def start(self):
        """
        Set up a subthread to run a spinner.
        """
        self._stop_flag = False
        self._spinner_thread = threading.Thread(target=self._spinner)
        self._spinner_thread.setDaemon(True)
        self._spinner_thread.start()

    def stop(self, etext: str = "", overwrite: bool = True):
        """
        Kill a subthread and display `etest`.

        Parameters
        ----------
        etext : str
            text to be displayed when the process is terminated
        overwrite : bool
            whether `etext` overwrites `text` or not
        """
        if self._spinner_thread and self._spinner_thread.is_alive():
            self._stop_flag = True
            self._spinner_thread.join()

        etext = etext or self.etext
        overwrite = self.overwrite if not self.overwrite else overwrite

        if overwrite:
            if etext == "":
                print(f"\r\033[2K\033[G", end="")
            else:
                print(f"\r\033[2K\033[G{etext}")
        else:
            if etext == "":
                print(f"\033[1D\033[K\n", end="")
            else:
                print(f"\033[1D\033[K\n{etext}")

    def __enter__(self) -> None:
        """
        Start the spinner used on context managers.
        """
        self.start()

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        """
        Stop the spinner used on context managers.
        """
        if exception_type is not None:
            if self.overwrite:
                self.stop(etext=self.text)
            else:
                self.stop(etext="")
        else:
            self.stop()
