import os.path as osPath
from pathlib import Path as path
from enum import Enum 
###################################################################################################
# Get Files is the starting function that retrieves the csv result files from the previous part
# It returns a iterable tuple for the program to use
def GetFiles():
    working_dir = path.cwd() # Get current file path
    working_dir = working_dir.as_posix() + "/Predictive_Model/prediction/" # Modify for navigation
    
    # If the previous folder exists on the computer already, add the training and testing folders
    if(osPath.exists(working_dir)):
        return tuple(path.rglob(path(working_dir), "*.csv"))
    else:
        return print("No prediction path exists")
###################################################################################################
######
#   Get Districts function
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
                numberOfDistricts = int(input("How many districts do you want?: "))
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
#   Get Party Districts function
#   no parameters
#   Prompts the user for how many democrat dominated districts they want. It forces them in the loop until they input an actual number.
#   Republican districts = total Districts - Democrat Districts
######
def GetPartyDistricts(districts):
    #keeps the user in the loop until they successfully submit a valid input
    while True:
        try: 
            #since we are using a total - number of democrats, we don't need a democrat and republican input
            numDems = int(input("How many of those districts do you want to be Democrat?: "))
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
def print_dict(districts):
    for district, blocks in dict(districts).items():
        print("This is a district: " +str(district))
        for id, neighbors in dict(blocks).items():
            print("\tThis is a block: " + str(id))
            # for neighbor in list(neighbors):
            print("\t\tThis is its neighbors: " + str(neighbors))
###################################################################################################
def create_csv(districts, choice):
    currDir = path.cwd().as_posix().replace("\\", "/") + "/"
    result_dir = currDir + "Reasonable_Gerrymandering/gerrymandered_results"

    if not path.exists(path(result_dir)):
        path.mkdir(path(result_dir))

    choice = path(choice).name.removesuffix("results.csv") + "gerrymandered.csv"
    with open(result_dir + "/" + choice, "w") as result:
        for district, blocks in dict(districts).items():
            parts = [str(district)]
            for blockId, neighbors in dict(blocks).items():
                parts.append(str(blockId) + ":" + str(neighbors).replace(", ", "|"))
            result.write(", ".join(parts) + "\n")
##################################################################################################
#Start of program, get the files and ask which files to use

def gerrymander():
    
    ###########################
    # Helper function
    ###########################
    def Index(id):
        # id_to_index is built once (see below) so this is an O(1) dict lookup
        # instead of an O(n) scan through list_of_blocks. With 500k+ blocks the
        # old version turned every leftover-dump and every spread-claim into a
        # linear scan, which is what was making the leftover-dump step take hours.
        idx = id_to_index.get(id)
        return list_of_blocks[idx] if idx is not None else None

    result_files = GetFiles()
    num = 0
    #prints out the list of files.
    print("\n\n")
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
        # id[0], longitude[1], latitude[2], population[3], democrat share[4], republican share[5]
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

            # finding the highest N populations
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

    # Tuning knobs for the adaptive radius below.
    MIN_NEIGHBORS = 4        # every block should end up with at least this many neighbors
    MAX_RING_EXPANSION = 40  # safety cap so a truly empty area can't search forever

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

    print(f"[DEBUG] Base radius pass complete: {pairs_found} pair(s) found, "
        f"{len(block_neighbors)} block(s) have >=1 neighbor")

    ###########################
    # Top-up pass: a fixed minDist is fine for dense urban blocks but leaves
    # sparse/rural blocks (huge in CA) with zero neighbors -- those blocks can
    # never be reached by district growth and previously got bulk-dumped into
    # one district at the end. Any block short of MIN_NEIGHBORS gets its own
    # search radius expanded outward, ring of grid cells at a time, until it
    # finds enough neighbors. Dense blocks are untouched -- only the sparse
    # minority pays the extra cost.
    ###########################
    def ring_cells(cx, cy, r):
        """All grid cells at exactly Chebyshev distance r from (cx, cy)."""
        cells = []
        for dx in range(-r, r + 1):
            cells.append((cx + dx, cy - r))
            cells.append((cx + dx, cy + r))
        for dy in range(-r + 1, r):
            cells.append((cx - r, cy + dy))
            cells.append((cx + r, cy + dy))
        return cells

    sparse_ids = [b[Data.ID.value] for b in list_of_blocks
                if len(block_neighbors.get(b[Data.ID.value], [])) < MIN_NEIGHBORS]

    print(f"[DEBUG] {len(sparse_ids)} block(s) have fewer than {MIN_NEIGHBORS} neighbor(s) "
        f"after the base pass; expanding their search radius individually...")

    topped_up = 0
    still_isolated = 0

    for block_id in sparse_ids:
        block = Index(block_id)
        cx = int(block[Data.LON.value] // cell_size)
        cy = int(block[Data.LAT.value] // cell_size)
        existing = set(block_neighbors.get(block_id, []))
        needed = MIN_NEIGHBORS - len(existing)
        found = []  # (distance, candidate_id)
        ring = 2    # rings 0-1 (the 3x3 block) were already covered by the base pass
        while len(found) < needed and ring <= MAX_RING_EXPANSION:
            for (gx, gy) in ring_cells(cx, cy, ring):
                for candidate in grid.get((gx, gy), []):
                    candidate_id = candidate[Data.ID.value]
                    if candidate_id == block_id or candidate_id in existing:
                        continue
                    lon_dist = abs(candidate[Data.LON.value] - block[Data.LON.value])
                    lat_dist = abs(candidate[Data.LAT.value] - block[Data.LAT.value])
                    found.append((max(lon_dist, lat_dist), candidate_id))
            ring += 1

        found.sort()
        for _, candidate_id in found[:needed]:
            block_neighbors.setdefault(block_id, []).append(candidate_id)
            block_neighbors.setdefault(candidate_id, []).append(block_id)
            existing.add(candidate_id)
            pairs_found += 1

        if existing:
            topped_up += 1
        else:
            still_isolated += 1  # nothing found even after MAX_RING_EXPANSION rings

    print(f"[DEBUG] Top-up pass complete: {topped_up} block(s) topped up, "
        f"{still_isolated} block(s) still isolated after {MAX_RING_EXPANSION} ring(s) "
        f"(no other block anywhere nearby -- worth a data sanity check if this is > 0)")

    print(f"[DEBUG] Neighbor search complete: {pairs_found} pair(s) found, "
        f"{len(block_neighbors)} block(s) have at least one neighbor")

    ###########################
    # Districting block
    # Time for some seeds
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
    # Districting block 2
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

    print("Beginning data conversion...\nThis may take up to 10 minutes")
    create_csv(districts, str(result_files[choice]))
    print("Finished")
