# import tensorflow as tf
import tkinter

from sklearn import svm
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

# This searches the entire computer for shape files.
def search_computer_for_training_and_testing_dirs():
    print("Searching... (this may take a while)\n")
    write_list = ""
    folder_list = []
    for _path in path(osPath.expanduser("~")).rglob("*"):
        write_list = write_list + str(_path) + ","
        folder_list.append(str(_path))

    # Build a database so the search doesn't need to be conducted again.
    with open("folder_list.csv", "w") as folder_lists:
        folder_lists.write(write_list[:-1])
    folder_lists.close()

    for _item in folder_list:
        folder_list[folder_list.index(_item)] = _item.replace("\\", "/")

    return folder_list

# This checks the stored database of shape files in the same directory.
# Used to save time while testing and executing
def check_database():
    with open("folder_list.csv", "r") as folder_lists:
        folder_lists = folder_lists.read().replace("\\", "/").strip().split(",")
        
    folder_lists.close()
    return folder_lists


training_path, testing_path = findFiles()

#Request for training file
# Let user decide how to input shape files
while True:
    choice = input("Choose what you'd like to do:\n1. Automatically search the computer for all shape files\n2. Use a file-picker dialog\n3. Use Saved CSV Files\n")
    print("")
    if choice == "1" or choice == "2" or choice == "3":
        break

if choice == "1":
    if (osPath.exists("folder_list.csv")):
        if (input("\nYour previous search was saved to a database! You can use that instead of checking again.\nSearch anyway? (y/n) ") == "y"):
            folder_list = search_computer_for_training_and_testing_dirs()
        else:
            folder_list = check_database()
    else:
        folder_list = search_computer_for_training_and_testing_dirs()

# Let the user opt to upload a file using a file-picker dialog
elif choice == "2":
    selected_path = tkinter.filedialog.askopenfilename()

# If the user neglects the whole search, instead use a database stored on the computer
elif choice == "3" and (osPath.exists("folder_list.csv")):
    folder_list = check_database()

# Choose from list of shape files that were cached or detected
if choice == "1" or choice == "3":    
    common_path = osPath.commonprefix(folder_list)
    for x in range(len(folder_list)):
        print(str(x) + ": " + str(folder_list[x])[str(folder_list[x]).rfind("/") + 1:]) 
    selected_path = folder_list[int(input("Please enter the index of the file you would like to use (start at 0 and count up): "))]




