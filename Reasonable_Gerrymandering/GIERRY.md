My **(Seth)** plan to get part III solved


#### Master plan to get this to work

### Recap
# This is essentially what we have done.
- look at the picture (population_sticking_out)
- We mapped the state's lon and lat using the blocks, then we have the blocks ejected into the 3d space to express population
- the svm then trains on this with the answers and is able to predict the vote shares between the parties.
### Imagine Clustering
# Requirements
- Program must have these inputs
    - The number of districts required **(input => N)**
    - The desired number of districts for each party (these will add up to the total)
- The districts should be assigned in such a way that they are contiguous, and have a number of districts won by each party as close to the desired number as possible.
# Determining districts.
- Using the inputed number, **N**, for democrat iterate this algorithm
    - Since we know higher populations generally means democrat, we can find the highest population predicted democrat in a state then use that as a seed.
        - The seed is the start of clustering where we look at the nearest neighbors (possibly could implement a clustering model to do this for us)
        - We expand the area to absorb the nearest blocks that stay above the (50% or n%) threshhold for democrat. If no more can be found then we find the next highest population predicted democrat that is above the (50% or n%) threshhold that is not included in the cluster(s) already found. Repeat until **N** democrat districts exist. 
        - Then repeat for republican till there are **(total - N)** republican districts.
    - I'd imagine we have to reiterate through the disctricts to determine if certain blocks need to change districts to *"perfectly"* Gerrymander, but I am unsure as of right now how that would be done. 