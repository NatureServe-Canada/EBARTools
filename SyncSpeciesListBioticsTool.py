# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: SyncSpeciesListTool.py
# ArcGIS Python tool for Synchronizing the BIOTICS_NATIONAL_ELEMENT and Species tables with Biotics

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import arcpy
import io
import csv
import EBARUtils


class SyncSpeciesListBioticsTool:
    """Synchronize the BIOTICS_NATIONAL_ELEMENT and Species tables with Biotics"""
    def __init__(self):
        pass

    def runSyncSpeciesListBioticsTool(self, parameters, messages):
        # make variables for parms
        param_geodatabase = parameters[0].valueAsText
        param_csv = parameters[1].valueAsText

        # try to open data file as a csv
        infile = io.open(param_csv, 'r', encoding='mbcs') # mbcs encoding is Windows ANSI
        reader = csv.DictReader(infile)

        # read existing IDs and scientific names into dicts
        EBARUtils.displayMessage(messages, 'Reading existing IDs')
        element_species_dict = EBARUtils.readElementSpecies(param_geodatabase)
        species_dict = EBARUtils.readSpecies(param_geodatabase)

        # process all file lines
        EBARUtils.displayMessage(messages, 'Processing file lines')
        count = 0
        added = 0
        skipped = 0
        # fields that are always sync'd, overwriting values on update
        regular_fields = ['ELEMENT_GLOBAL_ID',
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
                          'COSEWIC_DATE',
                          'INTERP_COSEWIC',
                          'INTERP_COSEWIC_DATE',
                          'COSEWIC_SUMMARY',
                          'COSEWIC_NAME',
                          'ENGLISH_COSEWIC_COM_NAME',
                          'FRENCH_COSEWIC_COM_NAME',
                          'CA_ORIGIN',
                          'CA_REGULARITY',
                          'CA_CONFIDENCE',
                          'CA_PRESENCE',
                          'CA_POPULATION',
                          'SHORT_CITATION_AUTHOR',
                          'SHORT_CITATION_YEAR',
                          'AUTHOR_NAME',
                          'MAJOR_HABITAT',
                          'PHYLUM',
                          'GLOBAL_SCIENTIFIC_NAME',
                          'GLOBAL_SYNONYMS',
                          'GLOBAL_ENGL_NAME',
                          'GLOB_FR_NAME',
                          'GLOBAL_UNIQUE_IDENTIFIER',
                          'G_RANK_CHANGE_DATE',
                          'N_RANK_CHANGE_DATE',
                          'CURRENT_DISTRIBUTION',
                          'CA_DIST_COMPLETE',
                          'TOTAL_EOS_CANADA',
                          'AB_EOS',
                          'AB_SFS',
                          'BC_EOS',
                          'BC_SFS',
                          'MB_EOS',
                          'MB_SFS',
                          'NT_EOS',
                          'NT_SFS',
                          'ON_EOS',
                          'ON_SFS',
                          'SK_EOS',
                          'SK_SFS',
                          'YT_EOS',
                          'YT_SFS',
                          'NATN_NRK_ALL_ENTS',
                          'US_STATES',
                          'CA_DISTRIBUTION_COMMENTS',
                          'TAX_COM',
                          'INACTIVE_IND',
                          'N_ENDEMISM_DESC',
                          'G_JURIS_ENDEM_DESC']
        # fields that only get overwritten on update if they are currently null
        # this is to avoid overwriting a value from a CDC recevied as part of an input point/line/polygon import
        special_fields = ['AB_DATASEN',
                          'AB_DATASEN_CAT',
                          'BC_DATASEN',
                          'BC_DATASEN_CAT',
                          'LB_DATASEN',
                          'LB_DATASEN_CAT',
                          'MB_DATASEN',
                          'MB_DATASEN_CAT',
                          'NB_DATASEN',
                          'NB_DATASEN_CAT',
                          'NF_DATASEN',
                          'NF_DATASEN_CAT',
                          'NS_DATASEN',
                          'NS_DATASEN_CAT',
                          'NT_DATASEN',
                          'NT_DATASEN_CAT',
                          'NU_DATASEN',
                          'NU_DATASEN_CAT',
                          'ON_DATASEN',
                          'ON_DATASEN_CAT',
                          'PE_DATASEN',
                          'PE_DATASEN_CAT',
                          'QC_DATASEN',
                          'QC_DATASEN_CAT',
                          'SK_DATASEN',
                          'SK_DATASEN_CAT',
                          'YT_DATASEN',
                          'YT_DATASEN_CAT']
        all_fields = regular_fields + special_fields
        for file_line in reader:
            element_national_id = int(float(file_line['ELEMENT_NATIONAL_ID']))
            EBARUtils.displayMessage(messages, 'ELEMENT_NATIONAL_ID: ' + str(element_national_id))
            if element_national_id in element_species_dict:
                with arcpy.da.UpdateCursor(param_geodatabase + '/BIOTICS_ELEMENT_NATIONAL', all_fields,
                                           'ELEMENT_NATIONAL_ID = ' + str(element_national_id)) as update_cursor:
                    update_row = None
                    for update_row in EBARUtils.updateCursor(update_cursor):
                        update_values = []
                        for field in all_fields:
                            if len(file_line[field]) > 0:
                                # special fields get replaced only if existing value is null
                                if field in special_fields and update_row[field]:
                                    # retain existing value
                                    update_values.append(update_row[field])
                                else:
                                    # import value
                                    update_values.append(file_line[field])
                            else:
                                # import NULL
                                update_values.append(None)
                        update_cursor.updateRow(update_values)
                    if update_row:
                        del update_row
            else:
                # create new Species and BIOTICS_ELEMENT_NATIONAL records
                # first check for existing scientific name
                if file_line['NATIONAL_SCIENTIFIC_NAME'].lower() in species_dict:
                    msg = 'WARNING: record with ELEMENT_NATIONAL_ID ' + str(element_national_id) + \
                        ' skipped because it would create duplicate NATIONAL_SCIENTIFIC_NAME ' + \
                        file_line['NATIONAL_SCIENTIFIC_NAME']
                    EBARUtils.displayMessage(messages, msg)
                    skipped += 1
                else:
                    with arcpy.da.InsertCursor(param_geodatabase + '/Species',
                                               ['ActiveEBAR']) as insert_cursor:
                        object_id = insert_cursor.insertRow([1])
                    species_id = EBARUtils.getUniqueID(param_geodatabase + '/Species', 'SpeciesID', object_id)
                    all_fields.append('SpeciesID')
                    with arcpy.da.InsertCursor(param_geodatabase + '/BIOTICS_ELEMENT_NATIONAL',
                                               all_fields) as insert_cursor:
                        insert_values = []
                        for field in all_fields:
                            if field == 'SpeciesID':
                                insert_values.append(species_id)
                            elif len(file_line[field]) > 0:
                                insert_values.append(file_line[field])
                            else:
                                insert_values.append(None)
                        #EBARUtils.displayMessage(messages, 'BIOTICS insert values: ' + str(insert_values))
                        insert_cursor.insertRow(insert_values)
                    all_fields.remove('SpeciesID')
                    added += 1
            count += 1

        # summary and end time
        EBARUtils.displayMessage(messages, 'Summary:')
        EBARUtils.displayMessage(messages, 'Processed - ' + str(count))
        EBARUtils.displayMessage(messages, 'Added - ' + str(added))
        EBARUtils.displayMessage(messages, 'Skipped - ' + str(skipped))

        infile.close()
        return


# controlling process
if __name__ == '__main__':
    ssl = SyncSpeciesListBioticsTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:/GIS/EBAR/EBAR-KBA-Dev.gdb'
    param_csv = arcpy.Parameter()
    param_csv.value = 'C:/Users/rgree/Downloads/rgreene_1614721964444.csv'
    parameters = [param_geodatabase, param_csv]
    ssl.runSyncSpeciesListBioticsTool(parameters, None)
