### Prediction Model named Gerry Jankins
 
 # Goals
 1. Given a set of census blocks and an amount of desired political party districts
 2. get our predicted files from part 2
 3. create districts that are contiguous (no gaps between them)
 
 Approach from the video
 1. Make all districts as close to the same population by branching out as much as possible. 
 2. Smooth out each district to minimize each shape's area (minimize branches/Gerrymanders)
 3. Make small changes to each district until you get as close to the desired amount of Republican/Democrat dominated districts as possible
 
 # Pseudo Code
 file = training_data of state
 model = tensorflow neural model
