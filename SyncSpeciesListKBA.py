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
        count = 1
        skipped = 0
        species_fields = ["ELEMENT_NATIONAL_ID",
                          "KBATrigger",
                          "RemainingKBAPotential",
                          "KBATrigger_G",
                          "KBATrigger_G_A1",
                          "KBATrigger_G_B1",
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
                          "COSEWIC_Date",
                          "COSEWIC_Criteria",
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
                          "G_RANK_PopReduction",
                          "PRECAUTIONARY_N_RANK",
                          "PRECAUTIONARY_N_RANK_Breeding",
                          "PRECAUTIONARY_N_RANK_NonBreeding",
                          "PRECAUTIONARY_N_RANK_Migrant",
                          "N_RANK_PopReduction",
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
                          "PotentialKBAs",
                          "SpeciesID"
                          ]

        for file_line in reader:

            # Skip any rows that don't have an ELEMENT_NATIONAL_ID
            if file_line['ELEMENT_NATIONAL_ID'] is "":
                skipped += 1
                pass

            else:
                element_national_id = int(file_line['ELEMENT_NATIONAL_ID'])

                # If the record has an element_national_id that is in the biotics table, process it
                if element_national_id in element_species_dict:

                    # Get the corresponding SpeciesID from the element_species dictionary
                    species_id = element_species_dict.get(element_national_id)

                    EBARUtils.displayMessage(messages,
                                             "READ ROW {}. ELEMENT_NATIONAL_ID = {}. SPECIES_ID = {}".format(count,
                                                                                                             element_national_id,
                                                                                                             species_id))

                    # Generate list of existing element_national_id values in the species_kba table
                    existing_values = [row[0] for row in arcpy.da.SearchCursor(param_geodatabase + "\\SpeciesKBA",
                                                                               "ELEMENT_NATIONAL_ID")]

                    # If the record is in the species_kba table, then update it
                    if element_national_id in existing_values:

                        # print("UPDATE RECORD")

                        with arcpy.da.UpdateCursor(param_geodatabase + '\\SpeciesKBA', species_fields,
                                                   'ELEMENT_NATIONAL_ID = ' + str(
                                                       element_national_id)) as update_cursor:
                            update_row = None
                            for update_row in EBARUtils.updateCursor(update_cursor):
                                update_values = []

                                for field in species_fields:

                                    # special case to insert the species id from the dictionary, because this field is
                                    # not in the input CSV
                                    if field == "SpeciesID":
                                        update_values.append(species_id)

                                    elif len(file_line[field]) > 0:
                                        update_values.append(file_line[field])

                                    else:
                                        update_values.append(None)

                                update_cursor.updateRow(update_values)

                            if update_row:
                                del update_row

                        # If the record is in the species csv but not in the species_kba table, then insert it
                    else:

                        print("INSERT RECORD")

                        with arcpy.da.InsertCursor(param_geodatabase + '\\SpeciesKBA',
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


                #     ### TRYING TO WORK DIRECTLY WITH SPECIES ID
                #     # Get the corresponding SPECIES ID from the element_species dictionary
                #     species_id = element_species_dict.get(element_national_id)
                #
                #     # Generate list of existing element_national_id values in the species_kba table
                #     # NOTE need to use SPECIESID because ELEMENT_NATIONAL_ID is not in the species_kba table
                #     existing_values = [row[0] for row in arcpy.da.SearchCursor(param_geodatabase + "\\Species_KBA",
                #                                                                "SPECIESID")]
                #
                #     # If the record is in the species_kba table, then update it
                #     if species_id in existing_values:
                #
                #         print("UPDATE RECORD")
                #
                #         with arcpy.da.UpdateCursor(param_geodatabase + '\\SpeciesKBA', species_fields,
                #                                    'SPECIESID = ' + str(species_id)) as update_cursor:
                #             update_row = None
                #             for update_row in EBARUtils.updateCursor(update_cursor):
                #                 update_values = []
                #
                #                 # ignore the ELEMENT_NATIONAL_ID by starting at index position 1
                #                 for field in species_fields[1:]:
                #
                #                     if len(file_line[field]) > 0:
                #                         update_values.append(file_line[field])
                #
                #                     else:
                #                         update_values.append(None)
                #
                #                 update_cursor.updateRow(update_values)
                #
                #             if update_row:
                #                 del update_row
                #
                #     # If the record is in the species csv but not in the species_kba table, then insert it
                #     else:
                #
                #         print("INSERT RECORD")
                #
                #         # THE INSERT CURSOR IS BROKEN AND NEEDS TO BE FIXED
                #         with arcpy.da.InsertCursor(param_geodatabase + '\\SpeciesKBA', species_fields) as insert_cursor:
                #             insert_values = []
                #
                #             # NEED TO ADD SCRIPT TO ADD THE SPECIESID AS WELL
                #
                #             # ignore the ELEMENT_NATIONAL_ID by starting at index position 1
                #             for field in species_fields[1:]:
                #
                #                 if len(file_line[field]) > 0:
                #                     insert_values.append(file_line[field])
                #
                #                 else:
                #                     insert_values.append(None)
                #
                #             insert_cursor.insertRow(insert_values)

                # If the record has no element_national_id or if the id is not in the biotics table
                else:
                    # do not update and do not add new records
                    EBARUtils.displayMessage(messages,
                                             "SKIP ROW {}. ELEMENT_NATIONAL_ID = {} not in BIOTICS table.".format(count,
                                                                                                                  element_national_id))
                    skipped += 1
                    # IDEA: ADD CLAUSE TO OUTPUT THIS LIST OF ELEMENT_NATIONAL_IDs TO A TEXT FILE

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
    param_csv.value = 'C:\\GIS_Processing\\KBA\\Scripts\\GITHUB\\Elements.csv'
    parameters = [param_geodatabase, param_csv]
    sslkba.RunSyncSpeciesListKBATool(parameters, None)
