import os.path as osPath
from pathlib import Path as path
import bisect as split
import numpy as math
from enum import Enum 
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
######
#   Get Districts functon
#   no parameters
#   Prompts the user for how many districts they want. It forces them in the loop until they input an actual number.
######
def GetDistricts():
    #keeps the user in the loop until they successfully submit a valid input
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
######
#   Get Party Districts functon
#   no parameters
#   Prompts the user for how many democrat dominated districts they want. It forces them in the loop until they input an actual number.
#   Republican districts = total Districts - Democrat Districts
######
def GetPartyDistricts(districts):
    #keeps the user in the loop until they successfully submit a valid input
    while True:
        try: 
            #since we are using a total - number of democrats, we don't need a democrat and republican input
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
def print_dict(districts):
    for district, blocks in dict(districts).items():
        print(str(district))
        for id, neighbors in dict(blocks).items():
            print("\t" + str(id))
            # for neighbor in list(neighbors):
            print("\t\t" + str(neighbors))
###################################################################################################
#Start of program, get the files and ask which files to use
result_files = GetFiles()
num = 0
#prints out the list of files.
for x in result_files:
    print(str(num) + ": " + str(x)[-35:])
    num += 1

choice = int(input("\nWhich state would you like to gerrymander?\n"))

districts = GetDistricts()
democrats, republicans = GetPartyDistricts(districts)

# This is to save us the confusion of arbitrary array/list indexing. 
# Use this when accessing any part of a block's data 
class Data(Enum):
    ID = 0
    LON = 1
    LAT = 2
    POP = 3
    DEM = 4
    REP = 5
# Iterating through the state file and beginning to gerrymander
with open(result_files[choice], "r") as state:
    # the formatting of each block VVV
    # id[0], longtitude[1], latitude[2], population[3], democrat share[4], republican share[5]
    list_of_blocks = []
    highest_pops = []
    total_pop = 0
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
        list_of_blocks.append(tuple([id, lon, lat, population, dem_share, rep_share]))
        total_pop += population #adds the block's population to the total. Cast to integer to avoid errors

        if len(highest_pops) < democrats:
            highest_pops.append(tuple([id, population]))
        else:
            lowest, index = find_lowest(highest_pops)
            if(population > lowest[1]):
                highest_pops[index] = tuple([id, population])
    #figure out the ideal population share per district (totalPop / number of districts)
    popPerDistrict = total_pop / districts
    list_of_blocks.sort(key=lambda block: block[2])
    highest_pops.sort()
    state.close()
    #Use this for determining if a district has too much/little population compared to the others.
    #Ideally, each district should be within +/- 5% of the popPerDistrict

#This is to make the index search happen only once instead of us needing to search every time we need id. 
# through list_of_blocks every time it's called.
id_to_index = {block[Data.ID.value]: i for i, block in enumerate(list_of_blocks)}

# Using the highest populations we begin to seed the districts onto the map
#minDist = 0.001
minDist = 0.05 
lat_values = [block[Data.LAT.value] for block in list_of_blocks]
block_neighbors = {}
# This loop intializes a dictionary with every single block having a list of its neighbors
for block in list_of_blocks:
    left_idx = split.bisect_left(lat_values, block[2] - minDist)
    right_idx = split.bisect_right(lat_values, block[2] + minDist)
    # print("lat: " + str(block[2]) + "| L: " + str(left_idx) + " | R: " + str(right_idx))
    distRange = right_idx - left_idx
    for x in range(distRange):
        candidate = list_of_blocks[left_idx + x]
        neighbors = [] if block_neighbors.get(block[Data.ID.value]) == None else block_neighbors.get(block[Data.ID.value])
        if candidate[Data.ID.value] == block[Data.ID.value]:
            continue  # skip the rest of the code
        #check both the above and below neighbors along with left and right neighbors.
        lon_dist = abs(candidate[Data.LON.value] - block[Data.LON.value])
        lat_dist = abs(candidate[Data.LAT.value] - block[Data.LAT.value])
        if lon_dist <= minDist and lat_dist <= minDist:
            neighbors.append(candidate[Data.ID.value])
            block_neighbors.update({block[Data.ID.value]: neighbors})

#Goals:
# Calculate ideal population add it to the district dict
# We need a loop to start adding blocks to districts
# Visual of hierarchy 
# districts =
#   {
#       (district num/name) : { (priority of district) : (priority value), (block id) : (list of block neighbors) }
#       0 : { priority : X, block1 : [neighbors], block2 : [neighbors], ...}
#       1 : { priority : X, block1 : [neighbors], block2 : [neighbors], ...}
#       2 : { priority : X, block1 : [neighbors], block2 : [neighbors], ...}
#       ...
#   }
"""
So far we have block_neighbors which is a dictionary of block ids with their corresponding neighbors
    {(single id) : (list of ids)
        block1 : [neighbor ids]
        block2 : [neighbor ids]
        block3 : [neighbor ids]
    }

    
    TO ETHAN:
        If you want to, 
            1. You can start calculating the ideal population for a district.
            2. Create the districts and start working on a loop that iterates through the block_neighbors and adds to a district
                I imagine that it would need to be a while loop because it would have to loop over block_neighbors over and over till
                it is empty. Furthermore, you may need to have the seeds figured out so if you can't get this to work without the seeds
                then work on that first. I'll pick up where you leave off tomorrow if I can.
        
"""





#VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV
# I commented out this because I was focusing on the dict inits, you can continue if you like
#VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV
    #I want your seed (threat) Democrats
    # dem_Seed = [id[0] for id in highest_pops]

    # #Time for the Republican seeds. Takes the lowest population blocks
    # pop_Reverse_order = sorted(list_of_blocks, key=lambda b: b[3], reverse=True)

    # rep_Seed = []
    # for block in pop_Reverse_order:
    #     if block[0] not in dem_Seed:        # if the block isn't among the highest populations
    #         rep_Seed.append(block[0])
    #     if len(rep_Seed) == republicans:     # stop once we have enough Republican districts
    #         break