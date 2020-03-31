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

        # arcpy.env.workspace = param_geodatabase
        # print(arcpy.env.workspace)

        # try to open data file as a csv
        infile = io.open(param_csv, 'r', encoding='mbcs')  # mbcs encoding is Windows ANSI
        reader = csv.DictReader(infile)

        # read existing IDs into list
        EBARUtils.displayMessage(messages, 'Reading existing IDs')

        # dictionary of element_national_id and species_id
        element_species_dict = EBARUtils.readElementSpecies(param_geodatabase)

        # process input csv
        EBARUtils.displayMessage(messages, 'Processing input csv file')
        count = 0
        skipped = 0
        species_fields = ["ELEMENT_NATIONAL_ID",
                          "ELEMENT_CODE",
                          "NATIONAL_SCIENTIFIC_NAME",
                          "NATIONAL_ENGL_NAME",
                          "KBATrigger",
                          "RemainingKBAPotential",
                          "KBATrigger_G",
                          "KBATrigger_G_A1",
                          "KBATrigger_G_B1",
                          "KBATrigger_N",
                          "KBATrigger_N_A1",
                          "KBATrigger_N_B1",
                          "KBATrigger_N_PercThreshold",
                          "ECCC_PrioritySpecies",
                          "Endemic"]

        for file_line in reader:
            element_national_id = int(float(file_line['ELEMENT_NATIONAL_ID']))

            # If the record has an element_national_id that is in the biotics table, process it
            if element_national_id in element_species_dict:

                EBARUtils.displayMessage(messages, "READ ROW. ELEMENT_NATIONAL_ID = {}".format(element_national_id))

                # Generate list of existing element_national_id values in the species_kba table
                existing_values = [row[0] for row in arcpy.da.SearchCursor(param_geodatabase + "\\Species_KBA",
                                                                           "ELEMENT_NATIONAL_ID")]

                # If the record is in the species_kba table, then update it
                if element_national_id in existing_values:

                    print("UPDATE RECORD")

                    with arcpy.da.UpdateCursor(param_geodatabase + '\\SPECIES_KBA', species_fields,
                                               'ELEMENT_NATIONAL_ID = ' + str(element_national_id)) as update_cursor:
                        update_row = None
                        for update_row in EBARUtils.updateCursor(update_cursor):
                            update_values = []
                            for field in species_fields:
                                if len(file_line[field]) > 0:
                                    update_values.append(file_line[field])
                                else:
                                    update_values.append(None)
                            update_cursor.updateRow(update_values)
                        if update_row:
                            del update_row

                # If the record is in the species csv but not in the species_kba table, then insert it
                else:

                    print("INSERT RECORD")

                    with arcpy.da.InsertCursor(param_geodatabase + '\\SPECIES_KBA', species_fields,
                                               'ELEMENT_NATIONAL_ID = ' + str(element_national_id)) as insert_cursor:
                        insert_values = []
                        for field in species_fields:
                            if len(file_line[field]) > 0:
                                insert_values.append(file_line[field])
                            else:
                                insert_values.append(None)
                        insert_cursor.insertRow(insert_values)

            # If the record has no element_national_id or if the id is not in the biotics table
            else:
                # do not update and do not add new records
                EBARUtils.displayMessage(messages, "SKIP ROW. ELEMENT_NATIONAL_ID = {} not in BIOTICS table.".format(
                    element_national_id))

                # ADD CLAUSE TO OUTPUT THIS LIST OF ELEMENT_NATIONAL_IDs TO A TEXT FILE
                pass
                skipped += 1
            count += 1

        # summary and end time
        EBARUtils.displayMessage(messages, '\nSummary:')
        EBARUtils.displayMessage(messages, 'Processed - ' + str(count))
        EBARUtils.displayMessage(messages, 'Skipped - ' + str(skipped))

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
