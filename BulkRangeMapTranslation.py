import arcpy
import EBARUtils
import StaticTranslations
import datetime


# Only run this code for Range Maps that were run before Generate Range Map tool had translation!!!


start_time = datetime.datetime.now()
geodatabase = r'C:\GIS\EBAR\nsc-gis-ebarkba.sde'
table_name_prefix = EBARUtils.getTableNamePrefix(geodatabase)
# use dict for optional DatasetSourceName translations
source_fr_dict = EBARUtils.readDatasetSourceTranslations(geodatabase)
range_map_ids = [3850]
for range_map_id in range_map_ids:
    print('Translating ' + str(range_map_id))
    # RangeMap
    update_row = None
    with arcpy.da.UpdateCursor(geodatabase + '/RangeMap',
                               ['RangeStage', 'RangeStage_FR', 'RangeMapScope', 'RangeMapScope_FR', 'RangeMapNotes',
                                'RangeMapNotes_FR', 'RangeMetadata', 'RangeMetadata_FR', 'ReviewerComments',
                                'ReviewerComments_FR'], 'RangeMapID = ' + str(range_map_id)) as update_cursor:
        for update_row in EBARUtils.updateCursor(update_cursor):
            stage_fr = None
            if update_row['RangeStage'] in StaticTranslations.range_stage_translation.keys():
                stage_fr = StaticTranslations.range_stage_translation[update_row['RangeStage']]
            notes_fr = update_row['RangeMapNotes']
            if notes_fr:
                notes_fr = notes_fr.replace('Primary Species', 'Espèce primaire')
                notes_fr = notes_fr.replace('Secondary Species', 'Espèces secondaires')
                notes_fr = notes_fr.replace('Synonyms', 'Synonymes')
            summary_fr = update_row['RangeMetadata']
            if summary_fr:
                # build up DatasetSourceNames from RangeMapEcoshapeInputDataset
                input_records_fr = ''
                where = 'RangeMapEcoshapeID IN (SELECT RangeMapEcoshapeID FROM RangeMapEcoshape WHERE RangeMapID = ' + \
                    str(range_map_id) + ')'
                arcpy.MakeTableView_management(geodatabase + '/RangeMapEcoshapeInputDataset', 'rmeid')
                arcpy.SelectLayerByAttribute_management('rmeid', 'NEW_SELECTION', where)
                arcpy.AddJoin_management('rmeid', 'InputDatasetID', geodatabase + '/InputDataset', 'InputDatasetID')
                arcpy.AddJoin_management('rmeid', 'DatasetSourceID', geodatabase + '/DatasetSource', 'DatasetSourceID')
                rmeid_stats = geodatabase + '/TempRMEIDStats' + str(start_time.year) + str(start_time.month) + \
                    str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
                arcpy.Statistics_analysis('rmeid', rmeid_stats, [['InputDataCount', 'SUM']],
                                          [table_name_prefix + 'DatasetSource.DatasetSourceName'])
                search_row = None
                with arcpy.da.SearchCursor(rmeid_stats,
                                           ['ebarkba_sde_datasetsource_datasetsourcename',
                                            'sum_ebarkba_sde_rangemapecoshapeinputdataset_inputdatacount'],
                                           sql_clause=[None, 'ORDER BY ebarkba_sde_datasetsource_datasetsourcename']
                                           ) as search_cursor:
                    for search_row in EBARUtils.searchCursor(search_cursor):
                        if len(input_records_fr) == 0:
                            input_records_fr += "Enregistrements d'entrée - "
                        else:
                            input_records_fr += ', '
                        input_records_fr += str(int(
                            search_row['sum_ebarkba_sde_rangemapecoshapeinputdataset_inputdatacount'])) + ' ' + \
                            source_fr_dict[search_row['ebarkba_sde_datasetsource_datasetsourcename']]
                if search_row:
                    del search_row
                del search_cursor
                arcpy.Delete_management(rmeid_stats)
                arcpy.Delete_management('rmeid')

                # assemble
                # always have "Input Records -" should have "; Expert Reviews"
                sections = summary_fr.split(';')
                summary_fr = input_records_fr
                if len(sections) > 1:
                    for index in range(1, len(sections)):
                        summary_fr += ';' + sections[index]
                    summary_fr = summary_fr.replace('Expert Reviews', "Avis d'experts")
                    summary_fr = summary_fr.replace('Anonymous', 'Anonyme')

            reviewer_comments_fr = update_row['ReviewerComments']
            if reviewer_comments_fr:
                sections = reviewer_comments_fr.split('<br>')
                reviewer_comments_fr = ''
                used_deepl = False
                for section in sections:
                    # each subsection is a reviewer comment
                    subsections = section.split(' - ')
                    prefix = subsections[0]
                    prefix = prefix.replace('Reviewer Comment', 'Commentaire du réviseur')
                    prefix = prefix.replace('Anonymous', 'Anonyme')
                    postfix = subsections[1]
                    if postfix == 'Unpublished':
                        postfix = 'Non publié'
                    else:
                        postfix = EBARUtils.translateENtoFRUsingDeepL(postfix)
                        used_deepl = True
                    if len(reviewer_comments_fr) > 0:
                        reviewer_comments_fr += '<br>'
                    reviewer_comments_fr += prefix + ' - ' + postfix
                if used_deepl:
                    reviewer_comments_fr += ' (traduit par DeepL)'
            update_cursor.updateRow([update_row['RangeStage'], stage_fr, update_row['RangeMapScope'],
                                     StaticTranslations.range_map_scope_translation[update_row['RangeMapScope']],
                                     update_row['RangeMapNotes'], notes_fr, update_row['RangeMetadata'], summary_fr,
                                     update_row['ReviewerComments'], reviewer_comments_fr])
    if update_row:
        del update_row
    del update_cursor

    # RangeMapEcoshape
    update_row = None
    with arcpy.da.UpdateCursor(geodatabase + '/RangeMapEcoshape',
                               ['RangeMapEcoshapeID', 'RangeMapEcoshapeNotes', 'RangeMapEcoshapeNotes_FR'],
                               'RangeMapID = ' + str(range_map_id)) as update_cursor:
        for update_row in EBARUtils.updateCursor(update_cursor):
            notes_fr = update_row['RangeMapEcoshapeNotes']
            if notes_fr:
                # build up DatasetSourceNames from RangeMapEcoshapeInputDataset
                input_records_fr = ''
                where = 'RangeMapEcoshapeID = ' + str(update_row['RangeMapEcoshapeID'])
                arcpy.MakeTableView_management(geodatabase + '/RangeMapEcoshapeInputDataset', 'rmeid2')
                arcpy.SelectLayerByAttribute_management('rmeid2', 'NEW_SELECTION', where)
                arcpy.AddJoin_management('rmeid2', 'InputDatasetID', geodatabase + '/InputDataset', 'InputDatasetID')
                arcpy.AddJoin_management('rmeid2', 'DatasetSourceID', geodatabase + '/DatasetSource', 'DatasetSourceID')
                rmeid2_stats = geodatabase + '/TempRMEID2Stats' + str(start_time.year) + str(start_time.month) + \
                    str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
                arcpy.Statistics_analysis('rmeid2', rmeid2_stats, [['InputDataCount', 'SUM']],
                                          [table_name_prefix + 'DatasetSource.DatasetSourceName'])
                search_row = None
                with arcpy.da.SearchCursor(rmeid2_stats,
                                           ['ebarkba_sde_datasetsource_datasetsourcename',
                                            'sum_ebarkba_sde_rangemapecoshapeinputdataset_inputdatacount'],
                                           sql_clause=[None, 'ORDER BY ebarkba_sde_datasetsource_datasetsourcename']
                                           ) as search_cursor:
                    for search_row in EBARUtils.searchCursor(search_cursor):
                        if len(input_records_fr) == 0:
                            input_records_fr += "Enregistrements d'entrée - "
                        else:
                            input_records_fr += ', '
                        input_records_fr += str(int(
                            search_row['sum_ebarkba_sde_rangemapecoshapeinputdataset_inputdatacount'])) + ' ' + \
                            source_fr_dict[search_row['ebarkba_sde_datasetsource_datasetsourcename']]
                if search_row:
                    del search_row
                del search_cursor
                arcpy.Delete_management(rmeid2_stats)
                arcpy.Delete_management('rmeid2')

                # assemble
                sections = notes_fr.split('<br>')
                # notes_fr = sections[0]
                # notes_fr = notes_fr.replace('Input records', "Enregistrements d'entrée")
                # notes_fr = notes_fr.replace('Expert Ecoshape Review', "Avis d'experts écoshape")
                notes_fr = input_records_fr
                if 'Expert Ecoshape Review' in sections[0]:
                    notes_fr += "; Avis d'experts écoshape"
                # each subsequent section is a reviewer comment
                used_deepl = False
                for section in sections[1:]:
                    subsections = section.split(' - ')
                    prefix = subsections[0]
                    prefix = prefix.replace('Reviewer Comment', 'Commentaire du réviseur')
                    prefix = prefix.replace('Anonymous', 'Anonyme')
                    prefix = prefix.replace('Expert Ecoshape Review', "Avis d'experts écoshape")
                    postfix = subsections[1]
                    if postfix == 'Unpublished':
                        postfix = 'Non publié'
                    else:
                        postfix = EBARUtils.translateENtoFRUsingDeepL(postfix)
                        used_deepl = True
                    notes_fr += '<br>' + prefix + ' - ' + postfix
                if used_deepl:
                    notes_fr += ' (traduit par DeepL)'
            update_cursor.updateRow([update_row['RangeMapEcoshapeID'], update_row['RangeMapEcoshapeNotes'], notes_fr])
    if update_row:
        del update_row
    del update_cursor
