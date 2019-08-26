# -*- coding: cp1252 -*-
import arcpy
from arcpy import da
import os

##Uncomment below 5 lines for use in geoprocessing tool.

#GDB = arcpy.GetParameterAsText(0)
#Update_FC = arcpy.GetParameterAsText(1)
#Attach_table = arcpy.GetParameterAsText(2)
#photo_directory = arcpy.GetParameterAsText(3)
#project_code = arcpy.GetParameterAsText(4)

#Hardcoded paths for use in testing.
GDB = r"\\Bhptfs2\proj\77107-07\16-GIS\Geodatabases\S123_b2b1ad1b6846483fa7dd883a05d95b1c_FGDB\a13dedd1a673476fb2078710924e4251.gdb"
Update_FC = r"\\Bhptfs2\proj\77107-07\16-GIS\Geodatabases\S123_b2b1ad1b6846483fa7dd883a05d95b1c_FGDB\a13dedd1a673476fb2078710924e4251.gdb\PWSA_Unmetered_Flat_Rate"
Attach_table = r"\\Bhptfs2\proj\77107-07\16-GIS\Geodatabases\S123_b2b1ad1b6846483fa7dd883a05d95b1c_FGDB\a13dedd1a673476fb2078710924e4251.gdb\PWSA_Unmetered_Flat_Rate__ATTACH"
photo_directory = r"\\Bhptfs2\proj\77107-07\16-GIS\Images\Survey_photos\\"
project_code = 'UMFR'

#Initialize a number to append to the end of file name 'dir_iterator' ensuring a
#file is not overwritten in the event of more than one survey of a particular entity.
unique_ID = 0

#Initialize UpdateCursor on Update_FC to populate the Photo field with paths to
#the image's repsective directory 'fileloc' using values from the fields called below.
#Create a directory for the set of images and write the images to the respective directory.
with arcpy.da.UpdateCursor(Update_FC, ['GlobalID_Static','St_Direc','St_Name','St_Type','St_Num','AcctID','Photo']) as cursor_1:
    for row_1 in cursor_1:

        #Begin an editing session on the GDB.
        edit = arcpy.da.Editor(GDB)
        edit.startEditing(False, True)
        edit.startOperation()

        #Initialize variables to hold values for the fields called out in cursor_1.
        fc_global, strt_direc, strt_name, strt_type, strt_num, locationID = row_1[0],row_1[1],row_1[2],row_1[3],row_1[4],row_1[5]

        #Create directory name for the photos for each survey (row_1) in Update_FC.
        dir_iterator = str(strt_direc) + '_' + str(strt_name) +\
        '_' + str(strt_type) + '_' + str(strt_num) + '_' + str(locationID) + '_' + str(project_code) + '_' + str(unique_ID)

        #Query the rows in Attach_table that are associated with row_1 in
        #Update_FC and name queried table 'table_view_' + the GlobalID_Static.
        arcpy.MakeTableView_management(Attach_table, "table_view_" + str(row_1[0]), where_clause = '"REL_GLOBALID" =' + "'%s'" %row_1[0])

        #Update the name of each photo in the queried Attach_table 'table_view_'+ the GlobalID_Static.
        with arcpy.da.UpdateCursor("table_view_" + str(fc_global), ['ATT_NAME']) as cursor_2:
            for row_2 in cursor_2:
                #Set the old value in Attach_table to the newly derived value
                #plus the old value. Execute the update.
                row_2[0] = dir_iterator + '_' + str(row_2[0])
                cursor_2.updateRow(row_2)

        #Create a directory in os with the the name 'dir_iterator'.
        directory = os.mkdir(photo_directory + dir_iterator)

        #Get this directory as a value 'fileloc' to populate row_1 in Update_FC
        #as the location of the file for reference. Execute the update.
        fileloc = photo_directory + dir_iterator
        row_1[6] = fileloc
        cursor_1.updateRow(row_1)

        #Save edits and stop the editing session of 'Update_FC'.
        edit.stopOperation()
        edit.stopEditing(True)


        #Extract and write the newly named images into the appropriate directory.
        with arcpy.da.SearchCursor("table_view_" + str(row_1[0]), ['DATA', 'ATT_NAME']) as cursor:
            for item in cursor:
                attachment = item[0]
                filename = str(item[1])
                #open the directory and write the file to it.
                open(fileloc + os.sep + filename, 'wb').write(attachment.tobytes())
                del item
                del filename
                del attachment
        #Increment unique_ID by 1 as it will ensure no subsequent files have an identical name.
        unique_ID += 1
