# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: SyncSpeciesListTool.py
# ArcGIS Python tool for Synchronizing the BIOTIOCS_NATIONAL_ELMENT and Species tables with Biotics

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import arcpy
import io
import csv
import EBARUtils


class SyncSpeciesListTool:
    """Synchronize the BIOTIOCS_NATIONAL_ELMENT and Species tables with Biotics"""
    def __init__(self):
        pass

    def RunSyncSpeciesListTool(self, parameters, messages):
        # make variables for parms
        param_geodatabase = parameters[0].valueAsText
        param_csv = parameters[1].valueAsText

        # try to open data file as a csv
        infile = io.open(param_csv, 'r', encoding='mbcs') # mbcs encoding is Windows ANSI
        reader = csv.DictReader(infile)

        # read existing IDs into list
        IDs = []
        EBARUtils.displayMessage(messages, 'Reading existing IDs')
        with arcpy.da.SearchCursor(param_geodatabase + '/BIOTICS_ELEMENT_NATIONAL', ['ELEMENT_NATIONAL_ID']) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                IDs.append(['ELEMENT_NATIONAL_ID'])
            del row

        # process all file lines
        EBARUtils.displayMessage(messages, 'Processing file lines')
        count = 0
        added = 0
        for file_line in reader:
            if file_line['ELEMENT_NATIONAL_ID'] in IDs:
                # update
                with arcpy.da.UpdateCursor(param_geodatabase + '/BIOTICS_ELEMENT_NATIONAL',
                                           ['ELEMENT_NATIONAL_ID',
                                            'ELEMENT_CODE',
                                            'CLASSIFICATION_STATUS',
                                            'CATEGORY',
                                            'TAX_GROUP',
                                            'FAMILY_COM',
                                            'GENUS',
                                            'CA_NNAME_LEVEL',
                                            'NATIONAL_SCIENTIFIC_NAME']) as update_cursor:
                    for row in EBARUtils.updateCursor(update_cursor):
                        pass
            else:
                pass
                # create new Species and BIOTICS_ELEMENT_NATIONAL_RECORDS
            added += 1

            count += 1

        # summary and end time
        EBARUtils.displayMessage(messages, 'Summary:')
        EBARUtils.displayMessage(messages, 'Processed - ' + str(count))
        EBARUtils.displayMessage(messages, 'Added - ' + str(added))

        infile.close()
        return


# controlling process
if __name__ == '__main__':
    ssl = SyncSpeciesListTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value='C:/GIS/EBAR/EBAR_test.gdb'
    param_csv = arcpy.Parameter()
    param_csv.value='C:/Users/rgree/OneDrive/EBAR/Data Mining/Species Prioritization/BioticsSpeciesExample2.csv'
    parameters = [param_geodatabase, param_csv]
    ssl.RunSyncSpeciesListTool(parameters, None)
