import pathlib as path
import io as io

import tkinter.filedialog
import shapefile
import os.path

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

def Format_File():
    # Let user decide how to input shape files
    while True:
        choice = input("Choose what you'd like to do:\n1. Automatically search the computer for all shape files\n2. Use a file-picker dialog\n3. Use Cached Shape Files (only available after option 1 at least once)\n")
        print("")
        if choice == "1" or choice == "2" or choice == "3":
            break

    # Auto-searches for all shape files in the whole computer and returns a list. Faster than typing a file path in
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
        selected_path = tkinter.filedialog.askopenfilename()

    # If the user neglects the whole search, instead use a database stored on the computer
    elif choice == "3" and (os.path.exists("shapefiles.csv")):
        shapefile_list = check_database()

    # Choose from list of shape files that were cached or detected
    if choice == "1" or choice == "3":
        for x in range(len(shapefile_list)):
            print(str(x) + ": " + str(shapefile_list[x])[str(shapefile_list[x]).rfind("/") + 1:]) 
        selected_path = shapefile_list[int(input("Please enter the index of the file you would like to use (start at 0 and count up): "))]

    # Initialize shapefile reader and records/shapes
    sf = shapefile.Reader(selected_path)

    #get records and shapes
    records = sf.records()
    shapes = sf.shapes()

    print("Parsing through records...")

    # Initialize votes and lists of locations in each record
    republicanVotes = 0
    democratVotes = 0
    repub_places = []
    dem_places = []
    fields = []

    # Find the field placements for president, senators, and delegates 
    # for dynamic num state vote accuracy 
    party = 6
    def repOrDem(s, x):
        if(str(s[party]) == "R"):
            repub_places.append(int(x))
        elif(str(s[party]) == "D"):
            dem_places.append(int(x) - 1)
        return

    # Relate each field with a spot in the record format
    pre_start = 0
    pre_end = 0
    sen_start = 0
    sen_end = 0
    con_start = 0
    con_end = 0
    for x in sf.fields[1:]: #keep
        fields.append(x.name)
        field = x.name if x.name.startswith("G20") else ""

        # Calculate locations of voting-groups in records
        pre_find = field.find("PRE")
        sen_find = field.find("USS")
        con_find = field.find("COC")

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

    print("Finished!")
    # Create training/testing directories if they don't already exist
    if not os.path.exists(os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + "/training"):
        os.mkdir(os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + "/training")
    if not os.path.exists(os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + "/testing"):
        os.mkdir(os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + "/testing")

    print("Writing training file...")

    # file to training csv
    with open(os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + "/training/" + selected_path[selected_path.rfind("/") + 1:-4] + "_train" + ".csv", 'w') as file:
        # file.write(" ID, Longitude, Latitude, Population, Total Votes, Republican Vote Share, Democratic Vote Share\n")

        # Totals used to calculate grand total
        global_president_votes = 0
        global_senate_votes = 0
        global_congress_votes = 0

        # Main processor loop
        for i in range(len(records)):

            #separate records into variables
            record = records[i]
            shape = shapes[i]
            lineId = record[0]
            population = record[4]

            #grapping the number of votes for President, Senator, and Delegates    
            presidentVotes = 0
            for x in range(pre_end - pre_start):
                presidentVotes += float(record[x + pre_start])
            global_president_votes += presidentVotes
        
            senateVotes = 0
            for x in range(sen_end - sen_start):
                senateVotes += float(record[x + sen_start])
            global_senate_votes += senateVotes
        
            congressVotes = 0
            for x in range(con_end - con_start):
                congressVotes += float(record[x + con_start])
            global_congress_votes += congressVotes
            
            #finding num republican and democrat votes
            for x in range(len(repub_places)):
                republicanVotes += float(record[repub_places[x]])
            for x in range(len(dem_places)):
                democratVotes += float(record[dem_places[x]])
            
            #calculate votes and shares
            try: 
                total_votes = float(global_president_votes) + float(global_senate_votes) + float(global_congress_votes)
            except (ValueError, TypeError):
                total_votes = 0

            if total_votes > 0: #check if total votes aren't zero to prevent dividing by zero
                rep_share = republicanVotes / total_votes
                dem_share = democratVotes / total_votes
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

            #putting file line data together and writing it
            file.write(str(i) + "," + str(longitude) + "," + str(latitude) + "," + str(population) + "," + str(total_votes) + "," + str(rep_share) + "," + str(dem_share) + "\n")

            # Reset totals to begin a new line
            global_president_votes = 0
            global_senate_votes = 0
            global_congress_votes = 0
            total_votes = 0
            republicanVotes = 0
            rep_share = 0
            democratVotes = 0
            dem_share = 0
        print("Finished!")

    print("Writing test file...")
    # file to testing csv
    with open(os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + "/testing/" + selected_path[selected_path.rfind("/") + 1:-4] + "_test" + ".csv", 'w') as file:
        with open(os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + "/training/" + selected_path[selected_path.rfind("/") + 1:-4] + "_train" + ".csv", 'r') as  trainer:
            for _line in trainer:
                __line = _line.strip().split(",")
                #longitude , latitude , population, total votes
                file.write(__line[0] + "," + __line[1] + "," + __line[2] + "," + __line[3] +  "\n")
    print("Finished!\n\nCheck your /training/ and /testing/ directories now.\nOutput files are named after the original shape file you uploaded.")

    return None