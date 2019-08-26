import arcpy, os

##This tool takes an input 'update_feature' and a reference feature (here called 'parcels'), and, in space,
##selects a reference feature that spatially intersects the input feature and transfers specified values
##from the reference feature into the corresponding attribute of the update_feature.


##Paths hardcoded for testing. Use arcpy.GetParameterAsText() to implement geoprocessing tool.
parcels = r'\\Bhptfs2\PROJ\77107-07\16-GIS\Shapefiles\PITTSBURGH_PARCELS.shp'
GDB = r'\\Bhptfs2\PROJ\77107-07\16-GIS\Geodatabases\UMFR_Main_GDB.gdb'
update_feature = r'\\Bhptfs2\PROJ\77107-07\16-GIS\Geodatabases\UMFR_Main_GDB.gdb\UMFR_Merge_2019_08_14'
##Paths hardcoded for testing. Use arcpy.GetParameterAsText() to implement geoprocessing tool.

#Begin editing session on GDB.
edit = arcpy.da.Editor(GDB)
edit.startEditing(False, True)
edit.startOperation()

#Make the reference layer into a feature layer for use in spatial analysis.
parcels_layer = arcpy.MakeFeatureLayer_management(parcels, 'parcels_layer')

#Initialize UpdateCursor on update_feature to update its values called in the cursor below.
#Call 'SHAPE@' to reference the feautre in space for select by location.
with arcpy.da.UpdateCursor(update_feature, ['PIN','MapBlockLo','SHAPE@']) as cursor:
    #Iterate through each feature in update_feature
    for row in cursor:
        pin = str(row[0])
        mapblo = str(row[1])
        feature = row[2]
        #If the lenght of the pin value is > 1, its is already populated.
        #Remove if condition should the value be updated regardless of the presence of a preexisting value.
        if len(pin) > 1:
            continue
        else:
            #Select the (if any) reference feature (parcels_layer) that spatially intersects the current update_feature 'feature'.
            arcpy.SelectLayerByLocation_management(parcels_layer, 'INTERSECT', feature)
            #Initialize SearchCursor on the reference feature which is queried by the above command to obtain its values specified in cursor2 below.
            with arcpy.da.SearchCursor(parcels_layer, ['PIN', 'MAPBLOCKLO']) as cursor2:
                #There is likely only one feature in this queried version of parcels layer. Assign its values below.
                for i in cursor2:
                    pin_2 = str(i[0])
                    mapblo_2 = str(i[1])
                    #Set the values of the update_feature to the values of the queried reference feature.
                    row[0] = pin_2
                    row[1] = mapblo_2
            #Execute the update to the update_featureS
            cursor.updateRow(row)

#Stop the editing session and save edits.
edit.stopOperation()
edit.stopEditing(True)
