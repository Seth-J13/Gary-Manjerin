import os.path as osPath
from pathlib import Path as path
import bisect as split
import numpy as math
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
            while(True):
                numberOfDistricts = int(input("How many disctricts do you want?: "))
                #check for negative numbers/zeroes
                if(numberOfDistricts <= 0):
                    print("You can't have 0 or a negative amount of districts.")
                else:
                    break
            return numberOfDistricts
        except ValueError:
            print("Bro, the prompt clearly said to give a NUMBER!")
###################################################################################################
def GetPartyDistricts(districts):
    while True:
        try: 
            numDems = int(input("How many of those disctricts do you want to be Democrat?: "))
            if(districts - numDems <= 0):
                print("Too many democrat districts")
                continue
            
            numReps = districts - numDems
            return numDems, numReps
        except ValueError:
            print("Please input a number next time")
###################################################################################################
def find_lowest(high_pops):
    min = tuple([0, -1])
    for pop in high_pops:
        if min[1] < 0 or min[1] > pop[1]:
            min = tuple(pop)
    return min, list(high_pops).index(min)
###################################################################################################
def Index(id):
    # print(id)
    for block in list_of_blocks:
        # print(block)
        if id == block[0]:
            return block
###################################################################################################

#Start of program, get the files and ask which files to use
result_files = GetFiles()
num = 0
for x in result_files:
    print(str(num) + ": " + str(x)[-35:])
    num += 1

choice = int(input("\nWhich state would you like to gerrymander?\n"))

districts = GetDistricts()
democrats, republicans = GetPartyDistricts(districts)

# Iterating through the state file and beginning to gerrymander
with open(result_files[choice], "r") as state:
    # the formatting of each block VVV
    # id[0], longtitude[1], latitude[2], population[3], democrat share[4], republican share[5]
    list_of_blocks = []
    highest_pops = []
    # Separates the blocks and their values into a 2D array(list) and finds number of democrat districts of higest district populations
    for block in state:
        # getting data into a usable array
        block = block.split(",")

        # putting data into readable and useable vars
        id = int(block[0])
        lon = float(block[1])
        lat = float(block[2])
        population = int(block[3])
        rep_share = float(block[4])
        dem_share = float(block[5])

        # finding the higest N populations
        list_of_blocks.append(tuple([id, lon, lat, population, rep_share, dem_share]))

        if len(highest_pops) < democrats:
            highest_pops.append(tuple([id, population]))
        else:
            lowest, index = find_lowest(highest_pops)
            if(population > lowest[1]):
                highest_pops[index] = tuple([id, population])
    # print(sorted_by_lat)
    list_of_blocks.sort(key=lambda block: block[2])
    highest_pops.sort()
    state.close()

# Using the highest populations we begin to seed the districts onto the map
neighbors = {}
minDist = 0.001
lat_values = [block[2] for block in list_of_blocks]
num = 0
for block in list_of_blocks:
    left_idx = split.bisect_left(lat_values, block[2] - minDist)
    right_idx = split.bisect_right(lat_values, block[2] + minDist)
    print("lat: " + str(block[2]) + "| L: " + str(left_idx) + " | R: " + str(right_idx))
    nearestNeighbors = {}
    distRange = right_idx - left_idx
    for x in range(distRange):
        if(x + left_idx != Index(block[0])[0]):
            nearestNeighbors.update({str(x) : str(list_of_blocks[left_idx + x][0])})
    neighbors.update({block[0] : nearestNeighbors})
    num += 0
    print(neighbors)
    # minDist = math.sqrt(math.square())






