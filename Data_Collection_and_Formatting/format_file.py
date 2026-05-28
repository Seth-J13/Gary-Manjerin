import shapefile
import io as io

# Change this path when you're testing
# If we need to input files easier, we can ask user to input a path instead of hard-coding it

#Seth's path
# default_path = "C:/Users/xrock/OC_Classes/AI_Project_T1/tx_2020_gen_2020_blocks/"
default_path = "C:/Users/xrock/OC_Classes/AI_Project_T1/ok_2020_gen_2020_blocks/"

#Ethan's file path
# default_path = "C:/College/SummerClasses/"

#Seth's shape file
# sf = shapefile.Reader(default_path + "tx_2020_gen_2020_blocks.shp")
sf = shapefile.Reader(default_path + "ok_2020_gen_2020_blocks.shp")
    
    

#Ethan's shape file reader
# sf = shapefile.Reader("oktraining.shp")

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