import arcpy, datetime
arcpy.env.overwriteOutput = True
WET_FLAG = r'C:\Sternberger\LOCAL_GPS_DATA_TEST\Homer City-Indiana\merged\WET_FLAG_Merge.shp'
workspace = r'C:\Sternberger\LOCAL_GPS_DATA_TEST\Homer City-Indiana\Working.gdb'
arcpy.AddMessage(str(WET_FLAG))
arcpy.AddMessage(type(WET_FLAG))
print(str(WET_FLAG))
print(type(WET_FLAG))



start_time = datetime.datetime.now()
print("Start time: " + str(start_time))
#Wetlands
##########################################################################################################################################################################################################################################
##########################################################################################################################################################################################################################################
##########################################################################################################################################################################################################################################
#Create blank lists to store wetland IDs and wetland IDs for post processing review. 
Wetland_IDs = []
Wetland_IDs_REVIEW = []

#Initialize attribute field lists for features. Initialize an open end line feature class to append open ends into
wetlands = arcpy.CreateFeatureclass_management(workspace, '\wetlands', 'POLYLINE')

wetland_att_list = [('Project_Name', 'TEXT','','','50','','',''),('GAI_ID', 'TEXT','','', '16','','',''),('Type','TEXT','','','8','','',''),('Jurisdiction','TEXT','','','16','','',''),
                    ('Open_End','TEXT','','','8','','',''),('GPS_Date','DATE','','','','','',''),('Mod_Date', 'DATE','','','','','',''),('Latitude', 'DOUBLE','','','','','',''),
                    ('Longitude', 'DOUBLE','','','','','',''),('Acres','DOUBLE','','','','','',''),('Impact','TEXT','','','8','','',''),('RC_ID','TEXT','','','8','','',''),('SSW_ID','TEXT','','','8','','',''),
                    ('Comment','TEXT','','','50','','',''),('CR_Intersect','TEXT','','','8','','','')]
for att in wetland_att_list:
    arcpy.AddField_management(*(wetlands,)+att)

open_ends = arcpy.CreateFeatureclass_management(workspace, '\open_ends', 'POLYLINE')

open_end_att_list = [('Project_Name', 'TEXT', '','','50','','',''), ('GAI_ID', 'TEXT','','', '16','','',''),('Type','TEXT','','','8','','',''),('Jurisdiction','TEXT','','','16','','',''),
                    ('GPS_Date','DATE','','','','','',''),('Mod_Date', 'DATE','','','','','',''), ('Impact','TEXT','','','8','','',''),('RC_ID','TEXT','','','8','','',''),('SSW_ID','TEXT','','','8','','',''),
                    ('Comment','TEXT','','','50','','','')]

for att in open_end_att_list:
    arcpy.AddField_management(*(open_ends,)+att)
#Append all WET_FLAG points into ENV_GDB

#Below draws the wetlands based upon the gps points taken and will ultimately append them into the ENV_GDB
#Create a list of stream features to iterate through.
GAI_ID_count = 0
with arcpy.da.SearchCursor(WET_FLAG, "GAI_ID") as cursor:
    for row in cursor:
        if row[0] not in Wetland_IDs:
            Wetland_IDs.append(row[0])
            GAI_ID_count += 1
print((str(GAI_ID_count) + " unique GAI IDs."))
print(Wetland_IDs)
unique_ID = 1
#Iterate through each grouping of features (GAI_ID), draw the feature, transfer attributes to the derived feature, and append the feature into the ENV_GDB. 
for ID in Wetland_IDs:
    print(ID)
    ID_original = str(ID)
    ID_replace_one = ID_original.replace(" ", "_")
    ID_replace_final = ID_replace_one.replace("-", "_")
    wetland_lyr = arcpy.MakeFeatureLayer_management(WET_FLAG, "wetland_lyr", where_clause='"GAI_ID" =' + "'%s'" %ID) 
    #Make a blank list for flag nums to make sure each number occurs only once. If more than one flag has the same number, add to Wetland_IDs_REVIEW.##################################################################################### 
    wetland_lyr_flagnums = []
    with arcpy.da.SearchCursor(wetland_lyr, "Flag_num") as cursor:
        for row in cursor:
           if row[0] not in wetland_lyr_flagnums:
                wetland_lyr_flagnums.append(row[0])
           else:
                print("Feature " + str(ID) + " needs reviewed. More than one flag has the same number. Adding ID to review list")
                Wetland_IDs_REVIEW.append(ID)
                break
    #Check to make sure there are at least three points for the feature to be drawn from.
    #Test to make sure flags increase sequentially by an interval of 1. If not, its possible a flag was missed. Add to Wetland_IDs_REVIEW if not.######################################################################################## 
    length_flagnums = len(wetland_lyr_flagnums)
    if length_flagnums <= 2 and ID not in Wetland_IDs_REVIEW:
        print("Feature " + str(ID) + " consists of " + str(length_flagnums) + " point(s). A wetland cannot be drawn. Adding ID to review list.")
        Wetland_IDs_REVIEW.append(ID)
    max_flagnums = max(wetland_lyr_flagnums)
    #If biggest number in list flag nums is not also the length of the list, this implies that a flag number was skipped (flag nums do not all increase by interval of one)
    if max_flagnums > length_flagnums and ID not in Wetland_IDs_REVIEW:
        print("Feature " + str(ID) + " needs reviewed. Flag numbers do not all increase by interval of one. A flag may have possibly been skipped or querried out. Adding ID to review list.")
        Wetland_IDs_REVIEW.append(ID)
    #Iterate through each grouping of features (GAI_ID), draw the feature, transfer attributes to the derived feature, and append the feature into the ENV_GDB.
    if ID not in Wetland_IDs_REVIEW:
        print(ID)
        wetland_outline = arcpy.PointsToLine_management(wetland_lyr, workspace + "\wetland_line_" + str(ID_replace_final) + "uID_" + str(unique_ID), Sort_Field = "Flag_num", Close_Line = "CLOSE")
        wetland = arcpy.FeatureToPolygon_management(wetland_outline, workspace + "\wetland" + str(ID_replace_final)+ "uID_" + str(unique_ID))
        unique_ID += 1
        wetland_parts = int(arcpy.GetCount_management(wetland).getOutput(0))
        if wetland_parts >= 2:
            print("Wetland consists of " + str(wetland_parts) + " parts and therefore intersects itself. Adding " + str(ID) + " to Wetland_IDs_REVIEW.")
            Wetland_IDs_REVIEW.append(ID)
            arcpy.DeleteFeatures_management(wetland)
        else:
            #Add attribute values to wetland from wetland_lyr
            for att in wetland_att_list:
                arcpy.AddField_management(*(wetland,)+att)
            #Initialize variable to store wetland type and open end.
            wetland_type = ''
            open_end = 'No'
            #For the wetland type in particular, we must confirm that each point in wetland_lyr has the same value (type). If so, the value will be used to populate the wetland_type field. If not,
            #the field will be left blank.
            #Initialize list to count if there is more than 1 wetland type for the wetland_lyr
            type1_holder = []
            with arcpy.da.SearchCursor(wetland_lyr, "Type_1") as cursor:
                for type1 in cursor:
                    if type1[0] not in type1_holder:
                        type1_holder.append(type1[0])
            if len(type1_holder) == 1:
                wetland_type = type1_holder[0]
            else:
                print('Wetland ' + str(ID) + ' is more than one type and its partitioning must be done manually.')
            open_end_holder = []
            with arcpy.da.SearchCursor(wetland_lyr, "Flag_type") as cursor:
                for i in cursor:
                    if i[0] == 'Open End' or i[0] == 'End/Open End':
                        open_end = 'Yes'
                        break
                
            #Update values of wetland with values from wetland_lyr points
            #Start editing
            edit = arcpy.da.Editor(workspace)
            edit.startEditing(False, True)
            edit.startOperation()    
            update_fields = ['GAI_ID','Jurisdic','GPS_Date']
            with arcpy.da.SearchCursor(wetland_lyr, ['GAI_ID', 'Jurisdicti', 'GPS_Date']) as cursor1:
                for row1 in cursor1:
                    GAI_ID, Jurisdiction, GPS_Date = row1[0], row1[1], row1[2]
                    with arcpy.da.UpdateCursor(wetland, ['GAI_ID', 'Jurisdiction', 'GPS_Date']) as cursor2:
                        for row2 in cursor2:
                            for i in range(0,len(update_fields)):
                                row2[i] = row1[i]
                                cursor2.updateRow(row2)
            with arcpy.da.UpdateCursor(wetland,['Type', 'Open_End']) as cursor3:
                for row3 in cursor3:
                    if len(wetland_type) > 0:
                           row3[0] = wetland_type
                    row3[1] = open_end
                    cursor3.updateRow(row3)
            edit.stopOperation()
            edit.stopEditing(True)

            #Append wetland into wetlands feature class
            arcpy.Append_management(wetland, wetlands, 'NO_TEST')



            #Draw open ends if wetland is open ended
            if open_end == 'Yes':
                #print('open end start')
                open_end_var, open_end_var2 = "Open End", "End/Open End"
                open_end_lyr = arcpy.MakeFeatureLayer_management(wetland_lyr, "open_end_lyr", where_clause='"Flag_type" =' + "'%s'"%open_end_var + 'OR "Flag_type" =' + "'%s'" %open_end_var2)
                wetland_split = arcpy.SplitLineAtPoint_management(wetland_outline, wetland_lyr, workspace + "\wetland" + str(ID_replace_final)+ "uID_" + str(unique_ID), "1")
                with arcpy.da.SearchCursor(wetland_split, 'SHAPE@') as cursor:
                    for line in cursor:
                        #Add attribute values to line from open_end_lyr
                        for att in open_end_att_list:
                            arcpy.AddField_management(*(line,)+att)
                        #print('in open end for loop')
                        arcpy.SelectLayerByLocation_management(open_end_lyr, "INTERSECT", line)
                        open_count = int(arcpy.GetCount_management(open_end_lyr).getOutput(0))
                        if open_count < 2:
                            #print('open count <2')
                            arcpy.DeleteFeatures_management(line)
                        else:
                            #Attribute and add open end
                            #print('adding open end')
                            edit = arcpy.da.Editor(workspace)
                            edit.startEditing(False, True)
                            edit.startOperation()
                            fields_update = ['GAI_ID','Type_1','Jurisdic','Comment']
                            with arcpy.da.SearchCursor(open_end_lyr, ['GAI_ID','Type_1','Jurisdici','Comment']) as cursor1:
                                for row1 in cursor1:
                                    GAI_ID, Type, Jurisdiction, Comment = row1[0], row1[1], row1[2], row1[3]
                                    with arcpy.da.UpdateCursor(line, ['GAI_ID','Type','Jurisdiction','Comment']) as cursor2:
                                        for row2 in cursor2:
                                            for i in range(0,len(fields_update)):
                                                row2[i] = row1[i]
                                                cursor2.updateRow(row2)
                            edit.stopOperation()
                            edit.stopEditing(True)
                             
                            arcpy.Append_management(line, open_ends, 'NO_TEST')
                        
                    
            #arcpy.Append_management(wetland, ENV_GDB + "\Wetlands", "NO_TEST")


print("Wetland_IDs_REVIEW after: " + str(Wetland_IDs_REVIEW))
end_time = datetime.datetime.now()
elapsed_time = end_time-start_time
print("Elapsed time: " + str(elapsed_time))

        
