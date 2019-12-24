import os, re

photo_directory = r"\\Bhptfs2\proj\77107-07\16-GIS\Images\Survey_photos_good\\"

photo_naming = {'Loc_of_Existing_Watermain': 'Watermain', 'Loc_of_Existing_Watermain_2': 'Entrance', 'Existing_Curb_Stop': 'Curb_Stop', 'Existing_Curb_Stop_2': 'Curb_Stop2',
'ServiceLineEntryiIntoBuilding': 'SL_Entry','ServiceLineEntryIntoBuilding': 'SL_Entry', 'ServiceLineEntryiIntoBuilding_2': 'SL_Entry2','ServiceLineEntryIntoBuilding_2': 'SL_Entry2',
'ServiceLineExit': 'SL_Exit', 'ServiceLineExit_2': 'SL_Exit2', 'ServiceLineAccessAndPlumbing': 'SL_Access','ServiceLineAccessAndPlumbing_2': 'SL_Access2',
'ServiceLineAccessAndPlumbing2': 'SL_Access2', 'PotentialNewSLEntry': 'New_SL_Entry', 'ThermalExpansionTank': 'TET', 'ThermalExpansionTank_2': 'TET2', 'BackflowPreventer': 'Backflow',
'BackflowPreventer_2': 'Backflow2'}

#For sorting out old photos. No longer needed moving forward.
new_photo_names = []
for i in photo_naming.iteritems():
    new_photo_names.append(i[1])

#Get list of all directories (surveys) in photo_directory
dirs = os.listdir(photo_directory)

error_log = []
possible_manual_fixes = []

for upper_dir in dirs:
    #List out each photo in the given directory
    x = os.listdir(photo_directory+upper_dir)
    #print("x below")
    #print(x)

    #If there is >0 photos
    if x:
        #for each photo
        for photo_name in x:
            #Get rid of date and time at end of each file name.
            origin_photo_name = photo_name
            #print("origin path full: " + str(origin_photo_name))
            photo_name = photo_name.strip()
            #print("photo name before: " + photo_name)
            if len(photo_name.split('-')) > 1:
                photo_name = photo_name.split('-')[0] + ".jpg"
            #print("photo name after: " + photo_name)

            #Regex to split out the photo name into parts to keep and parts to change
            for item in re.finditer('(?P<keep>[\w ]+UMFR_\d+_)(?P<change>[\w]+)', photo_name):
                keep = item.groupdict()['keep']
                change = item.groupdict()['change']

                #If the category name is old and needs to be updated with the corresponding
                #value in photo_naming dict, add this new value from photo_naming[change]
                if change in photo_naming:
                    fixA = keep + photo_naming[change]+".jpg"
                    fixA = fixA.replace(" ", "")
                    #print("FixA " + os.path.join(photo_directory,upper_dir,origin_photo_name))
                    #print("FixA " + os.path.join(photo_directory,upper_dir,fixA))
                    try:
                        os.rename(os.path.join(photo_directory,upper_dir,origin_photo_name),os.path.join(photo_directory,upper_dir,fixA))
                        #print("FixA executed")
                    except Exception as e:
                        #print(str(e) + ": " + os.path.join(photo_directory,upper_dir,origin_photo_name))
                        error_log.append(str(e) + ": " + os.path.join(photo_directory,upper_dir,origin_photo_name))


                #Category does not need changed, leave as is
                else:
                    fixB = keep + change + ".jpg"
                    fixB = fixB.replace(" ", "")
                    if change not in new_photo_names and change not in photo_naming and "Pic" not in change:
                        possible_manual_fixes.append(os.path.join(photo_directory,upper_dir,fixB))
                    #print("FixB " + os.path.join(photo_directory,upper_dir,origin_photo_name))
                    #print("FixB " + os.path.join(photo_directory,upper_dir+fixB))
                    try:
                        os.rename(os.path.join(photo_directory,upper_dir,origin_photo_name),os.path.join(photo_directory,upper_dir,fixB))
                        #print("FixB executed")
                    except Exception as e:
                        #print(str(e) + ": " + os.path.join(photo_directory,upper_dir,origin_photo_name))
                        error_log.append(str(e) + ": " + os.path.join(photo_directory,upper_dir,origin_photo_name))



    #Survey physical location directory (i.e. general photo directory + name of location...one level above individual photos)
    survey_dir_original = photo_directory + upper_dir
    survey_dir = survey_dir_original.replace(" ", "")

    os.rename(survey_dir_original, survey_dir)

print("error log:")
for i in error_log:
    print(i)
print("possible_manual_fixes: " + str(len(possible_manual_fixes)))
for i in possible_manual_fixes:
    print(i)
