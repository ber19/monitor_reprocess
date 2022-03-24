import tempfile
from shutil import rmtree
import os
import sys

def clean_mei():
    mei = getattr(sys, "_MEIPASS", False)
    if mei:
        dir_mei, current_mei = mei.split("_MEI")
        for file in os.listdir(dir_mei):
            if file.startswith("_MEI") and not file.endswith(current_mei):
                try:
                    rmtree(os.path.join(dir_mei, file))
                except PermissionError:
                    pass

def clean_scoped():
    temp_path = tempfile.gettempdir()
    for dir in os.listdir(temp_path):
        if dir.startswith("scoped_dir"):
            rmtree(os.path.join(temp_path, dir))

def clean_drag():
    temp_path = tempfile.gettempdir()
    for dir in os.listdir(temp_path):
        if dir.startswith("chrome_drag"):
            rmtree(os.path.join(temp_path, dir))
            