# import tensorflow as tf
import tkinter

# #from claude AI VVVV
# from sklearn.pipeline import Pipeline
# from sklearn.preprocessing import StandardScaler
# from sklearn.model_selection import train_test_split
# # ^^^^

import csv
import math
import numpy as np
import os.path as osPath
import sklearn as sklearn
from pathlib import Path as path


training_path = ""
testing_path = ""

#copying the file finding code from part 2
def findFiles():
    working_dir = path.cwd()
    working_dir = working_dir.parent.as_posix() + "/Data_Collection_and_Formatting"
    if(osPath.exists(working_dir)):
        training_path = working_dir + "/training"
    else:
        print("No training path exists")
    if(osPath.exists(working_dir)):
        testing_path = working_dir + "/testing"
    else:
        print("No testing path exists")
    return training_path, testing_path
training_path, testing_path = findFiles()
