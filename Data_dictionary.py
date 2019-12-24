import pandas as pd
import arcpy
import openpyxl

#Create path for feature class to pull fields from and output path to store and name dictionary.
fc = r'\\Bhptfs2\proj\77107-07\16-GIS\Geodatabases\Master_UMFR_GDB\Master_UMFR_Survey_GDB.gdb\Proj_Master_PWSA_Unmetered_Flat_Rate_2019_12_16'
output_excel = r'J:\PROJ\77107-07\16-GIS\Excel\UMFR_Data_Dictionary.xlsx'

#Get fields as 'Field' objects from fc
fields = arcpy.ListFields(fc)

#Initialize list to hold entries to be added into df
entries = []

#Loop through fields making a list to be used as each row in df
for field in fields:
    add_entry = [field.name.encode("utf-8"), field.aliasName.encode("utf-8"),
                 str(field.type.encode("utf-8")), field.precision, ""]
    #Add the list (row) to the main list of lists (rows)
    entries.append(add_entry)

#Create column names for df
col_names = ['Name', 'Alias', 'Type', 'Precision', 'Description']

#Create an index for df
inx = pd.Index([i for i in range(1,len(entries)+1)], name = 'Field')

#Create the df
UMFR_fields_df = pd.DataFrame(data=entries, columns = col_names, index = inx)

#Write to Excel file. Warning: this currently overwrites existing files with the same name.
UMFR_fields_df.to_excel(output_excel)
