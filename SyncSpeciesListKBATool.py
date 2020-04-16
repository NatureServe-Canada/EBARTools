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
import os
import EBARUtils


class SyncSpeciesListKBATool:
    """Synchronize the Species table with WCS KBA trigger species updates"""

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

        # dictionary of element_national_id and species_id
        element_species_dict = EBARUtils.readElementSpecies(param_geodatabase)

        # process input csv
        EBARUtils.displayMessage(messages, 'Processing input csv file')
        count = 1
        skipped = 0
        species_fields = ["SpeciesID",
                          "ELEMENT_NATIONAL_ID",
                          "KBATrigger",
                          "RemainingKBAPotential",
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
                          "Endemism_Type",
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
                          "PRECAUTIONARY_N_RANK_NonBreed",
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
                          "NSC_Comments",
                          "PotentialKBAs"
                          ]

        # use os library to access the folder that contains the geodatabase
        root_dir = os.path.dirname(param_geodatabase)

        # create output csv file to write the skipped element national id values
        outfile_name = root_dir + "\\output_skipped_element_national_ids.csv"
        outfile = open(outfile_name, 'w')
        IDs = []

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

                    # Generate list of existing element_national_id values in the Species table
                    existing_values = [row[0] for row in arcpy.da.SearchCursor(param_geodatabase + '\\Species',
                                                                               "ELEMENT_NATIONAL_ID")]

                    # If the record is in the species_kba table, then update it
                    if element_national_id in existing_values:

                        # print("UPDATE RECORD")

                        with arcpy.da.UpdateCursor(param_geodatabase + '\\Species', species_fields,
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

                        # If the record is in the species csv but not in the Species table, then insert it
                    else:

                        # print("INSERT RECORD")

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

                # If the record has no element_national_id or if the element_national_id is not in the biotics table
                else:

                    # do not update and do not add new records
                    EBARUtils.displayMessage(messages,
                                             "SKIP ROW {}. ELEMENT_NATIONAL_ID = {} not in BIOTICS table.".format(count,
                                                                                                                  element_national_id))
                    skipped += 1

                    # write skipped element_national_id values to output csv file
                    outfile.write(str(element_national_id) + ', ')

                    # append skipped element_national id values to list for ArcPy message print out
                    IDs.append(element_national_id)

            # increase line count for reader
            count += 1

        # summary and output messages
        EBARUtils.displayMessage(messages, '\nSummary:')
        EBARUtils.displayMessage(messages, 'Records read - ' + str(count))
        EBARUtils.displayMessage(messages, 'Records skipped - ' + str(skipped))
        EBARUtils.displayMessage(messages, '\nPrint out of Element_National_ID values with no match in Biotics table:')
        EBARUtils.displayMessage(messages, ','.join(map(str, IDs)))
        EBARUtils.displayMessage(messages, '\nThe above list of values are also recorded here {}'.format(outfile_name))

        infile.close()
        outfile.close()
        return


# controlling process
if __name__ == '__main__':
    sslkba = SyncSpeciesListKBATool()

    # hard-coded parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:\\GIS_Processing\\KBA\\Scripts\\GITHUB\\EBARDev.gdb'
    param_csv = arcpy.Parameter()
    #param_csv.value = 'C:\\GIS_Processing\\KBA\\Scripts\\GITHUB\\EBARTools\\SpeciesElementsExample.csv'
    param_csv.value = 'C:\\GIS_Processing\\KBA\\Scripts\\GITHUB\\Elements.csv'
    parameters = [param_geodatabase, param_csv]

    sslkba.RunSyncSpeciesListKBATool(parameters, None)
