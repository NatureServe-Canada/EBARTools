# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2026 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

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
import datetime
import StaticTranslations


class SyncSpeciesListBioticsTool:
    """Synchronize the BIOTICS_NATIONAL_ELEMENT and Species tables with Biotics"""
    def __init__(self):
        pass

    def runSyncSpeciesListBioticsTool(self, parameters, messages):
        # make variables for parms
        param_geodatabase = parameters[0].valueAsText
        param_csvs = parameters[1].valueAsText
        param_csvs = param_csvs.replace("'", '')
        param_csvs = param_csvs.split(';')

        for param_csv in param_csvs:
            EBARUtils.displayMessage(messages, 'File: ' + param_csv)
            # try to open data file as a csv
            infile = io.open(param_csv, 'r', encoding='utf-8-sig') #encoding='mbcs') # mbcs encoding is Windows ANSI
            reader = csv.DictReader(infile)

            # read existing IDs and scientific names into dicts
            EBARUtils.displayMessage(messages, 'Reading existing IDs')
            element_species_dict = EBARUtils.readElementSpecies(param_geodatabase)
            species_dict = EBARUtils.readSpecies(param_geodatabase)

            # process all file lines
            EBARUtils.displayMessage(messages, 'Processing file lines')
            count = 0
            updated = 0
            added = 0
            skipped = 0
            # fields that are sync'd whenever changed, overwriting values on update
            regular_fields = ['element_global_id',
                              'element_national_id',
                              'element_code',
                              'classification_status',
                              'category',
                              'tax_group',
                              'family_com',
                              'genus',
                              'ca_nname_level',
                              'national_scientific_name',
                              'national_engl_name',
                              'national_fr_name',
                              'g_rank',
                              'rounded_g_rank',
                              'g_rank_review_date',
                              'n_rank',
                              'rounded_n_rank',
                              'n_rank_review_date',
                              'bcd_style_n_rank',
                              'sara_status',
                              'sara_status_date',
                              'cosewic_id',
                              'cosewic_status',
                              'cosewic_date',
                              'interp_cosewic',
                              'interp_cosewic_date',
                              'cosewic_summary',
                              'cosewic_name',
                              'english_cosewic_com_name',
                              'french_cosewic_com_name',
                              'ca_origin',
                              'ca_regularity',
                              'ca_confidence',
                              'ca_presence',
                              'ca_population',
                              'short_citation_author',
                              'short_citation_year',
                              'author_name',
                              'major_habitat',
                              'kingdom',
                              'family',
                              'phylum',
                              'class',
                              'tax_order',
                              'global_scientific_name',
                              'global_synonyms',
                              'global_engl_name',
                              'glob_fr_name',
                              'global_unique_identifier',
                              'g_rank_change_date',
                              'n_rank_change_date',
                              'current_distribution',
                              'ca_dist_complete',
                              'total_eos_canada',
                              'ab_eos',
                              'ab_sfs',
                              'bc_eos',
                              'bc_sfs',
                              'mb_eos',
                              'mb_sfs',
                              'nt_eos',
                              'nt_sfs',
                              'on_eos',
                              'on_sfs',
                              'sk_eos',
                              'sk_sfs',
                              'yt_eos',
                              'yt_sfs',
                              'natn_nrk_all_ents',
                              'us_states',
                              'ca_distribution_comments',
                              'tax_com',
                              'inactive_ind',
                              'n_endemism_desc',
                              'g_juris_endem_desc',
                              'formatted_full_citation',
                              'cosewic_assess_criteria',
                              'kba_group']
            # fields that only get overwritten on update if they are currently null
            # this is to avoid overwriting a value from a cdc recevied as part of an input point/line/polygon import
            special_fields = ['ab_datasen',
                              'ab_datasen_cat',
                              'bc_datasen',
                              'bc_datasen_cat',
                              'lb_datasen',
                              'lb_datasen_cat',
                              'mb_datasen',
                              'mb_datasen_cat',
                              'nb_datasen',
                              'nb_datasen_cat',
                              'nf_datasen',
                              'nf_datasen_cat',
                              'ns_datasen',
                              'ns_datasen_cat',
                              'nt_datasen',
                              'nt_datasen_cat',
                              'nu_datasen',
                              'nu_datasen_cat',
                              'on_datasen',
                              'on_datasen_cat',
                              'pe_datasen',
                              'pe_datasen_cat',
                              'qc_datasen',
                              'qc_datasen_cat',
                              'sk_datasen',
                              'sk_datasen_cat',
                              'yt_datasen',
                              'yt_datasen_cat',
                              'ab_s_rank',
                              'ab_rounded_s_rank',
                              'bc_s_rank',
                              'bc_rounded_s_rank',
                              'lb_s_rank',
                              'lb_rounded_s_rank',
                              'mb_s_rank',
                              'mb_rounded_s_rank',
                              'nb_s_rank',
                              'nb_rounded_s_rank',
                              'nf_s_rank',
                              'nf_rounded_s_rank',
                              'ns_s_rank',
                              'ns_rounded_s_rank',
                              'nt_s_rank',
                              'nt_rounded_s_rank',
                              'nu_s_rank',
                              'nu_rounded_s_rank',
                              'on_s_rank',
                              'on_rounded_s_rank',
                              'pe_s_rank',
                              'pe_rounded_s_rank',
                              'qc_s_rank',
                              'qc_rounded_s_rank',
                              'sk_s_rank',
                              'sk_rounded_s_rank',
                              'yt_s_rank',
                              'yt_rounded_s_rank']
            french_fields = ['category_fr',
                             'tax_group_fr',
                             'family_com_fr',
                             'ca_nname_level_fr']
            all_fields = regular_fields + special_fields
            for file_line in reader:
                element_national_id = int(float(file_line['element_national_id']))
                EBARUtils.displayMessage(messages, 'element_national_id: ' + str(element_national_id))
                if element_national_id in element_species_dict:
                    # update if changed
                    # temporarily change this for one-time updating of translated french fields!!!
                    changed = True # False
                    # wrap updates overcome
                    # RuntimeError: Objects in this class cannot be updated outside an edit session [BIOTICS_ELEMENT_NATIONAL]
                    edit = arcpy.da.Editor(param_geodatabase)
                    edit.startEditing(with_undo=False, multiuser_mode=False)
                    with arcpy.da.UpdateCursor(param_geodatabase + '/BIOTICS_ELEMENT_NATIONAL',
                                               all_fields + ['nsx_url'] + french_fields,
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
                            # calc NSX_URL from GUID
                            update_values.append('https://explorer.natureserve.org/Taxon/' +
                                                file_line['global_unique_identifier'])
                            # translate French fields (use English if not in translation dict; periodically update latter)
                            category_fr = file_line['category']
                            if file_line['category'] in StaticTranslations.biotics_category_translation.keys():
                                category_fr = StaticTranslations.biotics_category_translation[file_line['category']]
                            update_values.append(category_fr)
                            tax_group_fr = file_line['tax_group']
                            if file_line['tax_group'] in StaticTranslations.biotics_taxa_group_translation.keys():
                                tax_group_fr = StaticTranslations.biotics_taxa_group_translation[file_line['tax_group']]
                            update_values.append(tax_group_fr)
                            family_com_fr = file_line['family_com']
                            if file_line['family_com'] in StaticTranslations.biotics_family_com_translation.keys():
                                family_com_fr = StaticTranslations.biotics_family_com_translation[file_line['family_com']]
                            update_values.append(family_com_fr)
                            ca_nname_level_fr = file_line['ca_nname_level']
                            if file_line['ca_nname_level'] in StaticTranslations.biotics_ca_nname_level_translation.keys():
                                ca_nname_level_fr = StaticTranslations.biotics_ca_nname_level_translation[file_line['ca_nname_level']]
                            update_values.append(ca_nname_level_fr)
                            if changed:
                                updated += 1
                                update_cursor.updateRow(update_values)
                        if update_row:
                            del update_row
                    # wrap updates overcome
                    # RuntimeError: Objects in this class cannot be updated outside an edit session [BIOTICS_ELEMENT_NATIONAL]
                    if changed:
                        edit.stopOperation()
                    edit.stopEditing(save_changes=True)
                else:
                    # create new Species and BIOTICS_ELEMENT_NATIONAL records
                    # first check for existing scientific name
                    if file_line['national_scientific_name'].lower() in species_dict:
                        msg = 'WARNING: record with ELEMENT_NATIONAL_ID ' + str(element_national_id) + \
                            ' skipped because it would create duplicate NATIONAL_SCIENTIFIC_NAME ' + \
                            file_line['national_scientific_name']
                        EBARUtils.displayMessage(messages, msg)
                        skipped += 1
                    else:
                        # wrap updates overcome
                        # RuntimeError: Objects in this class cannot be updated outside an edit session [Species]
                        edit = arcpy.da.Editor(param_geodatabase)
                        edit.startEditing(with_undo=False, multiuser_mode=False)
                        with arcpy.da.InsertCursor(param_geodatabase + '/Species', ['ActiveEBAR']) as insert_cursor:
                            object_id = insert_cursor.insertRow([1])
                        species_id = EBARUtils.getUniqueID(param_geodatabase + '/Species', 'SpeciesID', object_id)
                        all_fields.append('SpeciesID')
                        with arcpy.da.InsertCursor(param_geodatabase + '/BIOTICS_ELEMENT_NATIONAL',
                                                   all_fields + ['NSX_URL'] + french_fields) as insert_cursor:
                            insert_values = []
                            for field in all_fields:
                                if field == 'SpeciesID':
                                    insert_values.append(species_id)
                                elif len(file_line[field]) > 0:
                                    insert_values.append(file_line[field])
                                else:
                                    insert_values.append(None)
                            # calc NSX_URL from GUID
                            insert_values.append('https://explorer.natureserve.org/Taxon/' +
                                                file_line['global_unique_identifier'])
                            # translate French fields (use English if not in translation dict; periodically update latter)
                            category_fr = file_line['category']
                            if file_line['category'] in StaticTranslations.biotics_category_translation.keys():
                                category_fr = StaticTranslations.biotics_category_translation[file_line['category']]
                            insert_values.append(category_fr)
                            tax_group_fr = file_line['tax_group']
                            if file_line['tax_group'] in StaticTranslations.biotics_taxa_group_translation.keys():
                                tax_group_fr = StaticTranslations.biotics_taxa_group_translation[file_line['tax_group']]
                            insert_values.append(tax_group_fr)
                            family_com_fr = file_line['family_com']
                            if file_line['family_com'] in StaticTranslations.biotics_family_com_translation.keys():
                                family_com_fr = StaticTranslations.biotics_family_com_translation[file_line['family_com']]
                            insert_values.append(family_com_fr)
                            ca_nname_level_fr = file_line['ca_nname_level']
                            if file_line['ca_nname_level'] in StaticTranslations.biotics_ca_nname_level_translation.keys():
                                ca_nname_level_fr = StaticTranslations.biotics_ca_nname_level_translation[file_line['ca_nname_level']]
                            insert_values.append(ca_nname_level_fr)
                            insert_cursor.insertRow(insert_values)
                        all_fields.remove('SpeciesID')
                        added += 1
                        # wrap updates overcome
                        # RuntimeError: Objects in this class cannot be updated outside an edit session [Species]
                        if changed:
                            edit.stopOperation()
                        edit.stopEditing(save_changes=True)
                count += 1

            # # calculate NSX_URL
            # arcpy.CalculateField_management(param_geodatabase + '/BIOTICS_ELEMENT_NATIONAL', 'NSX_URL',
            #                                 "'https://explorer.natureserve.org/Taxon/' + !GLOBAL_UNIQUE_IDENTIFIER!")
            # summary and end time
            EBARUtils.displayMessage(messages, 'Summary:')
            EBARUtils.displayMessage(messages, 'Processed - ' + str(count))
            EBARUtils.displayMessage(messages, 'Updated - ' + str(updated))
            EBARUtils.displayMessage(messages, 'Added - ' + str(added))
            EBARUtils.displayMessage(messages, 'Skipped - ' + str(skipped))

            infile.close()

        return


# controlling process
if __name__ == '__main__':
    ssl = SyncSpeciesListBioticsTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = r'D:\GIS\EBAR\EBARDevJan2026.gdb'
    #param_geodatabase.value = 'C:/GIS/EBAR/nsc-gis-ebarkba.sde'
    param_csvs = arcpy.Parameter()
    param_csvs.value = "'C:/Users/rgree/Downloads/species_2026-11-13-11-38.csv'" #"'D:/GIS/EBAR/EBARTools/Samples/BioticsSpeciesExample.csv';'D:/GIS/EBAR/EBARTools/Samples/BioticsSpeciesExample.csv'"
    parameters = [param_geodatabase, param_csvs]
    ssl.runSyncSpeciesListBioticsTool(parameters, None)
