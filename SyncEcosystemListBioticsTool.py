# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Chloe Debyser, Samantha Stefanoff
# © NatureServe Canada 2026 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: SyncEcosystemListBioticsTool.py
# ArcGIS Python tool for Synchronizing the BIOTICS_ECOSYSTEM and Ecosystem tables with Biotics

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import arcpy
import io
import csv
import EBARUtils
import datetime


class SyncEcosystemListBioticsTool:
    """Synchronize the BIOTICS_ECOSYSTEM and Ecosystem tables with Biotics"""
    def __init__(self):
        pass

    def runSyncEcosystemListBioticsTool(self, parameters, messages):
        # make variables for parms
        param_geodatabase = parameters[0].valueAsText
        param_csv = parameters[1].valueAsText

        # try to open data file as a csv
        infile = io.open(param_csv, 'r', encoding='mbcs') # mbcs encoding is Windows ANSI
        reader = csv.DictReader(infile)

        # read existing IDs and scientific names into dicts
        EBARUtils.displayMessage(messages, 'Reading existing IDs')
        element_ecosystem_dict = EBARUtils.readElementEcosystem(param_geodatabase)
        ecosystems_dict = EBARUtils.readEcosystems(param_geodatabase)

        # process all file lines
        EBARUtils.displayMessage(messages, 'Processing file lines')
        count = 0
        updated = 0
        added = 0
        skipped = 0
        # fields that are sync'd whenever changed, overwriting values on update
        regular_fields = ['ELEMENT_NATIONAL_ID',
                          'ELEMENT_GLOBAL_ID',
                          'GLOBAL_UNIQUE_IDENTIFIER',
                          'NSX_URL',
                          'IVC_ELCODE',
                          'CNVC_ELCODE',
                          'IVC_SCIENTIFIC_NAME',
                          'IVC_FORMATTED_SCIENTIFIC_NAME',
                          'IVC_TRANSLATED_NAME',
                          'IVC_NAME',
                          'CNVC_ENGLISH_NAME',
                          'CNVC_ONLY_ENGLISH_NAME',
                          'CNVC_FRENCH_NAME',
                          'IVC_STATUS',
                          'CNVC_STATUS',
                          'CA_DIST_CONFIDENCE',
                          'CA_PRESENCE',
                          'G_CLASSIFICATION_COM',
                          'N_CLASSIFICATION_COM',
                          'CLASSIFICATION_LEVEL_NAME',
                          'IVC_CONCATENATED_CD',
                          'CNVC_CONCATENATED_CD',
                          'BIOME_KEY',
                          'BIOME_NAME',
                          'SUBBIOME_KEY',
                          'SUBBIOME_NAME',
                          'FORMATION_KEY',
                          'FORMATION_NAME',
                          'DIVISION_CODE',
                          'DIVISION_KEY',
                          'DIVISION_NAME',
                          'MG_KEY',
                          'IVC_MG_NAME',
                          'CNVC_MG_ENGLISHNAME',
                          'CNVC_ONLY_MG_ENGLISHNAME',
                          'CNVC_MG_FRENCHNAME',
                          'SUBMACROGROUP_CODE',
                          'G_RANK',
                          'ROUNDED_G_RANK',
                          'G_RANK_REVIEW_DATE',
                          'N_RANK',
                          'ROUNDED_N_RANK',
                          'N_RANK_REVIEW_DATE',
                          'NATIONS',
                          'CA_SUBNATIONS',
                          'US_STATES',
                          'N_CONCEPT_DATE',
                          'N_CONCEPT_AUTHOR',
                          'G_CONCEPT_REFERENCE',
                          'G_CONCEPT_SENTENCE',
                          'G_ELEMENT_SUMMARY',
                          'N_ELEMENT_SUMMARY',
                          'SORT',
                          'IVC_GROUP_KEY',
                          'CNVC_GROUP_KEY',
                          'IVC_GROUP_NAME',
                          'CNVC_GROUP_ENGLISHNAME',
                          'CNVC_ONLY_GROUP_ENGLISHNAME',
                          'CNVC_GROUP_FRENCHNAME']
        for file_line in reader:
            # element_global_id = int(float(file_line['ELEMENT_GLOBAL_ID']))
            # EBARUtils.displayMessage(messages, 'ELEMENT_GLOBAL_ID: ' + str(element_global_id))
            # if element_global_id in element_ecosystem_dict:
            element_national_id = int(float(file_line['ELEMENT_NATIONAL_ID']))
            EBARUtils.displayMessage(messages, 'ELEMENT_NATIONAL_ID: ' + str(element_national_id))
            if element_national_id in element_ecosystem_dict:
                # update if changed
                changed = False
                # with arcpy.da.UpdateCursor(param_geodatabase + '/BIOTICS_ECOSYSTEM', regular_fields,
                #                            'ELEMENT_GLOBAL_ID = ' + str(element_global_id)) as update_cursor:
                with arcpy.da.UpdateCursor(param_geodatabase + '/BIOTICS_ECOSYSTEM', regular_fields,
                                           'ELEMENT_NATIONAL_ID = ' + str(element_national_id)) as update_cursor:
                    update_row = None
                    for update_row in EBARUtils.updateCursor(update_cursor):
                        update_values = []
                        for field in regular_fields:
                            if len(file_line[field]) > 0:
                                # import value
                                update_values.append(file_line[field])
                                # all file_line fields are read as string, so convert as necessary
                                strval = file_line[field]
                                val = strval
                                if type(update_row[field]) is int:
                                    val = int(float(file_line[field]))
                                elif type(update_row[field]) is float:
                                    val = float(file_line[field])
                                elif type(update_row[field]) is datetime.datetime:
                                    val = datetime.datetime.strptime(file_line[field], '%Y-%m-%d')
                                if val != update_row[field]:
                                    changed = True
                            else:
                                # import NULL
                                update_values.append(None)
                                if update_row[field]:
                                    changed = True
                        if changed:
                            updated += 1
                            update_cursor.updateRow(update_values)
                    if update_row:
                        del update_row
            else:
                # create new Ecosystem and BIOTICS_ECOSYSTEM records
                # first check for existing scientific name
                if file_line['IVC_SCIENTIFIC_NAME'].lower() in ecosystems_dict:
                    #msg = 'WARNING: record with ELEMENT_GLOBAL_ID ' + str(element_global_id) + \
                    msg = 'WARNING: record with ELEMENT_NATIONAL_ID ' + str(element_national_id) + \
                        ' skipped because it would create duplicate IVC_SCIENTIFIC_NAME ' + \
                        file_line['IVC_SCIENTIFIC_NAME']
                    EBARUtils.displayMessage(messages, msg)
                    skipped += 1
                else:
                    with arcpy.da.InsertCursor(param_geodatabase + '/Ecosystem',
                                               ['ActiveEBAR']) as insert_cursor:
                        object_id = insert_cursor.insertRow([1])
                    ecosystem_id = EBARUtils.getUniqueID(param_geodatabase + '/Ecosystem', 'EcosystemID', object_id)
                    regular_fields.append('EcosystemID')
                    with arcpy.da.InsertCursor(param_geodatabase + '/BIOTICS_Ecosystem',
                                               regular_fields) as insert_cursor:
                        insert_values = []
                        for field in regular_fields:
                            if field == 'EcosystemID':
                                insert_values.append(ecosystem_id)
                            elif len(file_line[field]) > 0:
                                insert_values.append(file_line[field])
                            else:
                                insert_values.append(None)
                        insert_cursor.insertRow(insert_values)
                    regular_fields.remove('EcosystemID')
                    added += 1
            count += 1

        # # calculate NSX_URL
        # arcpy.CalculateField_management(param_geodatabase + '/BIOTICS_ECOSYSTEM', 'NSX_URL',
        #                                 "'https://explorer.natureserve.org/Taxon/' + !GLOBAL_UNIQUE_IDENTIFIER!")
        # summary and end time
        EBARUtils.displayMessage(messages, 'Summary:')
        EBARUtils.displayMessage(messages, 'Processed - ' + str(count))
        EBARUtils.displayMessage(messages, 'Updated - ' + str(updated))
        EBARUtils.displayMessage(messages, 'Added - ' + str(added))
        EBARUtils.displayMessage(messages, 'Skipped - ' + str(skipped))

        infile.close()
        return


# # controlling process
# if __name__ == '__main__':
#     sel = SyncEcosystemListBioticsTool()
#     # hard code parameters for debugging
#     param_geodatabase = arcpy.Parameter()
#     param_geodatabase.value = 'C:/GIS/EBAR/EBARDev2.gdb'
#     param_csv = arcpy.Parameter()
#     param_csv.value = 'C:/Users/rgree/OneDrive/Customers/WCSC/Pipeline/Ecosystems/Alliances.csv'
#     parameters = [param_geodatabase, param_csv]
#     sel.runSyncEcosystemListBioticsTool(parameters, None)
