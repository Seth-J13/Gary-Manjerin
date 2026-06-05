# import tensorflow as tf
import tkinter

from sklearn import svm
import numpy as np
import os.path as osPath
from pathlib import Path as path

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
def search_computer_for_shape_files():
    print("Searching... (this may take a while)\n")
    write_list = ""
    shapefile_list = []
    for _path in path.Path(osPath.expanduser("~")).rglob("*.shp"):
        write_list = write_list + str(_path) + ","
        shapefile_list.append(str(_path))

    # Build a database so the search doesn't need to be conducted again.
    with open("shapefiles.csv", "w") as shapefiles:
        shapefiles.write(write_list[:-1])
    shapefiles.close()

    for _item in shapefile_list:
        shapefile_list[shapefile_list.index(_item)] = _item.replace("\\", "/")

    return shapefile_list

# This checks the stored database of shape files in the same directory.
# Used to save time while testing and executing
def check_database():
    with open("shapefiles.csv", "r") as shapefiles:
        shapefile_list = shapefiles.read().replace("\\", "/").strip().split(",")
        
    shapefiles.close()
    return shapefile_list


training_path, testing_path = findFiles()

#Request for training file
# Let user decide how to input shape files
while True:
    choice = input("Choose what you'd like to do:\n1. Automatically search the computer for all shape files\n2. Use a file-picker dialog\n3. Use Saved CSV Files\n")
    print("")
    if choice == "1" or choice == "2" or choice == "3":
        break

if choice == "1":
    if (osPath.exists("shapefiles.csv")):
        if (input("\nYour previous search was saved to a database! You can use that instead of checking again.\nSearch anyway? (y/n) ") == "y"):
            shapefile_list = search_computer_for_shape_files()
        else:
            shapefile_list = check_database()
    else:
        shapefile_list = search_computer_for_shape_files()

# Let the user opt to upload a file using a file-picker dialog
elif choice == "2":
    selected_path = tkinter.filedialog.askopenfilename()

# If the user neglects the whole search, instead use a database stored on the computer
elif choice == "3" and (os.path.exists("shapefiles.csv")):
    shapefile_list = check_database()

# Choose from list of shape files that were cached or detected
if choice == "1" or choice == "3":    
    common_path = osPath.commonprefix(shapefile_list)
    for x in range(len(shapefile_list)):
        print(str(x) + ": " + str(shapefile_list[x])[str(shapefile_list[x]).rfind("/") + 1:]) 
    selected_path = shapefile_list[int(input("Please enter the index of the file you would like to use (start at 0 and count up): "))]
