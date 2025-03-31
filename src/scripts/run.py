import os
import subprocess
import sys


def start():
    os.system("uvicorn src.presentation.main:application --reload")


def test():
    sys.exit(subprocess.call(["pytest"]))


def format():
    os.system("black .")


def sort():
    os.system("isort .")


def lint():
    os.system("flake8 .")
