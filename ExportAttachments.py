# -*- coding: cp1252 -*-
import arcpy
from arcpy import da
import os
from random import randint

##Uncomment below 5 lines for use in geoprocessing tool.

#GDB = arcpy.GetParameterAsText(0)
#Update_FC = arcpy.GetParameterAsText(1)
#Attach_table = arcpy.GetParameterAsText(2)
#photo_directory = arcpy.GetParameterAsText(3)
#project_code = arcpy.GetParameterAsText(4)

#Hardcoded paths for use in testing.
GDB = r"\\Bhptfs2\proj\77107-07\16-GIS\Geodatabases\2019_12_16\S123_b2b1ad1b6846483fa7dd883a05d95b1c_FGDB\bb104e303e004e7183b84bce56dbda96.gdb"
Update_FC = r"\\Bhptfs2\proj\77107-07\16-GIS\Geodatabases\2019_12_16\S123_b2b1ad1b6846483fa7dd883a05d95b1c_FGDB\bb104e303e004e7183b84bce56dbda96.gdb\PWSA_Unmetered_Flat_Rate"
Attach_table = r"\\Bhptfs2\proj\77107-07\16-GIS\Geodatabases\2019_12_16\S123_b2b1ad1b6846483fa7dd883a05d95b1c_FGDB\bb104e303e004e7183b84bce56dbda96.gdb\PWSA_Unmetered_Flat_Rate__ATTACH"
photo_directory = r"\\Bhptfs2\proj\77107-07\16-GIS\Images\Survey_photos_good\\"
project_code = 'UMFR'

#Initialize a number to append to the end of file name 'dir_iterator' ensuring a
#file is not overwritten in the event of more than one survey of a particular entity.
# dir_iterators = []
unique_ID = 0
edit = arcpy.da.Editor(GDB)
edit.startEditing(False, True)
edit.startOperation()

#Create dictionary to hold immutable Survey123 field values and the associated values to be used in photo naming
photo_naming = {'Loc_of_Existing_Watermain': 'Watermain', 'Loc_of_Existing_Watermain_2': 'Entrance', 'Existing_Curb_Stop': 'Curb_Stop', 'Existing_Curb_Stop_2': 'Curb_Stop2',
'ServiceLineEntryiIntoBuilding': 'SL_Entry','ServiceLineEntryIntoBuilding': 'SL_Entry', 'ServiceLineEntryiIntoBuilding_2': 'SL_Entry2','ServiceLineEntryIntoBuilding_2': 'SL_Entry2',
'ServiceLineExit': 'SL_Exit', 'ServiceLineExit_2': 'SL_Exit2', 'ServiceLineAccessAndPlumbing': 'SL_Access','ServiceLineAccessAndPlumbing_2': 'SL_Access2',
'ServiceLineAccessAndPlumbing2': 'SL_Access2', 'PotentialNewSLEntry': 'New_SL_Entry', 'ThermalExpansionTank': 'TET', 'ThermalExpansionTank_2': 'TET2', 'BackflowPreventer': 'Backflow',
'BackflowPreventer_2': 'Backflow2'}



#Initialize UpdateCursor on Update_FC to populate the Photo field with paths to
#the image's repsective directory 'fileloc' using values from the fields called below.
#Create a directory for the set of images and write the images to the respective directory.
with arcpy.da.UpdateCursor(Update_FC, ['GlobalID_Static','St_Direc','St_Name','St_Type','St_Num','AcctID','Photo']) as cursor_1:
    for row_1 in cursor_1:

        #Initialize variables to hold values for the fields called out in cursor_1.
        fc_global, strt_direc, strt_name, strt_type, strt_num, locationID = row_1[0],row_1[1],row_1[2],row_1[3],row_1[4],row_1[5]

        #If there is a street direction (else, we dont want an empty place holder in the photo name for street direction)
        if strt_direc != ' ':
            #Create directory name for the photos for each survey (row_1) in Update_FC.
            dir_iterator = str(strt_name) + '_' + str(strt_type) +\
            '_' + str(strt_direc) + '_' + str(strt_num) + '_' + str(locationID) + '_' + str(project_code) + '_' + str(unique_ID)

        #If there is no street direction, we do not want to include a place holder for that value.
        elif strt_direc == ' ':
            #Create directory name for the photos for each survey (row_1) in Update_FC.
            dir_iterator = str(strt_name) + '_' + str(strt_type) +\
            '_' + str(strt_num) + '_' + str(locationID) + '_' + str(project_code) + '_' + str(unique_ID)

        #Query the rows in Attach_table that are associated with row_1 in
        #Update_FC and name queried table 'table_view_' + the GlobalID_Static.
        arcpy.MakeTableView_management(Attach_table, "table_view_" + str(row_1[0]), where_clause = '"REL_GLOBALID" =' + "'%s'" %row_1[0])

        #Update the name of each photo in the queried Attach_table 'table_view_'+ the GlobalID_Static.
        with arcpy.da.UpdateCursor("table_view_" + str(fc_global), ['ATT_NAME','CONTENT_TYPE']) as cursor_2:
            for row_2 in cursor_2:
                file_ext = row_2[1].split('/')[1]
                photo_name = str(row_2[0].split('-')[0])
                #If previous name in dictionary, set previous name to new name
                if photo_name in photo_naming:
                    photo_name = photo_naming[photo_name]
                    #Set the old value in Attach_table to the newly derived value
                    #plus the photo name. Execute the update.
                    update_val = dir_iterator + '_' + photo_name + "." + file_ext
                    update_val = update_val.replace(" ", "")
                    row_2[0] = update_val
                    cursor_2.updateRow(row_2)
                else:
                    #Set the old value in Attach_table to the newly derived value
                    #plus the original name. Execute the update.
                    update_val = dir_iterator + '_' + photo_name + "." + file_ext
                    update_val = update_val.replace(" ", "")
                    row_2[0] = update_val
                    cursor_2.updateRow(row_2)

        #Create a directory in os with the the name 'dir_iterator'. If directory already
        #exists, change the unique_ID by adding an additional character.
        if os.path.isdir(photo_directory + dir_iterator):
            new_dir = photo_directory + dir_iterator + str(randint(0,100))
            directory = new_dir
        else:
            directory = os.mkdir(photo_directory + dir_iterator)

        #Get this directory as a value 'fileloc' to populate row_1 in Update_FC
        #as the location of the file for reference. Execute the update.
        fileloc = photo_directory + dir_iterator
        row_1[6] = fileloc
        cursor_1.updateRow(row_1)


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


#Save edits and stop the editing session of 'Update_FC'.
edit.stopOperation()
edit.stopEditing(True)

