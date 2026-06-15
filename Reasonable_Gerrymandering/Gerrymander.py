
import os.path as osPath
import pathlib as path

def GetFiles():
    working_dir = path.cwd() # Get current file path
    working_dir = working_dir.parent.as_posix() + "/Data_Collection_and_Formatting" # Modify for navigation
    
    # If the previous folder exists on the computer already, add the training and testing folders
    if(osPath.exists(working_dir)):
        training_path = working_dir + "/training"
    else:
        print("No training path exists")
    if(osPath.exists(working_dir)):
        testing_path = working_dir + "/testing"
    else:
        print("No testing path exists")
    return

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

def GetPartyDistricts(districts):
    while True:
        try: 
            numDems = int(input("How many of those disctricts do you want to be Democrat?: "))
            if(districts - numDems < 0):
                print("Too many democrat districts")
                continue
            
            numReps = districts - numDems
            return numDems, numReps
        except ValueError:
            print("Please input a number next time")


result_file = GetFiles()
districts = GetDistricts()

democrats, republicans = GetPartyDistricts(districts)