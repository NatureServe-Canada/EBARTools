# encoding: utf-8

# Project: Key Biodiversity Areas (KBA) Canada
# Credits: Meg Southee, Randal Greene
# © WCS Canada / NatureServe Canada 2020 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: SyncSpeciesListKBATool.py
# ArcGIS Python tool to synchronize the Species table with the Biotics table in the EBAR-KBA database.
# This tool populates fields in the Species table that are specific to the WCS Canada workflow to identify KBAs.

# Notes:
# Normally called from EBAR Tools.pyt, unless doing interactive debugging
# (see controlling process at the end of this file)


# Import Python packages
import arcpy
import io
import csv
import os
import EBARUtils


class SyncSpeciesListKBATool:
    """Synchronize the Species table with WCS KBA trigger species updates"""

    def __init__(self):
        pass

    def runSyncSpeciesListKBATool(self, parameters, messages):

        # Make variables for parameters
        param_geodatabase = parameters[0].valueAsText
        param_csv = parameters[1].valueAsText

        # Open input csv data file (note: this file is from R script output)
        infile = io.open(param_csv, 'r', encoding='mbcs')  # mbcs encoding is Windows ANSI
        reader = csv.DictReader(infile)

        # Use os library to access the folder that contains the csv file
        root_dir = os.path.dirname(param_csv)

        # Assign variables
        line_count = 1
        processed = 0
        skipped_no_id = 0
        skipped = 0
        skipped_id_list = []
        species_fields = ["SpeciesID",
                          "KBATrigger",
                          "KBATrigger_G",
                          "KBATrigger_G_A1",
                          "KBATrigger_G_B1",
                          "KBATrigger_G_B2",
                          "KBATrigger_G_B3",
                          "KBATrigger_G_PercThreshold",
                          "MinKBASize_G",
                          "KBATrigger_N",
                          "KBATrigger_N_A1",
                          "KBATrigger_N_B1",
                          "KBATrigger_N_PercThreshold",
                          "MinKBASize_N",
                          "KBATrigger_Applicability",
                          "EBAR_Mapping",
                          "ECCC_PrioritySpecies",
                          "B1_GeoRestrict_G_ExpertInput",
                          "B1_GeoRestrict_N_ExpertInput",
                          "B1_GeoRestrict_ExpertName",
                          "B_TaxonomicGroup",
                          "B2_RestrictedRange",
                          "B2_NSpeciesNeeded",
                          "B2_Sources",
                          "B3_Subcriterion",
                          "B3_RegionRestricted",
                          "B3_Region",
                          "B3_NSpeciesNeeded",
                          "B3_Sources",
                          "GlobalName_Level",
                          "FullSpecies_ElementCode",
                          "IUCN_InternalTaxonId",
                          "IUCN_AssessmentId",
                          "COSEWIC_Report",
                          "IUCN_CD",
                          "IUCN_AssessmentDate",
                          "IUCN_Criteria",
                          "IUCN_CriteriaVersion",
                          "IUCN_Systems",
                          "IUCN_PossiblyExtinct",
                          "IUCN_PopulationTrend",
                          "IUCN_PresenceCA",
                          "IUCN_OriginCA",
                          "IUCN_SeasonalityCA",
                          "IUCN_AOORange",
                          "IUCN_EOORange",
                          "IUCN_Congregatory",
                          "IUCN_PopulationSize",
                          "IUCN_LocationsNumber",
                          "IUCN_MovementPatterns",
                          "IUCN_AreaRestricted",
                          "IUCN_YearOfPopulationEstimate",
                          "PRECAUTIONARY_G_RANK",
                          "PRECAUTIONARY_N_RANK",
                          "PRECAUTIONARY_N_RANK_Breeding",
                          "PRECAUTIONARY_N_RANK_NonBreed",
                          "PRECAUTIONARY_N_RANK_Migrant",
                          "BeyondNAmerica",
                          "BeyondUSCanada",
                          "AOO_N_COSEWIC",
                          "Range_G_IUCN",
                          "Range_N_IUCN",
                          "Range_N_ECCC",
                          "PercentRangeCanada",
                          "Source_NSCGlobalList",
                          "Source_NSCNationalList",
                          "Source_NSCOtherTaxa",
                          "Source_NSCEndemics",
                          "Source_IUCNSimpleSummary",
                          "Source_Other",
                          "NSC_Comments",
                          "PotentialKBAs",
                          "WDKBAID",
                          "KBAPotential",
                          "KBAPotential_Rationale",
                          "EBAR_G_MapID",
                          "EBAR_NA_MapID",
                          "EBAR_N_MapID",
                          "EBAR_MapID_GlobalAssessments",
                          "EBAR_MapID_NationalAssessment",
                          "Endemism",
                          "IUCN_Name",
                          "Range_G_IUCN_Breeding",
                          "Range_G_IUCN_NonBreeding",
                          "Range_N_IUCN_Breeding",
                          "Range_N_IUCN_NonBreeding",
                          "Range_G_EBAR",
                          "Range_N_EBAR",
                          "IsPotentialTrigger"
                          ]

        # Access the dictionary of existing element_national_id and species_id values (in Biotics table)
        element_species_dict = EBARUtils.readElementSpecies(param_geodatabase)

        EBARUtils.displayMessage(messages, 'Processing input csv file...')

        for file_line in reader:

            # If the csv record has no element_national_id, skip it
            if file_line['ELEMENT_NATIONAL_ID'] is "":
                skipped_no_id += 1

                # # Verbose messages for debugging
                # EBARUtils.displayMessage(messages, "READ ROW {}. NO ELEMENT_NATIONAL_ID.".format(count))

            else:
                element_national_id = int(file_line['ELEMENT_NATIONAL_ID'])

                # If the csv record has element_national_id in Biotics table, process it
                if element_national_id in element_species_dict:

                    # Get the corresponding SpeciesID from the element_species_dict dictionary
                    species_id = element_species_dict.get(element_national_id)

                    # # Verbose messages for debugging
                    # EBARUtils.displayMessage(messages,
                    #                          "READ ROW {}. ELEMENT_NATIONAL_ID = {}. SPECIES_ID = {}".format(line_count,
                    #                                                                                          element_national_id,
                    #                                                                                          species_id))

                    # Generate list of existing SpeciesID values in the Species table
                    existing_values = [row[0] for row in arcpy.da.SearchCursor(param_geodatabase + '\\Species',
                                                                               "SpeciesID")]

                    # If the SpeciesID generated for the record (i.e. from Biotics) is in the Species table,
                    # then update it
                    if species_id in existing_values:

                        # # Message for debugging
                        # print("UPDATE RECORD")

                        # Access Species table with an UpdateCursor to update fields that have changed
                        with arcpy.da.UpdateCursor(param_geodatabase + '\\Species', species_fields,
                                                   'SpeciesID = ' + str(
                                                       species_id)) as update_cursor:

                            update_row = None
                            for update_row in EBARUtils.updateCursor(update_cursor):
                                update_values = []

                                for field in species_fields:

                                    # Insert the SpeciesID from the dictionary
                                    if field == "SpeciesID":
                                        update_values.append(species_id)

                                    elif len(file_line[field]) > 0:
                                        update_values.append(file_line[field])

                                    else:
                                        update_values.append(None)

                                update_cursor.updateRow(update_values)

                            if update_row:
                                del update_row

                    # If the SpeciesID generated for the record (i.e. from Biotics) is NOT in the Species table,
                    # then insert it
                    else:

                        # # Message for debugging
                        # print("INSERT RECORD")

                        # Access Species table with an InsertCursor to create new records
                        with arcpy.da.InsertCursor(param_geodatabase + '\\Species',
                                                   species_fields) as insert_cursor:
                            insert_values = []

                            for field in species_fields:
                                if field == "SpeciesID":
                                    insert_values.append(species_id)

                                elif len(file_line[field]) > 0:
                                    insert_values.append(file_line[field])

                                else:
                                    insert_values.append(None)

                            insert_cursor.insertRow(insert_values)

                    # Increase count for processed records
                    processed += 1

                # If the element_national_id is not in the Biotics table, skip it
                else:

                    # # Verbose message for debugging
                    # EBARUtils.displayMessage(messages,
                    #                          "SKIP ROW {}. ELEMENT_NATIONAL_ID = {} not in BIOTICS table.".format(line_count,
                    #                                                                                               element_national_id))

                    # Append element_national id value to id_list
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
        EBARUtils.displayMessage(messages, 'Records skipped (no Element_National_ID) - ' + str(skipped_no_id))
        EBARUtils.displayMessage(messages, 'Records skipped (no match to Biotics table) - ' + str(skipped))
        EBARUtils.displayMessage(messages, 'List of Element_National_ID values with no match in Biotics table:')
        # Write skipped element_national_id values using a comma to separate them
        EBARUtils.displayMessage(messages, ','.join(map(str, skipped_id_list)))

        return


# Controlling process
if __name__ == '__main__':
    sslkba = SyncSpeciesListKBATool()

    # Hard-coded parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:\\GIS_Processing\\KBA\\Scripts\\EBAR_GITHUB\\EBARDev.gdb'
    param_csv = arcpy.Parameter()
    param_csv.value = 'C:\\GIS_Processing\\KBA\\Scripts\\EBAR_GITHUB\\EBARTools\\SpeciesElementsExample.csv'
    parameters = [param_geodatabase, param_csv]

    sslkba.runSyncSpeciesListKBATool(parameters, None)
