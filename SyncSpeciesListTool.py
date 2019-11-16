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
                IDs.append(row['ELEMENT_NATIONAL_ID'])
            del row

        # process all file lines
        EBARUtils.displayMessage(messages, 'Processing file lines')
        count = 0
        added = 0
        biotics_fields = ['ELEMENT_GLOBAL_ID',
                          'ELEMENT_NATIONAL_ID',
                          'ELEMENT_CODE',
                          'CLASSIFICATION_STATUS',
                          'CATEGORY',
                          'TAX_GROUP',
                          'FAMILY_COM',
                          'GENUS',
                          'CA_NNAME_LEVEL',
                          'NATIONAL_SCIENTIFIC_NAME',
                          'NATIONAL_ENGL_NAME',
                          'NATIONAL_FR_NAME',
                          'G_RANK',
                          'ROUNDED_G_RANK',
                          'G_RANK_REVIEW_DATE',
                          'N_RANK',
                          'ROUNDED_N_RANK',
                          'N_RANK_REVIEW_DATE',
                          'BCD_STYLE_N_RANK',
                          'SARA_STATUS',
                          'COSEWIC_ID',
                          'COSEWIC_STATUS',
                          'INTERP_COSEWIC',
                          'COSEWIC_SUMMARY',
                          'COSEWIC_NAME',
                          'ENGLISH_COSEWIC_COM_NAME',
                          'FRENCH_COSEWIC_COM_NAME',
                          'IUCN_CD',
                          'CA_ORIGIN',
                          'CA_REGULARITY',
                          'CA_CONFIDENCE',
                          'CA_PRESENCE',
                          'CA_POPULATION']
        for file_line in reader:
            element_national_id = int(float(file_line['ELEMENT_NATIONAL_ID']))
            if element_national_id in IDs:
                # update
                with arcpy.da.UpdateCursor(param_geodatabase + '/BIOTICS_ELEMENT_NATIONAL', biotics_fields,
                                           'ELEMENT_NATIONAL_ID = ' + str(element_national_id)) as update_cursor:
                    for update_row in EBARUtils.updateCursor(update_cursor):
                        update_fields = []
                        for field in biotics_fields:
                            if len(file_line[field]) > 0:
                                update_fields.append(file_line[field])
                            else:
                                update_fields.append(None)
                        update_cursor.updateRow(update_fields)
                    del update_row
            else:
                # create new BIOTICS_ELEMENT_NATIONAL and Species records
                with arcpy.da.InsertCursor(param_geodatabase + '/BIOTICS_ELEMENT_NATIONAL',
                                           biotics_fields) as insert_cursor:
                    insert_fields = []
                    for field in biotics_fields:
                        if len(file_line[field]) > 0:
                            insert_fields.append(file_line[field])
                        else:
                            insert_fields.append(None)
                    insert_cursor.insertRow(insert_fields)
                with arcpy.da.InsertCursor(param_geodatabase + '/Species',
                                           ['ELEMENT_NATIONAL_ID']) as insert_cursor:
                    insert_cursor.insertRow([element_national_id])
                EBARUtils.setNewID(param_geodatabase + '/Species', 'SpeciesID',
                                   'ELEMENT_NATIONAL_ID = ' + str(element_national_id))
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
    param_csv.value='C:/Users/rgree/OneDrive/EBAR/Data Mining/Species Prioritization/BioticsSpeciesExample3.csv'
    parameters = [param_geodatabase, param_csv]
    ssl.RunSyncSpeciesListTool(parameters, None)
