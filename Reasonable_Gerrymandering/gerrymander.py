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
        print("This is a district: " +str(district))
        for id, neighbors in dict(blocks).items():
            print("\tThis is a block: " + str(id))
            # for neighbor in list(neighbors):
            print("\t\tThis is its neighbors: " + str(neighbors))
###################################################################################################
def create_csv(districts):
    mainDir = path.cwd().as_posix().removesuffix("/Reasonable_Gerrymandering").replace("\\", "/") + "/"
    currDir = path.cwd().as_posix().replace("\\", "/") + "/"
    if(not path.exists(path(currDir + "gerrymandered_results"))):
        path.mkdir(path(currDir + "gerrymandered_results"))
    result_path = currDir + "gerrymandered_results"
    with open(result_path, "+w") as result:
        return
        # ~~~~~~ create a csv here ~~~~~~
    return
###################################################################################################
#Start of program, get the files and ask which files to use
create_csv({4, 3, 4})
input("waiting")
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
    idealPop = total_pop / districts
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

print(f"[DEBUG] Building spatial grid for neighbor search (minDist={minDist}) "
      f"over {len(list_of_blocks)} blocks...")

# NOTE: the old bisect approach only narrowed candidates by LATITUDE, so for
# every block it was scanning every other block in a similar latitude band
# across the ENTIRE longitude span of the state -- that's what made this take
# 30+ minutes. A 2D grid only ever compares a block against the handful of
# blocks in its own cell and the 8 cells touching it.
cell_size = minDist
grid = {}
for block in list_of_blocks:
    cell = (int(block[Data.LON.value] // cell_size), int(block[Data.LAT.value] // cell_size))
    grid.setdefault(cell, []).append(block)

print(f"[DEBUG] Grid built: {len(grid)} occupied cell(s), "
      f"avg {len(list_of_blocks) / max(len(grid), 1):.1f} block(s)/cell")

block_neighbors = {}
processed = 0
pairs_found = 0

for block in list_of_blocks:
    block_id = block[Data.ID.value]
    cx = int(block[Data.LON.value] // cell_size)
    cy = int(block[Data.LAT.value] // cell_size)

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for candidate in grid.get((cx + dx, cy + dy), []):
                candidate_id = candidate[Data.ID.value]
                if candidate_id <= block_id:
                    continue  # skip self, and skip pairs already handled from the other side
                lon_dist = abs(candidate[Data.LON.value] - block[Data.LON.value])
                lat_dist = abs(candidate[Data.LAT.value] - block[Data.LAT.value])
                if lon_dist <= minDist and lat_dist <= minDist:
                    block_neighbors.setdefault(block_id, []).append(candidate_id)
                    block_neighbors.setdefault(candidate_id, []).append(block_id)
                    pairs_found += 1

    processed += 1
    if processed % 5000 == 0:
        print(f"[DEBUG] Neighbor search: {processed}/{len(list_of_blocks)} blocks processed, "
              f"{pairs_found} neighbor pair(s) found so far")

print(f"[DEBUG] Neighbor search complete: {pairs_found} pair(s) found, "
      f"{len(block_neighbors)} block(s) have at least one neighbor")


###########################
#Districting block
#Time for some seeds
###########################
#I want your seed (threat) Democrats
dem_Seeds = [id[0] for id in highest_pops]
print(f"[DEBUG] Selected {len(dem_Seeds)} Democrat seed block(s): {dem_Seeds}")

 #Time for the Republican seeds. Takes the lowest population blocks
pop_Reverse_order = sorted(list_of_blocks, key=lambda b: b[3], reverse=True)

rep_Seeds = []
for block in pop_Reverse_order:
    if block[Data.ID.value] not in dem_Seeds:        # if the block isn't among the highest populations
        rep_Seeds.append((block[Data.ID.value], block[Data.POP.value]))
    if len(rep_Seeds) == republicans:     # stop once we have enough Republican districts
        break
print(f"[DEBUG] Selected {len(rep_Seeds)} Republican seed block(s): {rep_Seeds}")

#compile the list of all the seeds
all_seeds = list(highest_pops) + rep_Seeds
print(f"[DEBUG] Total seeds compiled: {len(all_seeds)} (expected {districts})")

###########################
#Districting block 2
# Create the starting districts
###########################
districts = {}
assigned = {}     # block_id -> district number, so no block ever gets claimed twice
frontiers = {}    # district number -> list of block ids on the growing edge
 
 #labels each district as either Democrat or Republican
for district_num, (seed_id, seed_pop) in enumerate(all_seeds):
    party = "D" if district_num < democrats else "R"
    districts[district_num] = {
        "priority": idealPop - seed_pop,
        "party": party,
        "population": seed_pop,
        seed_id: block_neighbors.get(seed_id, [])
    }
    assigned[seed_id] = district_num
    frontiers[district_num] = [seed_id]
    print(f"[DEBUG] Created district {district_num} ({party}) seeded at block {seed_id}, "
          f"starting population {seed_pop}")

###########################
# Spread the districts until all blocks are claimed
###########################
# made by AI VVVVVVVV

total_blocks = len(list_of_blocks)

print(f"[DEBUG] All {len(districts)} districts seeded. Beginning spread phase "
      f"({total_blocks} total blocks to assign)...")

DEBUG_PRINT_EVERY = 100   # print a progress line every N blocks claimed (raise/lower as needed)
loop_count = 0

while len(assigned) < total_blocks:
    loop_count += 1
    district_num = max(districts.keys(), key=lambda d: districts[d]["priority"])
    frontier = frontiers[district_num]

    claimed = False
    while frontier and not claimed:
        current_id = frontier.pop(0)
        for neighbor_id in block_neighbors.get(current_id, []):
            if neighbor_id in assigned:
                continue
            neighbor_block = Index(neighbor_id)
            districts[district_num][neighbor_id] = block_neighbors.get(neighbor_id, [])
            districts[district_num]["population"] += neighbor_block[Data.POP.value]
            districts[district_num]["priority"] = idealPop - districts[district_num]["population"]
            assigned[neighbor_id] = district_num
            frontier.append(neighbor_id)
            claimed = True
            if len(assigned) % DEBUG_PRINT_EVERY == 0 or len(assigned) == total_blocks:
                print(f"[DEBUG] Progress: {len(assigned)}/{total_blocks} blocks assigned "
                      f"(loop {loop_count}) | district {district_num} "
                      f"({districts[district_num]['party']}) claimed block {neighbor_id}, "
                      f"population now {districts[district_num]['population']:.0f} "
                      f"(target {idealPop:.0f})")
            break  # one block per turn, then re-check which district needs it most

    if not claimed:
        districts[district_num]["priority"] = float("-inf")
        print(f"[DEBUG] District {district_num} ({districts[district_num]['party']}) has no "
              f"unclaimed neighbors left on its frontier; marking it inactive.")

    if len(assigned) < total_blocks and all(d["priority"] == float("-inf") for d in districts.values()):
        leftover_ids = [b[Data.ID.value] for b in list_of_blocks if b[Data.ID.value] not in assigned]
        smallest_district = min(districts.keys(), key=lambda d: districts[d]["population"])
        print(f"[DEBUG] All districts stalled at {len(assigned)}/{total_blocks} blocks assigned. "
              f"Dumping {len(leftover_ids)} leftover block(s) into district {smallest_district} "
              f"({districts[smallest_district]['party']}, currently smallest).")
        for leftover_id in leftover_ids:
            block = Index(leftover_id)
            districts[smallest_district][leftover_id] = block_neighbors.get(leftover_id, [])
            districts[smallest_district]["population"] += block[Data.POP.value]
            assigned[leftover_id] = smallest_district
        break

print(f"[DEBUG] Spread phase complete after {loop_count} outer loop iteration(s). "
      f"{len(assigned)}/{total_blocks} blocks assigned across {len(districts)} districts.")

create_csv(districts)
print_dict(districts)