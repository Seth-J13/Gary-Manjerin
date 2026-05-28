import pathlib as path
import numpy as math
import io as io

import tkinter.filedialog
import shapefile
import os.path
import csv

#Seth's path
# default_path = "C:/Users/xrock/OC_Classes/AI_Project_T1/tx_2020_gen_2020_blocks/tx_2020_gen_2020_blocks.shp"

#Ethan's file path
# default_path = "C:/College/SummerClasses/"

# This checks the stored database of shape files in the same directory.
# Used to save time while testing and executing
def check_database():
    with open("shapefiles.csv", "r") as shapefiles:
        shapefile_list = shapefiles.read().replace("\\", "/").strip().split(",")
        
    shapefiles.close()
    return shapefile_list

# This searches the entire computer for shape files.
def search_computer_for_shape_files():
    print("Searching... (this may take a while)\n")
    write_list = ""
    shapefile_list = []
    for _path in path.Path(os.path.expanduser("~")).rglob("*.shp"):
        write_list = write_list + str(_path) + ","
        shapefile_list.append(str(_path))

    # Build a database so the search doesn't need to be conducted again.
    with open("shapefiles.csv", "w") as shapefiles:
        shapefiles.write(write_list[:-1])
    shapefiles.close()

    for _item in shapefile_list:
        shapefile_list[shapefile_list.index(_item)] = _item.replace("\\", "/")

    return shapefile_list

while True:
    choice = input("Choose what you'd like to do:\n1. Automatically search the computer for all shape files\n2. Use a file-picker dialog\n3. Use Cached Shape Files (only available after option 1 at least once)\n")
    if choice == "1" or choice == "2" or choice == "3":
        break

# This code searches for all shape files in the whole computer and returns a list. Faster than typing a file path in
# Tell the user we're looking for shape files.
if choice == "1":
    if (os.path.exists("shapefiles.csv")):
        if (input("\nYour previous search was saved to a database! You can use that instead of checking again.\nSearch anyway? (y/n) ") == "y"):
            shapefile_list = search_computer_for_shape_files()
        else:
            shapefile_list = check_database()
    else:
        shapefile_list = search_computer_for_shape_files()

# Let the user opt to upload a file using a file-picker dialog
elif choice == "2":
    default_path = tkinter.filedialog.askopenfilename()

# If the user neglects the whole search, instead use a database stored on the computer
elif choice == "3" and (os.path.exists("shapefiles.csv")):
    shapefile_list = check_database()

if choice == "1" or choice == "3":    
    print(shapefile_list)
    default_path = shapefile_list[int(input("Please enter the index of the file you would like to use (start at 0 and count up): "))]

sf = shapefile.Reader(default_path)

#get records and shapes
records = sf.records()
shapes = sf.shapes()

#temp VVVV
fields = []
for x in sf.fields[1:]:
    fields.append(x.name)
recordFirst = records[0]
for x in range(len(fields)):
    print(str(fields[x]) + " : " + str(recordFirst[x]))

#temp ^^^^^

#list for use in csv
file = io.open("training_data.csv", 'w')
file.write(" ID, Longitude, Latitude, Population, Total Votes, Republican Vote Share, Democratic Vote Share\n")

for i in range(len(records)):

    record = records[i]
    shape = shapes[i]
    
    #separate records into variables
    #on assignment sheet: "The fields in the file are: ID, Longitude, Latitude, Population, 
        #Total Votes, Republican Vote Share, and Democratic Vote Share, in that order"
    #0-4 Block ID, State FIPS Code, Unique Precinct Identifier, Modified Voting Age (VAP)
    #5-10 President Candidates (5:Trump (Rep), 6:Biden (Dem), 7:Jorgensen (Lib), 8:West (Ind), 9:Simmons (Ind), 10:Pierce (Ind))
    #11-15 Senators Candidates (11:Inhofe (Rep), 12:Broyles (Dem), 13:Murphy (Lib), 14:Farr (Ind), 15:Nesbit (Ind))
    #16-17 Corporation Commissioner Candidates (16:Hiett (Rep), 17:Hagopian (Lib))
    lineId = record[0]
    population = record[4]
        
    presidentVotes = 0
    for x in range(6):
        presidentVotes += float(record[x + 5])
        
        
    senateVotes = 0
    for x in range(5):
        senateVotes += float(record[x + 11])
    congressVotes = 0
    for x in range(2):
        congressVotes += float(record[x + 16])

    republicanVotes = float(record[5]) + float(record[11]) + float(record[16])
    democratVotes = float(record[6]) + float(record[12])


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

    assembled_data = str(lineId) + "," + str(longitude) + "," + str(latitude) + "," + str(population) + "," + str(total_votes) + "," + str(rep_share) + "," + str(dem_share) + "\n"
    file.write(assembled_data)