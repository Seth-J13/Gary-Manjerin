
import os.path as osPath
from pathlib import Path as path

def GetFiles():
    working_dir = path.cwd() # Get current file path
    working_dir = working_dir.parent.as_posix() + "/Predictive_Model/prediction/" # Modify for navigation
    
    # If the previous folder exists on the computer already, add the training and testing folders
    if(osPath.exists(working_dir)):
        return path.rglob(path(working_dir), "*.csv")
    else:
        return print("No prediction path exists")


result_files = GetFiles()
result_files = tuple(result_files)
num = 0
for x in result_files:
    print(str(num) + ": " + str(x)[-35:])
    num += 1