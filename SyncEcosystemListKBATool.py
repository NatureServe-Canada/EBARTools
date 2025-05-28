# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Chloe Debyser, Meg Southee
# © NatureServe Canada 2023 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: SyncEcosystemListKBATool.py
# ArcGIS Python tool to synchronize the Ecosystem table with KBA tracking information.
# This tool populates fields in the Ecosystem table that are specific to the WCS Canada workflow to identify KBAs.

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import arcpy
import io
import csv
#import os
import EBARUtils
import datetime


class SyncEcosystemListKBATool:
    """Synchronize the Ecosystem table with WCS KBA updates"""

    def __init__(self):
        pass

    def runSyncEcosystemListKBATool(self, parameters, messages):

        # Make variables for parameters
        param_geodatabase = parameters[0].valueAsText
        param_csv = parameters[1].valueAsText

        # Open input csv data file (note: this file is from R script output)
        infile = io.open(param_csv, 'r', encoding='mbcs')  # mbcs encoding is Windows ANSI
        reader = csv.DictReader(infile)

        # # Use os library to access the folder that contains the csv file
        # root_dir = os.path.dirname(param_csv)

        # Assign variables
        line_count = 1
        processed = 0
        updated = 0
        skipped_no_id = 0
        skipped = 0
        skipped_id_list = []
        ecosystem_fields = [
            'EcosystemID', 'IVC_SCIENTIFIC_NAME_FR', 'KBA_GROUP', 'EcosystemClassificationSystem',
            'EcosystemLevelJustification', 'G_CONCEPT_SENTENCE_FR', 'ActiveEBAR', 'BIOME_NAME_FR', 'SUBBIOME_NAME_FR',
            'FORMATION_NAME_FR', 'DIVISION_NAME_FR', 'IVC_MG_NAME_FR', 'IVC_GROUP_NAME_FR',
            'IVC_FORMATTED_SCIENTIFIC_NAME_F', 'IVC_NAME_FR', 'WDKBAID', 'IUCN_CD', 'IUCN_AssessmentDate',
            'IUCN_Criteria', 'Source', 'PRECAUTIONARY_G_RANK', 'PRECAUTIONARY_N_RANK'
        ]

        # Access the dictionary of existing element_national_id and species_id values (in Biotics table)
        element_ecosystem_dict = EBARUtils.readElementEcosystem(param_geodatabase)

        # Generate list of existing EcosystemID values in the Ecosystem table
        existing_values = []
        with arcpy.da.SearchCursor(param_geodatabase + '\\Ecosystem', ['EcosystemID']) as search_cursor:
            for search_row in EBARUtils.searchCursor(search_cursor):
                existing_values.append(search_row['EcosystemID'])
        if len(existing_values) > 0:
            del search_row
        del search_cursor
        #DEBUG
        #EBARUtils.displayMessage(messages, 'Existing EcosystemID values: ' + str(existing_values))

        EBARUtils.displayMessage(messages, 'Processing input csv file...')
        for file_line in reader:
            # If the csv record has no element_national_id, skip it
            if file_line['ELEMENT_NATIONAL_ID'] == "":
                skipped_no_id += 1
            else:
                element_national_id = int(file_line['ELEMENT_NATIONAL_ID'])
                # If the csv record has element_national_id in Biotics table, process it
                if element_national_id in element_ecosystem_dict:
                    # Get the corresponding EcosystemID from the element_ecosystem_dict dictionary
                    ecosystem_id = element_ecosystem_dict.get(element_national_id)

                    # If the EcosystemID generated for the record (i.e. from Biotics) is in the Ecosystem table,
                    # then update it if changed
                    #DEBUG
                    #EBARUtils.displayMessage(messages, 'EcosystemID value: ' + str(ecosystem_id))
                    if ecosystem_id in existing_values:
                        # wrap updates to Ecosystem table to force editor tracking to work!
                        edit = arcpy.da.Editor(param_geodatabase)
                        edit.startEditing(with_undo=False, multiuser_mode=False)

                        # Access Ecosystem table with an UpdateCursor to update fields that have changed
                        changed = False
                        update_row = None
                        with arcpy.da.UpdateCursor(param_geodatabase + '\\Ecosystem', ecosystem_fields,
                                                   'EcosystemID = ' + str(ecosystem_id)) as update_cursor:

                            for update_row in EBARUtils.updateCursor(update_cursor):
                                update_values = []
                                for field in ecosystem_fields:
                                    # Insert the EcosystemID from the dictionary
                                    if field == "EcosystemID":
                                        update_values.append(ecosystem_id)
                                    elif len(file_line[field]) > 0:
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
                                    update_cursor.updateRow(update_values)
                                    updated += 1
                        if update_row:
                            del update_row
                        del update_cursor

                        # wrap updates to Ecosystem table to force editor tracking to work!
                        if changed:
                            edit.stopOperation()
                        edit.stopEditing(save_changes=True)

                    # If the EcosystemID generated for the record (i.e. from Biotics) is NOT in the Ecosystem table,
                    # then insert it
                    else:
                        # Access Ecosystem table with an InsertCursor to create new records
                        with arcpy.da.InsertCursor(param_geodatabase + '\\Ecosystem',
                                                   ecosystem_fields) as insert_cursor:
                            insert_values = []
                            for field in ecosystem_fields:
                                if field == "EcosystemID":
                                    insert_values.append(ecosystem_id)
                                elif len(file_line[field]) > 0:
                                    insert_values.append(file_line[field])
                                else:
                                    insert_values.append(None)
                            insert_cursor.insertRow(insert_values)
                        del insert_cursor

                    # Increase count for processed records
                    processed += 1

                # If the element_national_id is not in the Biotics table, skip it
                else:
                    # Append ecosystem_id value to id_list
                    skipped_id_list.append(element_national_id)
                    # Increase counter for skipped records
                    skipped += 1

            # Increase counter for the lines read in the input csv file
            line_count += 1

        # Close the input csv file
        infile.close()

        # Print tool summary and output messages
        EBARUtils.displayMessage(messages, 'Summary:')
        EBARUtils.displayMessage(messages, 'Lines read - ' + str(line_count - 1))
        EBARUtils.displayMessage(messages, 'Records processed - ' + str(processed))
        EBARUtils.displayMessage(messages, 'Records updated - ' + str(updated))
        EBARUtils.displayMessage(messages, 'Records skipped (no ELEMENT_NATIONAL_ID) - ' + str(skipped_no_id))
        EBARUtils.displayMessage(messages, 'Records skipped (no match to Biotics table) - ' + str(skipped))
        EBARUtils.displayMessage(messages, 'List of ELEMENT_NATIONAL_ID values with no match in Biotics table:')
        # Write skipped element_national_id values using a comma to separate them
        EBARUtils.displayMessage(messages, ','.join(map(str, skipped_id_list)))

        return


# # Controlling process
# if __name__ == '__main__':
#     selkba = SyncEcosystemListKBATool()

#     # Hard-coded parameters for debugging
#     param_geodatabase = arcpy.Parameter()
#     param_geodatabase.value = 'C:/GIS/EBAR/EBARDev2.gdb'
#     param_csv = arcpy.Parameter()
#     param_csv.value = 'C:/GIS/EBAR/EBARTools/samples/EcosystemKBAExample.csv'
#     parameters = [param_geodatabase, param_csv]

#     selkba.runSyncEcosystemListKBATool(parameters, None)
