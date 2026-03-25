import arcpy
import EBARUtils
import StaticTranslations
import datetime


# Only run this code for Range Maps that were run before Generate Range Map tool had translation!!!
# Does not work with local file geodatabase


start_time = datetime.datetime.now()
geodatabase = r'C:\GIS\EBAR\nsc-gis-ebarkba.sde'
table_name_prefix = EBARUtils.getTableNamePrefix(geodatabase)
# use dict for optional DatasetSourceName translations
source_fr_dict = EBARUtils.readDatasetSourceTranslations(geodatabase)
#range_map_ids = [4295,4296,4298,4299,4326,4328,4354,4362,4377,4379,4399,4402,4414,4415,4416,4420,4425,4433,4444,4453,4476,4483,4498,4543,4544,4581,4582,4584,4588,4596,4598,4600,4601,4604,4605,4606,4613,4614,4616,4618,4619,4620,4621,4623,4625,4626,4627,4628,4629,4630,4631,4632,4633,4634,4635,4636,4637,4638,4639,4640,4641,4642,4643,4644,4645,4646,4647,4648,4649,4650,4651,4652,4653,4654,4655,4656,4657,4658,4660,4661,4662,4663,4665,4667,4668,4669,4670,4671,4672,4673,4674,4675,4676,4677,4678,4679,4680,4681,4683,4685,4686,4687,4689,4690,4691,4692,4693,4694,4695,4696,4697,4698,4699,4700,4701,4702,4734,4775,4781,4796,4818,4823,4877,4878,4892,4917,4918,4919,4920,4921,4922,4923,4924,4925,4927,4928,4929,4930,4931,4932,4934,4935,4936,4938,4939,4940,4941,4942,4948,4949,4950,4951,4952,4956,4958,4967,4968,4969,4976,4980,4981,4982,4983,4985,4987,4988]
#[3284,3286,3288,3289,3290,3291,3293,3296,3297,3298,3303,3311,3313,3314,3359,3444,3445,3446,3447,3456,3458,3459,3461,3462,3463,3468,3470,3471,3493,3501,3503,3504,3505,3506,3528,3564,3588,3589,3593,3603,3628,3662,3683,3703,3704,3710,3718,3733,3755,3764,3767,3768,3769,3770,3771,3772,3773,3774,3775,3776,3777,3778,3779,3781,3782,3783,3784,3785,3791,3793,3795,3796,3797,3798,3799,3800,3801,3802,3803,3804,3805,3806,3809,3810,3813,3814,3815,3816,3817,3818,3819,3821,3823,3828,3829,3830,3831,3832,3833,3834,3835,3836,3837,3838,3839,3840,3841,3842,3843,3844,3845,3846,3847,3848,3850,3851,3852,3853,3854,3855,3856,3857,3858,3867,3868,3872,3874,3892,3992,3993,3994,3995,4019,4020,4023,4040,4041,4043,4045,4047,4066,4074,4076,4081,4084,4097,4099,4100,4112,4158,4171,4196,4201,4203,4205,4206,4209,4210,4211,4212,4231,4251,4254,4265,4274,4275,4276,4277,4279,4280,4281,4283,4284,4287,4289,4290,4291,4292,4294]
#range_map_ids = [4020,4023,4040,4041,4043,4045,4047,4066,4074,4076,4081,4084,4097,4099,4100,4112,4158,4171,4196,4201,4203,4205,4206,4209,4210,4211,4212,4231,4251,4254,4265,4274,4275,4276,4277,4279,4280,4281,4283,4284,4287,4289,4290,4291,4292,4294,4687,4689,4691,4692,4693,4694,4695,4696
#range_map_ids = [4697,4698,4699,4700,4701,4702,4734,4775,4781,4796,4818,4823,4877,4878,4892,4917,4918,4919,4920,4921,4922,4923,4924,4925,4927,4928,4929,4930,4931,4932,4934,4935,4936,4938,4939,4940,4941,4942,4948,4949,4950,4951,4952,4956,4958,4967,4968,4969,4976,4980,4981,4982,4983,4985,4987,4988]
range_map_ids = [4690]
#range_map_ids = [3293,3289,3284,3286,3290,3291,3288] #864,2648
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
                arcpy.Statistics_analysis('rmeid', rmeid_stats,
                                          [['InputDataCount', 'SUM'], ['MinDate', 'MIN'], ['MaxDate', 'MAX'],
                                           ['MaxDate', 'MIN']],
                                          [table_name_prefix + 'DatasetSource.DatasetSourceName'])
                search_row = None
                with arcpy.da.SearchCursor(rmeid_stats,
                                           ['ebarkba_sde_datasetsource_datasetsourcename',
                                            'sum_ebarkba_sde_rangemapecoshapeinputdataset_inputdatacount',
                                            'max_ebarkba_sde_rangemapecoshapeinputdataset_maxdate',
                                            'min_ebarkba_sde_rangemapecoshapeinputdataset_maxdate',
                                            'min_ebarkba_sde_rangemapecoshapeinputdataset_mindate'],
                                           sql_clause=[None, 'ORDER BY ebarkba_sde_datasetsource_datasetsourcename']
                                           ) as search_cursor:
                    for search_row in EBARUtils.searchCursor(search_cursor):
                        if search_row['sum_ebarkba_sde_rangemapecoshapeinputdataset_inputdatacount']:
                            if len(input_records_fr) == 0:
                                input_records_fr += "Enregistrements d'entrée - "
                            else:
                                input_records_fr += ', '
                            input_records_fr += str(int(
                                search_row['sum_ebarkba_sde_rangemapecoshapeinputdataset_inputdatacount'])) + ' ' + \
                                source_fr_dict[search_row['ebarkba_sde_datasetsource_datasetsourcename']]
                            if search_row['max_ebarkba_sde_rangemapecoshapeinputdataset_maxdate']:
                                min_year = search_row['max_ebarkba_sde_rangemapecoshapeinputdataset_maxdate'].year
                                max_year = search_row['max_ebarkba_sde_rangemapecoshapeinputdataset_maxdate'].year
                                if search_row['min_ebarkba_sde_rangemapecoshapeinputdataset_maxdate']:
                                    if search_row['min_ebarkba_sde_rangemapecoshapeinputdataset_maxdate'].year < min_year:
                                        min_year = search_row['min_ebarkba_sde_rangemapecoshapeinputdataset_maxdate'].year
                                if search_row['min_ebarkba_sde_rangemapecoshapeinputdataset_maxdate']:
                                    if search_row['min_ebarkba_sde_rangemapecoshapeinputdataset_mindate'].year < min_year:
                                        min_year = search_row['min_ebarkba_sde_rangemapecoshapeinputdataset_mindate'].year
                                input_records_fr += ' ('
                                if min_year < max_year:
                                    input_records_fr += str(min_year) + '-'
                                input_records_fr += str(max_year) + ')'
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
                        if len(postfix) > 0:
                            postfix = EBARUtils.translateENtoFRUsingDeepL(postfix)
                            used_deepl = True
                    if len(reviewer_comments_fr) > 0:
                        reviewer_comments_fr += '<br>'
                    reviewer_comments_fr += prefix + ' - ' + postfix
                if used_deepl:
                    reviewer_comments_fr += ' (traduit par DeepL)'
            if len(summary_fr) > 2000:
                summary_fr = summary_fr[0:1889] + '... Veuillez consulter le fichier PDF et le package ZIP SIG en anglais pour obtenir les métadonnées complètes!'
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
                arcpy.Statistics_analysis('rmeid2', rmeid2_stats,
                                          [['InputDataCount', 'SUM'], ['MinDate', 'MIN'], ['MaxDate', 'MAX'],
                                           ['MaxDate', 'MIN']],
                                          [table_name_prefix + 'DatasetSource.DatasetSourceName'])
                search_row = None
                with arcpy.da.SearchCursor(rmeid2_stats,
                                           ['ebarkba_sde_datasetsource_datasetsourcename',
                                            'sum_ebarkba_sde_rangemapecoshapeinputdataset_inputdatacount',
                                            'max_ebarkba_sde_rangemapecoshapeinputdataset_maxdate',
                                            'min_ebarkba_sde_rangemapecoshapeinputdataset_maxdate',
                                            'min_ebarkba_sde_rangemapecoshapeinputdataset_mindate'],
                                           sql_clause=[None, 'ORDER BY ebarkba_sde_datasetsource_datasetsourcename']
                                           ) as search_cursor:
                    for search_row in EBARUtils.searchCursor(search_cursor):
                        if search_row['sum_ebarkba_sde_rangemapecoshapeinputdataset_inputdatacount']:
                            if len(input_records_fr) == 0:
                                input_records_fr += "Enregistrements d'entrée - "
                            else:
                                input_records_fr += ', '
                            input_records_fr += str(int(
                                search_row['sum_ebarkba_sde_rangemapecoshapeinputdataset_inputdatacount'])) + ' ' + \
                                source_fr_dict[search_row['ebarkba_sde_datasetsource_datasetsourcename']]
                            if search_row['max_ebarkba_sde_rangemapecoshapeinputdataset_maxdate']:
                                min_year = search_row['max_ebarkba_sde_rangemapecoshapeinputdataset_maxdate'].year
                                max_year = search_row['max_ebarkba_sde_rangemapecoshapeinputdataset_maxdate'].year
                                if search_row['min_ebarkba_sde_rangemapecoshapeinputdataset_maxdate']:
                                    if search_row['min_ebarkba_sde_rangemapecoshapeinputdataset_maxdate'].year < min_year:
                                        min_year = search_row['min_ebarkba_sde_rangemapecoshapeinputdataset_maxdate'].year
                                if search_row['min_ebarkba_sde_rangemapecoshapeinputdataset_maxdate']:
                                    if search_row['min_ebarkba_sde_rangemapecoshapeinputdataset_mindate'].year < min_year:
                                        min_year = search_row['min_ebarkba_sde_rangemapecoshapeinputdataset_mindate'].year
                                input_records_fr += ' ('
                                if min_year < max_year:
                                    input_records_fr += str(min_year) + '-'
                                input_records_fr += str(max_year) + ')'
                if search_row:
                    del search_row
                del search_cursor
                arcpy.Delete_management(rmeid2_stats)
                arcpy.Delete_management('rmeid2')

                # assemble
                sections = notes_fr.split('<br>')
                # notes_fr = sections[0]
                # notes_fr = notes_fr.replace('Input records', "Enregistrements d'entrée")
                # notes_fr = notes_fr.replace('Expert Ecoshape Review', "Avis d'experts ecoshape")
                notes_fr = input_records_fr
                if 'Expert Ecoshape Review' in sections[0]:
                    if len(notes_fr) > 0:
                        notes_fr += '; '
                    notes_fr += "Avis d'experts ecoshape"
                # each subsequent section is a reviewer comment
                used_deepl = False
                for section in sections[1:]:
                    subsections = section.split(' - ')
                    prefix = subsections[0]
                    prefix = prefix.replace('Reviewer Comment', 'Commentaire du réviseur')
                    prefix = prefix.replace('Anonymous', 'Anonyme')
                    #prefix = prefix.replace('Expert Ecoshape Review', "Avis d'experts ecoshape")
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
