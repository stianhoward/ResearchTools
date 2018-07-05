"""

Collection of tools for file interaction

tools:
- loading position.txt files
- selecting file
- selecting directory(ies)



"""
import glob
import os
import sys
from tkinter import filedialog, Tk
import pandas as pd
import matplotlib as mpl


def load_txt(filePath):
    #Try to open info about file location in 'position.txt'
    try:
        file = open(filePath)
        location = file.read()
        location = location.strip()
        file.close()
    except:
        location = None
        print("No 'position.txt' file found in: " + filePath)

    return location


def get_multi_paths():
    dirselect = filedialog.Directory(initialdir= os.path.expanduser('~'))
    dirs = []
    while True:
        d = dirselect.show()
        if not d: break
        dirs.append(d)
    if len(dirs)==0:
        print('No paths selected, exiting...')
        sys.exit
    return dirs


def get_directory(name = "select a directory: ", start_dir = os.path.expanduser('~')):
    root = Tk()
    root.withdraw()
    directory = filedialog.askdirectory(title = name, initialdir= start_dir)
    root.destroy()
    if directory != ():
        return directory
    else:
        return None


def pd_import_csv(path):
    if os.path.isfile(path):
        try:
            data = pd.read_csv(path)
            return data
        except:
            print("failed to read CSV file", sys.exc_info())
            return None
    else:
        print("File does not exist at: ", path)
        return None


def retrieve_image(path):
    if os.path.isfile(path):
        try:
            return mpl.image.imread(path)
        except:
            print("Failed to retrieve image as path is not a file.", sys.exc_info())
            return None
    else:
        print("No file found at ", path)
        return None


def save_image(path, image):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    try:
        mpl.image.imsave(path, image)
        return
    except:
        print('Failed to save image to ', path, sys.exc_info())
        return
