# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR) & Key Biodiversity Areas (KBA)
# Credits: Randal Greene, Christine Terwissen, Meg Southee
# © NatureServe Canada 2020 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: SyncSpeciesListKBATool.py
# ArcGIS Python tool to synchronize the Species tables with WCS KBA updates

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import arcpy
import io
import csv
import EBARUtils


class SyncSpeciesListKBA:
    """Synchronize the Species tables with WCS KBA updates"""
    def __init__(self):
        pass

    def RunSyncSpeciesListKBATool(self, parameters, messages):
        # make variables for parms
        param_geodatabase = parameters[0].valueAsText
        param_csv = parameters[1].valueAsText

        # try to open data file as a csv
        infile = io.open(param_csv, 'r', encoding='mbcs')  # mbcs encoding is Windows ANSI
        reader = csv.DictReader(infile)

        # read existing IDs into list
        EBARUtils.displayMessage(messages, 'Reading existing IDs')

        # FIGURE OUT WHAT IS GOING ON WITH THIS DICTIONARY AND IF IT IS NECESSARY
        element_species_dict = EBARUtils.readElementSpecies(param_geodatabase)

        # process all file lines
        EBARUtils.displayMessage(messages, 'Processing file lines')
        count = 0
        skipped = 0

        for file_line in reader:
            element_national_id = int(float(file_line['ELEMENT_NATIONAL_ID']))

            # NOTE: LOOKS FOR ELEMENT_NATIONAL_ID IN DICTIONARY THAT CONTAINS SPECIES_ID AS WELL
            if element_national_id in element_species_dict:

                # update records using an update cursor


                EBARUtils.displayMessage(messages, "READING ROW.  ELEMENT_NATIONAL_ID = {}".format(element_national_id))

            else:
                # do not update and do not add new records

                EBARUtils.displayMessage(messages, "ELEMENT_NATIONAL_ID does not exist.")

                # ADD CLAUSE TO OUTPUT THIS LIST OF ELEMENT_NATIONAL_IDs TO A TEXT FILE

                pass
                skipped += 1
            count += 1

        # summary and end time
        EBARUtils.displayMessage(messages, 'Summary:')
        EBARUtils.displayMessage(messages, 'Processed - ' + str(count))
        EBARUtils.displayMessage(messages, 'Added - ' + str(skipped))

        infile.close()
        return

# controlling process
if __name__ == '__main__':
    sslkba = SyncSpeciesListKBA()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:\\GIS_Processing\\KBA\\Scripts\\GITHUB\\EBARDev.gdb'
    param_csv = arcpy.Parameter()
    param_csv.value = 'C:\\GIS_Processing\\KBA\\Scripts\\GITHUB\\WCS_Species_test.csv'
    parameters = [param_geodatabase, param_csv]
    sslkba.RunSyncSpeciesListKBATool(parameters, None)


