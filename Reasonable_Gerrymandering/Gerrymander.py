
import os.path as osPath
from pathlib import Path as path
###################################################################################################
# Get Files is the starting function that retrieves the csv result files from the previous part
# It returns a iterable tuple for the program to use
def GetFiles():
    working_dir = path.cwd() # Get current file path
    working_dir = working_dir.parent.as_posix() + "/Predictive_Model/prediction/" # Modify for navigation
    
    # If the previous folder exists on the computer already, add the training and testing folders
    if(osPath.exists(working_dir)):
        return tuple(path.rglob(path(working_dir), "*.csv"))
    else:
        return print("No prediction path exists")
###################################################################################################
def GetDistricts():
    while True: 
        #Ethan: I can't believe I have to do a try/catch because some idiot is going to -->
        #-->input a non-number just to ragebait me
        try: 
            #prompt the user for the number of districts
            numberOfDistricts = int(input("How many disctricts do you want?: "))

            #check for negative numbers/zeroes
            if(numberOfDistricts <= 0):
                print("You can't have 0 or a negative amount of districts.")
                continue

            return numberOfDistricts
        except ValueError:
            print("Bro, the prompt clearly said to give a NUMBER!")
###################################################################################################

#Start of program, get the files and ask which files to use
result_files = GetFiles()
num = 0
for x in result_files:
    print(str(num) + ": " + str(x)[-35:])
    num += 1


result_file = GetFiles()
districts = GetDistricts()
