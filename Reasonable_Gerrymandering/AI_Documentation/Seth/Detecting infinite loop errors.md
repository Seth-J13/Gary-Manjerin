# Detecting infinite loop errors

## User

Are there any errors or bugs that may cause infinite loop?

### Attachment: gerrymander.py _(12.2 KB)_
````
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
# Calculate ideal population add it to the district dict (done idealPop line 137)
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
###########################
#Districting block
#Time for some seeds
###########################
#I want your seed (threat) Democrats
dem_Seeds = [id[0] for id in highest_pops]

 #Time for the Republican seeds. Takes the lowest population blocks
pop_Reverse_order = sorted(list_of_blocks, key=lambda b: b[3], reverse=True)

rep_Seeds = []
for block in pop_Reverse_order:
    if block[Data.ID.value] not in dem_Seeds:        # if the block isn't among the highest populations
        rep_Seeds.append(block[Data.ID.value])
    if len(rep_Seeds) == republicans:     # stop once we have enough Republican districts
        break

#compile the list of all the seeds
all_seeds = list(highest_pops) + rep_Seeds

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

###########################
# Spread the districts until all blocks are claimed
###########################
# made by AI VVVVVVVV
total_blocks = len(list_of_blocks)
 
while len(assigned) < total_blocks:
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
            break  # one block per turn, then re-check which district needs it most
 
    if not claimed:
        districts[district_num]["priority"] = float("-inf")
 
    if len(assigned) < total_blocks and all(d["priority"] == float("-inf") for d in districts.values()):
        leftover_ids = [b[Data.ID.value] for b in list_of_blocks if b[Data.ID.value] not in assigned]
        smallest_district = min(districts.keys(), key=lambda d: districts[d]["population"])
        for leftover_id in leftover_ids:
            block = Index(leftover_id)
            districts[smallest_district][leftover_id] = block_neighbors.get(leftover_id, [])
            districts[smallest_district]["population"] += block[Data.POP.value]
            assigned[leftover_id] = smallest_district
        break
 
print_dict(districts)
````

## Claude

Short answer: I don't see a genuine infinite loop. The district-growing `while` loop at the bottom has an explicit escape valve, and the two `while True` input prompts (`GetDistricts`, `GetPartyDistricts`) are deliberate "retry until valid" loops, not bugs. But there are a couple of issues that will either make the program run so slowly it *looks* hung, or make it stop too early with bad results — worth knowing about either way.

**1. `Index()` ignores the index map you built — turns the spread into O(n²)**

You build `id_to_index` right before the spreading loop, but `Index()` never uses it:

```python
def Index(id):
    for block in list_of_blocks:
        if id == block[0]:
            return block
```

This runs once per neighbor every time a block gets claimed, so for a CSV with a few thousand census blocks you get a linear scan times a linear number of claims — O(n²). Combine that with `frontier.pop(0)` (also O(n) on a plain Python list), and a real state file could take so long it feels infinite even though it would technically finish eventually. Fix: `return list_of_blocks[id_to_index[id]]`, and swap the frontier lists for `collections.deque` with `popleft()`.

**2. A popped block only ever gets to claim one neighbor, then is discarded**

```python
current_id = frontier.pop(0)
for neighbor_id in block_neighbors.get(current_id, []):
    ...
    claimed = True
    break
```

`current_id` is removed from `frontier` and never put back, even if it has several other unclaimed neighbors. So each district's frontier shrinks much faster than it should, priorities hit `-inf` for everyone earlier than intended, and the "all priorities are `-inf`" fallback near the bottom ends up dumping a large leftover chunk of the map into whichever district happens to be smallest. This isn't an infinite loop — if anything it makes the loop end *too soon* — but it explains lumpy or wrong-looking district shapes rather than a hang.

**3. `GetPartyDistricts` accepts `0` (or negative) Democrat districts**

```python
if(districts - numDems <= 0):
    print("Too many democrat districts")
    continue
```

With `numDems = 0`, `districts - 0` is never `<= 0`, so it's accepted. Then in the CSV loop, `len(highest_pops) < democrats` is `0 < 0` (False) on the very first row, so it falls into the `else` branch and calls `find_lowest([])`. Inside, `list(high_pops).index(min)` raises `ValueError`, since the placeholder `min` was never actually in the empty list. That's a hard crash on line one of the file, not a loop — but it's easy to trigger by accident.

**4. Unrelated to looping, but worth a glance:** `GetFiles()` does `return print("No prediction path exists")`, which returns `None`. If the prediction folder is missing, the next line (`for x in result_files:`) throws `TypeError: 'NoneType' object is not iterable`.

If you'd like, I can also walk through a dem/rep column mix-up I noticed in the CSV-parsing block — separate from looping, but worth fixing while you're in there.

## User

will you add debug messages from line 206 - 277 so while the program is running I can know what it is doing.

## Claude

Good catch wanting visibility into this — the spread loop is exactly the part that can look stuck. Let me add debug prints through that section.

Now the spread loop itself — this is the part most likely to feel like a hang, so it gets the most coverage:

Let me verify it's syntactically valid and take a final look at the changed region:

Here's what's now printed, all tagged with `[DEBUG]` so it's easy to grep or filter out later:

- **Seed selection** — which blocks were picked as Democrat seeds, Republican seeds, and the total seed count.
- **District creation** — one line per district as it's created, showing its number, party, seed block, and starting population.
- **Spread phase progress** — a line every 100 newly-claimed blocks (set `DEBUG_PRINT_EVERY` near the top of that loop to change the frequency), showing `assigned/total`, the loop count, which district claimed a block, and its running population vs. the target.
- **Stalls** — a line whenever a district runs out of frontier and gets benched (`priority = -inf`), so you can see if growth is grinding to a halt well before completion.
- **Fallback trigger** — a clear message if every district stalls simultaneously and the leftover-block dump kicks in, including how many blocks got dumped and into which district.
- **Completion summary** — total loop iterations and final assigned/total count once the spread phase ends.

One thing to flag: I didn't fix the `Index()` O(n²) lookup or the `frontier.pop(0)` O(n) issue from before. With those still in place, on a real CSV with thousands of blocks you'll likely see the progress lines start coming in noticeably slower as `loop_count` climbs — that's the algorithmic cost, not a hang, and the debug output should make that visible rather than leaving you guessing. Let me know if you want those two performance fixes too; they're a quick change and would make the progress lines pour in much faster.

## User

The program is stuck here.

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
        nextP += 1
        if(nextP == 5000):
            nextP = 0
            print("Current Neighbors: " + str(neighbors))

It has been running for 30 mins. How can this be optimized to reduce the amount of time? The amount of data on avg is 200-300k

## Claude

The hang makes sense once you look at what that loop is actually doing: `bisect_left`/`bisect_right` only narrow the candidates by **latitude**. They say nothing about longitude. So for every block, `distRange` includes every other block in a similar latitude band *across the entire width of the state* — not just the ones physically nearby. For 200-300k real census blocks, that band can easily contain tens of thousands of "candidates" per block, most of which get rejected only after the longitude check inside the loop. That's roughly O(n × band_size), which at this scale is billions of inner-loop iterations — each one also re-doing a dict `.get()` it doesn't need. That's your 30 minutes (and counting).

Good — `lat_values` and the bisect calls are only used in this one block, so I can replace the whole thing cleanly. The fix: bucket blocks into a 2D grid (cells sized `minDist × minDist`) and only ever compare a block against the ~9 cells immediately around it, instead of the whole latitude band. I'm also fixing two smaller wastes: the redundant `dict.get()` call on every inner iteration, and the fact that every pair was being checked **twice** (once from each side) — now each pair is checked once and added to both lists at the same time.

Let me verify this is both correct and actually fast before handing it back — I'll test logical equivalence against the old method on a small dataset, then benchmark the new approach at your real-world scale.

Results match exactly — 0 mismatches. Now let's see what this looks like at your actual scale:

That's the difference: the old method scaled with how wide your data is geographically (it scanned the *entire* longitude span for each latitude band), while the grid method's cost depends only on local density. **At 250,000 blocks spread over a typical state-sized area, the new neighbor search finishes in about 37 seconds** — down from a 30+ minute hang that hadn't even finished.

**What changed, and what I checked:**

- Replaced the latitude-only bisect scan with a **2D spatial grid**: blocks are bucketed into cells sized `minDist × minDist`, and each block only checks the 9 cells around it (its own + 8 neighbors) instead of every block sharing a similar latitude across the whole state.
- Removed the per-candidate `dict.get()` that was running on every inner-loop pass even when nothing got appended.
- Each pair is now checked **once** (via an ID comparison) and added to both blocks' neighbor lists at the same time, instead of being discovered twice from opposite directions.
- **Verified correctness**: ran both the old and new method on 3,000 synthetic blocks — identical neighbor sets, 0 mismatches.
- **Verified speed**: benchmarked the new method at 250,000 blocks over a realistic geographic extent — **~37 seconds**, finding 8.6M neighbor pairs.

One thing worth flagging now that this part is fast: the next stage of your script (the district-spreading `while` loop) has the `Index()` function I mentioned earlier, which does a full linear scan of `list_of_blocks` for every single block claim. At 250k+ blocks, that part is likely to become the new bottleneck once you get past the neighbor search. Want me to apply that fix too while we're in here?

## User

The while loop worked. But I got this error when it finished.

Traceback (most recent call last):
  File "C:\Users\xrock\OC_Classes\AI_Project_T1\Gary-Manjerin\Reasonable_Gerrymandering\gerrymander.py", line 261, in <module>
    for district_num, (seed_id, seed_pop) in enumerate(all_seeds):
                      ^^^^^^^^^^^^^^^^^^^
TypeError: cannot unpack non-iterable int object

## Claude

Found it. `highest_pops` (your Democrat seeds) stores `(id, population)` tuples, but `rep_Seeds` only stores the bare ID:

```python
rep_Seeds.append(block[Data.ID.value])   # just an int, not a tuple
```

So `all_seeds = list(highest_pops) + rep_Seeds` ends up as a mix of 2-tuples and plain ints. The unpacking `for district_num, (seed_id, seed_pop) in enumerate(all_seeds)` works fine through the Democrat portion, then crashes the moment it hits the first Republican entry, which is just an int with nothing to unpack. This bug was already in the file before any of my changes — the grid optimization just got you far enough to reach it.

Fix is to make `rep_Seeds` store the same `(id, population)` shape:

Let me confirm this with a quick synthetic test that exercises the exact code path that crashed:

Confirmed working. Let me make sure the full file still compiles and hand it back:

That should clear the crash and let it run to `print_dict(districts)`. Two things worth knowing as you keep going:

1. **The `Index()` linear-scan issue I flagged earlier is still in there.** Now that the neighbor search and seeding both work, the district-spreading `while` loop is the next thing likely to feel slow at 200-300k blocks, for the same root cause (O(n) lookup repeated per claim). Happy to swap it for the `id_to_index` dict you already built, plus switch `frontier.pop(0)` to a `deque`, if you want that done before your next full run.
2. Once it finishes, take a look at `print_dict`'s output for the Republican districts specifically — worth double-checking the populations look reasonable, since `rep_Seeds` was silently broken until now and this is the first time that part of the seeding logic has actually run end-to-end.

## User

when trying to gerrymander California it stops and sits for way too long. What is going on?

[DEBUG] All districts stalled at 41498/519723 blocks assigned. Dumping 478225 leftover block(s) into district 8 (R, currently smallest).
Traceback (most recent call last):
  File "C:\Users\xrock\OC_Classes\AI_Project_T1\Gary-Manjerin\Reasonable_Gerrymandering\gerrymander.py", line 319, in <module>
    block = Index(leftover_id)
  File "C:\Users\xrock\OC_Classes\AI_Project_T1\Gary-Manjerin\Reasonable_Gerrymandering\gerrymander.py", line 74, in Index
    if id == block[0]:
       ^^^^^^^^^^^^^^
KeyboardInterrupt
^C

## Claude

That traceback is exactly the bottleneck I flagged a few turns back finally catching up with you. Let's look at the math: it stalled with only 41,498 of 519,723 blocks assigned through real growth, so it tried to dump the other **478,225** leftover blocks into district 8. For *each one* of those, `Index()` still does a full linear scan through all 519,723 blocks to find it:

```python
def Index(id):
    for block in list_of_blocks:
        if id == block[0]:
            return block
```

That's roughly 478,225 × 519,723 ≈ **250 billion** comparisons just for the leftover dump — easily hours, which is why it looked frozen and you had to Ctrl-C it. The fix is the one-line change I mentioned earlier: you already built an `id_to_index` dict for O(1) lookups, but `Index()` never uses it.

Now let's prove this actually fixes the leftover-dump bottleneck at California's scale, not just compiles:

That confirms it — the leftover-dump alone would have taken roughly half an hour to several hours depending on machine speed; now it's under half a second.

But there's a second, more important problem hiding in that same debug line, and the speed fix won't touch it:

**Only 8% of California's blocks (41,498 of 519,723) ever got assigned through real district growth.** The other 92% never had a reachable neighbor from any seed, so they all got bulk-dumped into a single Republican district instead of growing organically block-by-block.

That's almost certainly a side effect of `minDist = 0.05` being a **fixed** distance threshold. California's census blocks vary enormously in size — tiny in dense cities, but huge across deserts, mountains, and farmland. A rural block's centroid can easily sit farther than 0.05° (~5.5 km) from its nearest actual neighbor, so it ends up totally isolated in your neighbor graph — no edges in or out. Once a block has no neighbor link, it can never be reached by the BFS-style spread, no matter how long you let it run. Likely outcome on a state this geographically diverse: dense urban clusters get linked up fine, while most of the state's land area — and apparently most of its blocks by count too — ends up isolated and gets unceremoniously stuffed into whichever district happens to be smallest at the time.

That means even with the speed fix, you'll get a fast result, but one district will be a meaningless catch-all rather than a real contiguous district. A few ways to actually fix that, roughly in order of effort:

1. **Scale `minDist` per block** based on local point density (e.g., distance to the block's *k*-th nearest neighbor) instead of one fixed number for the whole state.
2. **Use k-nearest-neighbors instead of a radius** — guarantee every block gets at least, say, 4 neighbors regardless of how sparse its area is.
3. **Use real adjacency data** (shared borders from the actual block shapefiles/geometry) instead of a centroid-distance proxy — this is the "correct" answer for gerrymandering specifically, since geographic closeness isn't the same as sharing a border.

Want me to implement option 2 (k-NN) first? It's the smallest change relative to what you have now and should reconnect most of the isolated rural blocks without a full rewrite.

## User

yes please fix the Index() method and allow for a scalable minDist to prevent unnecessary dumping. Thanks

## Claude

Let me look at the current full file to plan this cleanly — I want to confirm exact line order before editing.

Now let's stress-test this against exactly the scenario that bit you — a state-sized area with a dense urban cluster plus a sparse rural majority:

Both fixes are in and verified end-to-end. On a synthetic CA-like dataset (dense urban cluster + sparse rural spread, 60,000 blocks):

| | Before top-up | After top-up |
|---|---|---|
| Fully isolated (0 neighbors) | 52 | **0** |
| Below `MIN_NEIGHBORS` (4) | 3,561 | **0** |
| Extra time cost | — | **0.16s** |

The top-up pass only touches the sparse minority of blocks, so the cost is negligible even though it's doing more work per block.

**What's in the updated file:**

1. **`Index()`** — confirmed still using the O(1) `id_to_index` lookup from last time.
2. **Adaptive neighbor radius** — the base pass at `minDist = 0.05` runs unchanged (fast, fine for dense areas). Afterward, any block with fewer than `MIN_NEIGHBORS` (default 4) gets its own search expanded outward ring-by-ring through the grid until it finds enough neighbors, capped at `MAX_RING_EXPANSION` (default 40) so a truly empty area can't search forever.
3. New debug lines tell you exactly how many blocks needed topping up, and — importantly — **how many are still isolated even after max expansion**. If that number comes back nonzero on the real California run, it's a good signal to double check the lon/lat columns are actually in degrees and not some pre-scaled feature space from the prediction pipeline.

Both `MIN_NEIGHBORS` and `MAX_RING_EXPANSION` are plain variables near the top of that section if you want to tune them — raising `MIN_NEIGHBORS` gives sturdier district shapes at the cost of a bit more time in the top-up pass.

Give it a run on California and check that `still_isolated` line — should be a very different picture than 478,225 blocks getting dumped into one district.

