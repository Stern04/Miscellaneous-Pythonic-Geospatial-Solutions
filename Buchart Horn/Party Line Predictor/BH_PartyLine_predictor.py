import arcpy
from timeit import default_timer as timer

start_time = timer()

workspace = r'\\Bhptfs2\proj\77322-00\16-GIS\Shapefiles\2020_A_Contract_Sternberger_Working'
raw_service_lines = r'\\Bhptfs2\proj\77322-00\16-GIS\Shapefiles\2020_A_Contract_Sternberger_Working\ServiceLine_sample.shp'
raw_entities = r'\\Bhptfs2\proj\77322-00\16-GIS\Geodatabases\From_PWSA\2020_SDWMR_Contract_A_WSL_Material\2020_SDWMR_Contract_A_WSL_Material.shp'
raw_dissolved_service_lines = r'\\Bhptfs2\proj\77322-00\16-GIS\Shapefiles\2020_A_Contract_Sternberger_Working\SL_Sample_Dissolve.shp'

service_lines = arcpy.MakeFeatureLayer_management(raw_service_lines, 'service_lines')
entities = arcpy.MakeFeatureLayer_management(raw_entities, 'entities')
dissolved_service_lines = arcpy.MakeFeatureLayer_management(raw_dissolved_service_lines, 'dissolved_service_lines')

edit = arcpy.da.Editor(workspace)
edit.startEditing(False, True)
edit.startOperation()

group_IDs = [0]

with arcpy.da.UpdateCursor(service_lines,['FID','Group_ID']) as cursor:
    for row in cursor:
        FID = row[0]
        Group_ID = row[1]

        if Group_ID not in group_IDs:
            base_count = 0
            current_count = 0

            print('initial selection', FID)
            # arcpy.SelectLayerByAttribute_management(service_lines, where_clause = 'FID =' + "'%s'" %str(FID))
            arcpy.SelectLayerByAttribute_management(service_lines, where_clause = 'FID =' + str(FID))
            base_count = int(arcpy.GetCount_management(service_lines).getOutput(0))

            while True:
                print('in while loop')

                create_group_ID = group_IDs[-1] + 1

                subsequent_service_lines = arcpy.SelectLayerByLocation_management(in_layer = service_lines, selection_type = "ADD_TO_SELECTION", \
                                                        overlap_type = 'INTERSECT', select_features = service_lines)
                current_count = int(arcpy.GetCount_management(service_lines).getOutput(0))
                print('base', base_count)
                print('current', current_count)

                if current_count > base_count:
                    base_count = current_count
                    print(base_count, 'updated base count')
                else:
                    with arcpy.da.UpdateCursor(subsequent_service_lines,['Group_ID']) as cursor2:
                        for row2 in cursor2:
                            row2[0] = create_group_ID
                            group_IDs.append(create_group_ID)
                            print('new group id', group_IDs[-1])
                            cursor2.updateRow(row2)
                    print('cursor updated. breaking while loop.')
                    break

with arcpy.da.UpdateCursor(dissolved_service_lines,['FID','Party_Line']) as cursor:
    for row in cursor:
        FID = row[0]

        arcpy.SelectLayerByAttribute_management(dissolved_service_lines, where_clause = 'FID =' + str(FID))

        intersecting_entities = arcpy.SelectLayerByLocation_management(in_layer = entities, \
                                                                overlap_type = 'INTERSECT', select_features = dissolved_service_lines)

        entity_count = int(arcpy.GetCount_management(intersecting_entities).getOutput(0))
        # print("FID: ", str(FID))
        # print('Count: ', str(entity_count))

        if entity_count > 1:
            with arcpy.da.UpdateCursor(entities,['Party_Line']) as cursor2:
                for row2 in cursor2:
                    row2[0] = 'Yes'
                    cursor2.updateRow(row2)

            row[1] = 'Yes'
            cursor.updateRow(row)








edit.stopOperation()
edit.stopEditing(True)

end_time = timer()
print('elapsed time: ', str(end_time-start_time))
