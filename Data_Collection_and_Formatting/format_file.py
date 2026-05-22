import shapefile

sf = shapefile.Reader("C:/Users/xrock/OC_Classes/AI_Project_T1/tx_2020_gen_2020_blocks/tx_2020_gen_2020_blocks.shp")
# rec = sf.records()[0:10]
# fields = sf.fields
# print([x.name for x in sf.fields[1:]])
firstRec = sf.record(1)
for i in range(len(firstRec)):
    print(str(sf.fields[i]) +  " " + str(firstRec[i]) + "\n")