import shapefile
import numpy as math
import pathlib as path

# Change this path when you're testing
# If we need to input files easier, we can ask user to input a path instead of hard-coding it

#Seth's path
default_path = "C:/Users/xrock/OC_Classes/AI_Project_T1/tx_2020_gen_2020_blocks/"

#Ethan's file path
# default_path = "C:/College/SummerClasses/"

#Seth's shape file
sf = shapefile.Reader(default_path + "tx_2020_gen_2020_blocks.shp")



# rec = sf.records()[0:10]
# fields = sf.fields
# print([x.name for x in sf.fields[1:]])
#firstRec = sf.record(1)
#for i in range(len(firstRec)):
#    print(str(sf.fields[i]) +  " " + str(firstRec[i]) + "\n")
    
    

#Ethan's shape file reader
# sf = shapefile.Reader("oktraining.shp")

#get records and shapes
records = sf.records()
shapes = sf.shapes()

#list for use in csv
training_data = []

for i in range(len(records)):

    record = records[i]
    shape = shapes[i]
    
    #separate records into variables
    #on assignment sheet: "The fields in the file are: ID, Longitude, Latitude, Population, 
        #Total Votes, Republican Vote Share, and Democratic Vote Share, in that order"
    lineId = record[0]
    population = record[1]
    presidentVotes = record[2]
    senateVotes = record[3]
    congressVotes = record[4]
    republicanVotes = record[5]
    democratVotes = record[6]

    # print("President Votes: " + str(presidentVotes) + " Senate Votes: " + str(senateVotes) + " Congress Votes: " + str(congressVotes))

    #get bounding box (top left corner, bottom right corner)
    bbox = shape.bbox

    xmin = bbox[0]
    ymin = bbox[1]
    xmax = bbox[2]
    ymax = bbox[3]

    # Get center of bounding box
    longitude = (xmin + xmax) / 2
    latitude = (ymin + ymax) / 2

    #calculate votes
    try:
        total_votes = float(presidentVotes) + float(senateVotes) + float(congressVotes)
    except (ValueError, TypeError):
        total_votes = 0

    #check if total votes aren't zero to prevent dividing by zero
    if total_votes > 0:
        rep_share = republicanVotes / total_votes
        dem_share = 1 - rep_share
    else:
        rep_share = 0
        dem_share = 0

    assembled_data = [population, (longitude, latitude), rep_share, dem_share]
    training_data.append(assembled_data)
path.Path("training_data.csv").write_text(str(training_data))
