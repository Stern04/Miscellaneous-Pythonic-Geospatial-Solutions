import arcpy, datetime, re
arcpy.env.overwriteOutput = True
GDB = r"\\Bhptfs2\proj\77107-07\16-GIS\Geodatabases\S123_b2b1ad1b6846483fa7dd883a05d95b1c_FGDB\b0d263edda9d406bb60c0e591aae7e6a.gdb"
Update_FC = r"\\Bhptfs2\proj\77107-07\16-GIS\Geodatabases\S123_b2b1ad1b6846483fa7dd883a05d95b1c_FGDB\b0d263edda9d406bb60c0e591aae7e6a.gdb\PWSA_Unmetered_Flat_Rate"

edit = arcpy.da.Editor(GDB)
edit.startEditing(False, True)
edit.startOperation()
with arcpy.da.UpdateCursor(Update_FC, 'AcctID') as cursor:
    for row in cursor:
        rawstring = row[0]
        updatestring = ""
        if rawstring != None:
            if len(rawstring) > 7:
                x = re.findall("[0-9]", rawstring)
                for i in x:
                    updatestring += i
                row = updatestring[0:7]
            else:
                row = rawstring
            cursor.updateRow([row])

edit.stopOperation()
edit.stopEditing(True) 
            
            
        
        
        
