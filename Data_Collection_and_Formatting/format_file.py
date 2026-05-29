import pathlib as path
import io as io

import tkinter.filedialog
import shapefile
import os.path
import csv

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
    common_path = os.path.commonprefix(shapefile_list)
    for x in range(len(shapefile_list)):
        print(str(x) + ": " + str(shapefile_list[x]).removeprefix(common_path)) 
    default_path = shapefile_list[int(input("Please enter the index of the file you would like to use (start at 0 and count up): "))]

sf = shapefile.Reader(default_path)

#get records and shapes
records = sf.records()
shapes = sf.shapes()

#removing magic number in repOrDem
party = 6
#finding the place for only necessary for the Pres, Sen, and Cong
def repOrDem(field, field_placement):
    if(str(field[party]) == "R"):
        repub_places.append(int(field_placement))
    elif(str(field[party]) == "D"):
        dem_places.append(int(field_placement) - 1)
    return

#finding where the republican/democrat candidates are in the records
repub_places = []
dem_places = []
#to store the name fields and filter out the positions 
fields = []
#This finds the field placements for president, senators, and delegates for dynamic num state vote accuracy 
pre_start = 0
pre_end = 0
sen_start = 0
sen_end = 0
con_start = 0
con_end = 0

for x in sf.fields[1:]:
    #add to fields to track index of the titles
    fields.append(x.name)
    field = x.name if x.name.startswith("G20") else ""

    #local vars for simplicity
    pre_find = field.find("PRE")
    sen_find = field.find("USS")
    con_find = field.find("DEL")

    #finding the starting and ending indexes for the titles
    if(pre_find != -1 and pre_start == 0):
        pre_start = len(fields) - 1
        repOrDem(field, pre_start)
    elif(pre_find != -1):
        pre_end = len(fields)
        repOrDem(field, pre_end)
    if(sen_find != -1 and sen_start == 0):
        sen_start = len(fields) - 1
        repOrDem(field, sen_start)
    elif(sen_find != -1):
        sen_end = len(fields)
        repOrDem(field, sen_end)
    if(con_find != -1 and con_start == 0):
        con_start = len(fields) - 1
        repOrDem(field, con_start)
    elif(con_find != -1):
        con_end = len(fields)
        repOrDem(field, con_end)
    
#file to csv
file = io.open("training_data.csv", 'w')
file.write(" ID, Longitude, Latitude, Population, Total Votes, Republican Vote Share, Democratic Vote Share\n")

for i in range(len(records)):

    record = records[i]
    shape = shapes[i]
    lineId = record[0]
    population = record[4]

    #grapping the number of votes for President, Senator, and Delegates    
    presidentVotes = 0
    for x in range(pre_end - pre_start):
        presidentVotes += float(record[x + pre_start])
        # print("president votes: " + str(presidentVotes) + " for \n" + str(record) + "\n")
   
    senateVotes = 0
    for x in range(sen_end - sen_start):
        senateVotes += float(record[x + sen_start])
   
    congressVotes = 0
    for x in range(con_end - con_start):
        congressVotes += float(record[x + con_start])
    
    republicanVotes = 0
    democratVotes = 0
    #finding num republican and democrat votes
    for x in range(len(repub_places)):
        republicanVotes += float(record[repub_places[x]])
    for x in range(len(dem_places)):
        democratVotes += float(record[dem_places[x]])
    

    try: #calculate votes
        total_votes = float(presidentVotes) + float(senateVotes) + float(congressVotes)
    except (ValueError, TypeError):
        total_votes = 0

    #check if total votes aren't zero to prevent dividing by zero
    if total_votes > 0:
        rep_share = float(republicanVotes / total_votes)
        dem_share = float(1 - rep_share)
    else:
        rep_share = 0
        dem_share = 0


    #get bounding box (top left corner, bottom right corner)
    bbox = shape.bbox

    xmin = bbox[0]
    ymin = bbox[1]
    xmax = bbox[2]
    ymax = bbox[3]

    # Get center of bounding box
    longitude = (xmin + xmax) / 2
    latitude = (ymin + ymax) / 2

    #putting file line data together
    assembled_data = str(lineId) + "," + str(longitude) + "," + str(latitude) + "," + str(population) + "," + str(total_votes) + "," + str(rep_share) + "," + str(dem_share) + "\n"
    #writing to file
    file.write(assembled_data)

