import shapefile

# Change this path when you're testing
# If we need to input files easier, we can ask user to input a path instead of hard-coding it
default_path = "C:/Users/xrock/OC_Classes/AI_Project_T1/tx_2020_gen_2020_blocks/"

sf = shapefile.Reader(default_path + "tx_2020_gen_2020_blocks.shp")
# rec = sf.records()[0:10]
# fields = sf.fields
# print([x.name for x in sf.fields[1:]])
firstRec = sf.record(1)
for i in range(len(firstRec)):
    print(str(sf.fields[i]) +  " " + str(firstRec[i]) + "\n")