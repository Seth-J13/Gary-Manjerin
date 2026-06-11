# import tensorflow as tf
import tkinter

from sklearn import svm
import array
#from claude AI VVVV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
# ^^^^

import numpy as np
import os.path as osPath
from pathlib import Path as path


###
# The folder finder does not work. Alex is better at the os path stuff. If you(Alex) want to work on it, you can. 
# Otherwise, we can just keep findFiles() func to get the folders.
###




training_path = ""
testing_path = ""

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


print("\nSelect a file to use for training and testing the model.\n")
paths = path.rglob(path(training_path), "*.csv")
paths_list = tuple(paths)
num = 0
for x in paths_list:
    print(str(num) + ": " + str(x))
    num += 1

num = int(input("Please enter the index of the file you would like to use (start at 0 and count up): "))
selected_training_path = paths_list[num]

paths = path.rglob(path(testing_path), "*.csv")
paths_list = tuple(paths)
selected_testing_path = paths_list[num]

#I yoinked this from claude AI VVVV
X = path.open(selected_training_path).readlines()
y = path.open(selected_testing_path).readlines()
X_array = []
y_array = []
for i in X:
    tempArray = []
    for k in i.split(","):
        tempArray.append(k)
    X_array.append(tempArray)
for i in y:
    # tempArray = []
    k = i.split(",")
    y_array.append(k[2])

X_train, X_test, y_train, y_test = train_test_split(X_array, y_array, test_size=0.2)

pipe = Pipeline([
    ('scaler', StandardScaler()),   # always scale for SVMs!
    ('svm',    svm.SVC(kernel='rbf', C=1.0, gamma='scale'))
])

pipe.fit(X_train, y_train)
print(pipe.score(X_test, y_test))

#^^^^^ AI
