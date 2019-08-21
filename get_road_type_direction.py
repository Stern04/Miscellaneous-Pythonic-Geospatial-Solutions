import arcpy

##This ad hoc tool is used to take a given value, in this case a value with a full street name, and extract
##from it the direction (if any) of the road as well as the type of road (street, ave, blvd) etc.Typical
##format of the input value is 'N MAIN ST', 'ALLEGHENY BLVD' etc.


##Paths hardcoded for testing. Use arcpy.GetParameterAsText() to implement geoprocessing tool.
GDB = r"\\Bhptfs2\proj\77107-07\16-GIS\Geodatabases\UMFR_Main_GDB.gdb"
Update_FC = r"\\Bhptfs2\proj\77107-07\16-GIS\Geodatabases\UMFR_Main_GDB.gdb\UMFR_Merge_2019_08_14"
##Paths hardcoded for testing. Use arcpy.GetParameterAsText() to implement geoprocessing tool.

#Begin an editing session on the GDB
edit = arcpy.da.Editor(GDB)
edit.startEditing(False, True)
edit.startOperation()

#Initialize UpdateCursor to find the full adress and the parse to find the street direction and type (specified in the fields called in the cursor below).
with arcpy.da.UpdateCursor(Update_FC, ['Strt_Name','Strt_Type','Strt_Direc']) as cursor:
    #Iterate through each row/value in Update_FC.
    for row in cursor:
        #Continue only if the value is neither blank nore a Null value.
        if row[0] != " " and row[0] != None:

            #Initialize empty strings to hold potential parsed values of 'row'.
            strt_type = ''
            strt_direction = ''

            #Initialize a list of possible street types for the input parced value'strt_type'to be checked against. If this value is contained in the list, the value is added.
            possible_types = ['AVE','BLVD','CIR','PLAZA','PL','PK','PARK','RD','REAR','ST', 'SQ','WAY']

            #Parse the full street address
            strt_parts = row[0].split()
            #If the ending piece of the full street address is in 'possible_types', add the type to 'the Update_FC'.
            if strt_parts[-1] in possible_types:
                strt_type = strt_parts[-1]

            #Initialize a list of possible street directions for the input parced value'strt_direction'to be checked against. If this value is contained in the list, the value is added.
            possible_directions = ['NORTH','SOUTH','EAST','WEST', 'NORTHERN', 'SOUTHERN', 'EASTERN', 'WESTERN', 'N', 'S', 'E', 'W']

            #If the starting piece of the full street address is in 'possible_directions', add the type to 'the Update_FC'.
            if strt_parts[0] in possible_directions:
                strt_direction = strt_parts[0]

            #Set the values of the 'Update_FC' to the values extracted from the full street addres and execute the update.
            row[1] = strt_type
            row[2] = strt_direction
            cursor.updateRow(row)

#Save the editing session and save edits.
edit.stopOperation()
edit.stopEditing(True)
