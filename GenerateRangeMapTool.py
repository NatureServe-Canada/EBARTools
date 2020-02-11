# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: GenerateRangeMapTool.py
# ArcGIS Python tool for generating EBAR range maps from spatial data

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
#import sys
#import locale
import EBARUtils
import arcpy
import datetime


class GenerateRangeMapTool:
    """Generate Range Map for a species from available spatial data in the EBAR geodatabase"""
    def __init__(self):
        pass

    def RunGenerateRangeMapTool(self, parameters, messages):
        # debugging/testing
        #print(locale.getpreferredencoding())
        #return

        # check out any needed extension licenses
        #arcpy.CheckOutExtension('Spatial')

        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True
        # buffer size in metres #, used if Accuracy not provided
        default_buffer_size = 10
        ## proportion of point buffer that must be within ecoshape to get Present; otherwise gets Presence Expected
        #buffer_proportion_overlap = 0.6
        # number of years beyond which Presence gets set to Historical
        age_for_historical = 40

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        param_geodatabase = parameters[0].valueAsText
        param_species = parameters[1].valueAsText
        param_secondary = parameters[2].valueAsText
        if param_secondary:
            param_secondary = param_secondary.replace("'", '')
            param_secondary = param_secondary.split(';')
        param_version = parameters[3].valueAsText
        param_stage = parameters[4].valueAsText

        # use passed geodatabase as workspace (still seems to go to default geodatabase)
        arcpy.env.workspace = param_geodatabase

        # get table name prefix (needed for joined tables and feature classes in enterprise geodatabases)
        table_name_prefix = EBARUtils.getTableNamePrefix(param_geodatabase)

        # check for species
        species_id, short_citation = EBARUtils.checkSpecies(param_species, param_geodatabase)
        if not species_id:
            EBARUtils.displayMessage(messages, 'ERROR: Species not found')
            # terminate with error
            return
            #raise arcpy.ExecuteError
        param_species += '' + short_citation

        # check for secondary species
        species_ids = str(species_id)
        secondary_ids = []
        secondary_names = ''
        additional_input_records = 0
        if param_secondary:
            for secondary in param_secondary:
                secondary_id, short_citation = EBARUtils.checkSpecies(secondary, param_geodatabase)
                if not secondary_id:
                    EBARUtils.displayMessage(messages, 'ERROR: Secondary species not found')
                    # terminate with error
                    return
                    #raise arcpy.ExecuteError
                species_ids += ',' + str(secondary_id)
                if secondary_id in secondary_ids:
                    EBARUtils.displayMessage(messages, 'ERROR: Same secondary species specified more than once')
                    # terminate with error
                    return
                    #raise arcpy.ExecuteError
                secondary_ids.append(secondary_id)
                if len(secondary_names) > 0:
                    secondary_names += ', '
                secondary_names += secondary + '' + short_citation

        # check for range map record and add if necessary
        EBARUtils.displayMessage(messages, 'Checking for existing range map')
        range_map_id = None
        arcpy.MakeTableView_management(param_geodatabase + '/RangeMap', 'range_map_view')
        # filter just on species
        arcpy.SelectLayerByAttribute_management('range_map_view', 'NEW_SELECTION', 'SpeciesID = ' + str(species_id))
        # build list of existing range maps with same primary and secondary
        prev_range_map = []
        prev_range_map_ids = ''
        # start with list of range map candidates due to complexity of checking secondary
        match_candidate = []
        candidate_secondary_count = {}
        candidate_secondary_match_count = {}
        arcpy.AddJoin_management('range_map_view', 'RangeMapID',
                                 param_geodatabase + '/SecondarySpecies', 'RangeMapID', 'KEEP_ALL')
        with arcpy.da.SearchCursor('range_map_view', [table_name_prefix + 'RangeMap.RangeMapID',
                                                      table_name_prefix + 'SecondarySpecies.SpeciesID']) as cursor:
            row = None
            for row in EBARUtils.searchCursor(cursor):
                if row[table_name_prefix + 'RangeMap.RangeMapID'] not in match_candidate:
                    match_candidate.append(row[table_name_prefix + 'RangeMap.RangeMapID'])
                    candidate_secondary_match_count[row[table_name_prefix + 'RangeMap.RangeMapID']] = 0
                    candidate_secondary_count[row[table_name_prefix + 'RangeMap.RangeMapID']] = 0
                if row[table_name_prefix + 'SecondarySpecies.SpeciesID'] in secondary_ids:
                    # secondary matches
                    candidate_secondary_match_count[row[table_name_prefix + 'RangeMap.RangeMapID']] += 1
                if row[table_name_prefix + 'SecondarySpecies.SpeciesID']:
                    # secondary count
                    candidate_secondary_count[row[table_name_prefix + 'RangeMap.RangeMapID']] += 1
            if row:
                del row
        arcpy.RemoveJoin_management('range_map_view', table_name_prefix + 'SecondarySpecies')
        # check candidates for secondary match
        for candidate in match_candidate:
            if (candidate_secondary_match_count[candidate] == len(secondary_ids) and
                candidate_secondary_count[candidate] == len(secondary_ids)):
                prev_range_map.append(candidate)
                prev_range_map_ids = ','.join(map(str, prev_range_map))
        if len(prev_range_map_ids) > 0:
            # check prev for matching version and stage
            with arcpy.da.SearchCursor('range_map_view', ['RangeMapID', 'RangeVersion', 'RangeStage'],
                                       'RangeMapID IN (' + prev_range_map_ids + ')') as cursor:
                row = None
                for row in EBARUtils.searchCursor(cursor):
                    if (row['RangeVersion'] == param_version and row['RangeStage'] == param_stage):
                        # range map to be geneated already exists
                        range_map_id = row['RangeMapID']
                        prev_range_map.remove(range_map_id)
                        prev_range_map_ids = ','.join(map(str, prev_range_map)) 

        if range_map_id:
            arcpy.SelectLayerByAttribute_management('range_map_view', 'NEW_SELECTION',
                                                    'RangeMapID = ' + str(range_map_id))
            # check for completed Reviews or Reviews in progress
            review_found = False
            review_completed = False
            ecoshape_review = False
            # use multi-table joins
            arcpy.AddJoin_management('range_map_view', 'RangeMapID',
                                      param_geodatabase + '/Review', 'RangeMapID', 'KEEP_COMMON')

            # check for completed reviews, and if so terminate
            with arcpy.da.SearchCursor('range_map_view', [table_name_prefix + 'Review.DateCompleted']) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    review_found = True
                    if row[table_name_prefix + 'Review.DateCompleted']:
                        review_completed = True
                        break
                if review_found:
                    del row
            if review_completed:
                EBARUtils.displayMessage(messages, 'ERROR: Range Map already exists with completed review(s)')
                # terminate with error
                return
                #raise arcpy.ExecuteError

            # check for reviews in progress, and if so terminate
            if review_found:
                arcpy.AddJoin_management('range_map_view', table_name_prefix + 'Review.ReviewID',
                                         param_geodatabase + '/EcoshapeReview', 'ReviewID', 'KEEP_COMMON')
                with arcpy.da.SearchCursor('range_map_view',
                                           [table_name_prefix + 'EcoshapeReview.ReviewID']) as cursor:
                    for row in EBARUtils.searchCursor(cursor):
                        ecoshape_review = True
                        break
                    if ecoshape_review:
                        del row
                if ecoshape_review:
                    EBARUtils.displayMessage(messages, 'ERROR: Range Map already exists with review(s) in progress')
                    # terminate with error
                    return
                    #raise arcpy.ExecuteError

                arcpy.RemoveJoin_management('range_map_view', table_name_prefix + 'EcoshapeReview')
            arcpy.RemoveJoin_management('range_map_view', table_name_prefix + 'Review')

            # no reviews completed or in progress, so delete any existing related records
            EBARUtils.displayMessage(messages, 'Range Map already exists with but with no review(s) completed or in '
                                               'progress, so existing related records will be deleted')
            # consider replacing the following code blocks with select then Delete Rows tools
            with arcpy.da.SearchCursor(param_geodatabase + '/RangeMapEcoshape', ['RangeMapEcoshapeID'],
                                       'RangeMapID = ' + str(range_map_id)) as rme_cursor:
                for rme_row in EBARUtils.searchCursor(rme_cursor):
                    rmeid = False
                    with arcpy.da.UpdateCursor(param_geodatabase + '/RangeMapEcoshapeInputDataset',
                                               ['RangeMapEcoshpInputDatasetID'],
                                                'RangeMapEcoshapeID = ' + \
                                                str(rme_row['RangeMapEcoshapeID'])) as rmeid_cursor:
                        for rmeid_row in rmeid_cursor:
                            rmeid_cursor.deleteRow()
                            rmeid = True
                        if rmeid:
                            del rmeid_row
            with arcpy.da.UpdateCursor(param_geodatabase + '/RangeMapEcoshape', ['RangeMapEcoshapeID'],
                                       'RangeMapID = ' + str(range_map_id)) as rme_cursor:
                range_map_ecoshape = False
                for rme_row in EBARUtils.updateCursor(rme_cursor):
                    rme_cursor.deleteRow()
                    range_map_ecoshape = True
                if range_map_ecoshape:
                    del rme_row
                    EBARUtils.displayMessage(messages, 'Existing Range Map Ecoshape records deleted')
            existing_secondary = False
            with arcpy.da.UpdateCursor(param_geodatabase + '/SecondarySpecies', ['SecondarySpeciesID'],
                                       'RangeMapID = ' + str(range_map_id)) as es_cursor:
                for es_row in EBARUtils.updateCursor(es_cursor):
                    es_cursor.deleteRow()
                    existing_secondary = True
                if existing_secondary:
                    del es_row
                    EBARUtils.displayMessage(messages, 'Existing Secondary Species records deleted')

        else:
            arcpy.SelectLayerByAttribute_management('range_map_view', 'CLEAR_SELECTION')
            # create RangeMap record
            with arcpy.da.InsertCursor('range_map_view',
                                       ['SpeciesID', 'RangeVersion', 'RangeStage', 'IncludeInEBARReviewer']) as cursor:
                range_map_id = cursor.insertRow([species_id, param_version, param_stage, 0])
            EBARUtils.setNewID(param_geodatabase + '/RangeMap', 'RangeMapID', 'OBJECTID = ' + str(range_map_id))
            EBARUtils.displayMessage(messages, 'Range Map record created')

        # create SecondarySpecies records
        if param_secondary:
            with arcpy.da.InsertCursor(param_geodatabase + '/SecondarySpecies',
                                       ['RangeMapID', 'SpeciesID']) as cursor:
                for secondary in param_secondary:
                    secondary_id, short_citation = EBARUtils.checkSpecies(secondary, param_geodatabase)
                    cursor.insertRow([range_map_id, secondary_id])
            EBARUtils.setNewID(param_geodatabase + '/SecondarySpecies', 'SecondarySpeciesID',
                               'RangeMapID = ' + str(range_map_id))
            EBARUtils.displayMessage(messages, 'Secondary Species records created')

        # select all points for species and buffer
        EBARUtils.displayMessage(messages, 'Buffering Input Points')
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/InputPoint', 'input_point_layer')
        # select any from secondary inputs (chicken and egg - RangeMapID must already exist!)
        arcpy.AddJoin_management('input_point_layer', 'InputPointID', param_geodatabase + '/SecondaryInput',
                                 'InputPointID')
        arcpy.SelectLayerByAttribute_management('input_point_layer', 'NEW_SELECTION',
                                                table_name_prefix + 'SecondaryInput.RangeMapID = ' + str(range_map_id))
        result = arcpy.GetCount_management('input_point_layer')
        additional_input_records += int(result[0])
        arcpy.RemoveJoin_management('input_point_layer', table_name_prefix + 'SecondaryInput')
        # add "real" points to selection
        arcpy.SelectLayerByAttribute_management('input_point_layer', 'ADD_TO_SELECTION',
                                                'SpeciesID IN (' + species_ids + ') AND (Accuracy IS NULL'
                                                ' OR Accuracy <= ' + str(EBARUtils.worst_accuracy) + ')'
                                                ' AND MaxDate IS NOT NULL')
        EBARUtils.checkAddField('input_point_layer', 'buffer', 'LONG')
        code_block = '''
def GetBuffer(accuracy):
    ret = accuracy
    if not ret:
        ret = ''' + str(default_buffer_size) + '''
    return ret'''
        arcpy.CalculateField_management('input_point_layer', 'buffer', 'GetBuffer(!Accuracy!)', 'PYTHON3', code_block)
        temp_point_buffer = 'TempPointBuffer' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.Buffer_analysis('input_point_layer', temp_point_buffer, 'buffer')
        #arcpy.Buffer_analysis('input_point_layer', temp_point_buffer, default_buffer_size)

        # select all lines for species and buffer
        EBARUtils.displayMessage(messages, 'Buffering Input Lines')
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/InputLine', 'input_line_layer')
        # select any from secondary inputs (chicken and egg - RangeMapID must already exist!)
        arcpy.AddJoin_management('input_line_layer', 'InputLineID', param_geodatabase + '/SecondaryInput',
                                 'InputLineID')
        arcpy.SelectLayerByAttribute_management('input_line_layer', 'NEW_SELECTION',
                                                table_name_prefix + 'SecondaryInput.RangeMapID = ' + str(range_map_id))
        result = arcpy.GetCount_management('input_line_layer')
        additional_input_records += int(result[0])
        arcpy.RemoveJoin_management('input_line_layer', table_name_prefix + 'SecondaryInput')
        # add "real" points to selection
        arcpy.SelectLayerByAttribute_management('input_line_layer', 'ADD_TO_SELECTION',
                                                'SpeciesID IN (' + species_ids + ') AND (Accuracy IS NULL'
                                                ' OR Accuracy <= ' + str(EBARUtils.worst_accuracy) + ')'
                                                ' AND MaxDate IS NOT NULL')
        temp_line_buffer = 'TempLineBuffer' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.Buffer_analysis('input_line_layer', temp_line_buffer, default_buffer_size)

        # select all polygons for species
        EBARUtils.displayMessage(messages, 'Selecting Input Polygons')
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/InputPolygon', 'input_polygon_layer')
        # select any from secondary inputs (chicken and egg - RangeMapID must already exist!)
        arcpy.AddJoin_management('input_polygon_layer', 'InputPolygonID', param_geodatabase + '/SecondaryInput',
                                 'InputPolygonID')
        arcpy.SelectLayerByAttribute_management('input_polygon_layer', 'NEW_SELECTION',
                                                table_name_prefix + 'SecondaryInput.RangeMapID = ' + str(range_map_id))
        result = arcpy.GetCount_management('input_polygon_layer')
        additional_input_records += int(result[0])
        arcpy.RemoveJoin_management('input_polygon_layer', table_name_prefix + 'SecondaryInput')
        # add "real" points to selection
        arcpy.SelectLayerByAttribute_management('input_polygon_layer', 'ADD_TO_SELECTION',
                                                'SpeciesID IN (' + species_ids + ') AND (Accuracy IS NULL'
                                                ' OR Accuracy <= ' + str(EBARUtils.worst_accuracy) + ')'
                                                ' AND MaxDate IS NOT NULL')

        # merge buffer polygons and input polygons
        EBARUtils.displayMessage(messages, 'Merging Buffered Points and Lines and Input Polygons')
        temp_all_inputs = 'TempAllInputs' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.Merge_management([temp_point_buffer, temp_line_buffer, 'input_polygon_layer'], temp_all_inputs, None,
                               'ADD_SOURCE_INFO')
        arcpy.MakeFeatureLayer_management(temp_all_inputs, 'all_inputs_layer')

        # eo ranks, when available, override dates in determining historical (fake the date to accomplish this)
        EBARUtils.displayMessage(messages, 'Applying EO Ranks, where available, to determine historical records')
        result = arcpy.SelectLayerByAttribute_management('all_inputs_layer', 'NEW_SELECTION',
                                                         "EORank IN ('H', 'H?', 'X', 'X?')")
        if int(result[1]) > 0:
            # 1000 years in the past
            fake_date_expr = 'datetime.datetime(datetime.datetime.now().year - 1000, 1, 1)'
            arcpy.CalculateField_management('all_inputs_layer', 'MaxDate', fake_date_expr)
        result = arcpy.SelectLayerByAttribute_management('all_inputs_layer', 'NEW_SELECTION',
                                                         "EORank IS NOT NULL AND EORank NOT IN ('H', 'H?', 'X', 'X?')")
        if int(result[1]) > 0:
            # 1000 years in the future
            fake_date_expr = 'datetime.datetime(datetime.datetime.now().year + 1000, 1, 1)'
            arcpy.CalculateField_management('all_inputs_layer', 'MaxDate', fake_date_expr)
        arcpy.SelectLayerByAttribute_management('all_inputs_layer', 'CLEAR_SELECTION')

        # pairwise intersect buffers and ecoshape polygons
        EBARUtils.displayMessage(messages, 'Pairwise Intersecting All Inputs with Ecoshapes')
        temp_pairwise_intersect = 'TempPairwiseIntersect' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.PairwiseIntersect_analysis(['all_inputs_layer',  param_geodatabase + '/Ecoshape'],
                                         temp_pairwise_intersect)
        arcpy.AddIndex_management(temp_pairwise_intersect, 'InputDatasetID', 'idid_idx')
        arcpy.MakeFeatureLayer_management(temp_pairwise_intersect, 'pairwise_intersect_layer')

        ## calculate proportion buffer per ecoshape piece based on size of full buffer
        #EBARUtils.displayMessage(messages, 'Calculating Proportion of Polygon per Ecoshape')
        ## calculate total size of pieces for each buffer (will not equal original buffer size if outside ecoshapes)
        #EBARUtils.checkAddField('pairwise_intersect_layer', 'PolygonPropn', 'FLOAT')
        ## calculate total size of buffer (will not equal original buffer size if it extends outside ecoshapes)
        #if arcpy.Exists('TempTotalArea'):
        #    arcpy.Delete_management('TempTotalArea')
        #arcpy.Statistics_analysis('pairwise_intersect_layer', 'TempTotalArea', [['Shape_Area', 'SUM']],
        #                          'FID_TempAllInputs')
        #arcpy.AddJoin_management('pairwise_intersect_layer', 'FID_TempAllInputs', 'TempTotalArea',
        #                         'FID_TempAllInputs')
        #arcpy.CalculateField_management('pairwise_intersect_layer', 'TempPairwiseIntersect.PolygonPropn',
        #                                '!TempPairwiseIntersect.Shape_Area! / !TempTotalArea.SUM_Shape_Area!',
        #                                'PYTHON3')
        #arcpy.RemoveJoin_management('pairwise_intersect_layer', 'TempTotalArea')

        ## get max date and buffer proportion per ecoshape
        #EBARUtils.displayMessage(messages, 'Determining Maximum Polygon Proportion and Date per Ecoshape')
        #if arcpy.Exists('TempEcoshapeMaxPolygon'):
        #    arcpy.Delete_management('TempEcoshapeMaxPolygon')
        #arcpy.Statistics_analysis('pairwise_intersect_layer', 'TempEcoshapeMaxPolygon',
        #                          [['PolygonPropn', 'MAX'], ['MaxDate', 'MAX']], 'EcoshapeID')

        # get max date per ecoshape
        EBARUtils.displayMessage(messages, 'Determining Maximum Date per Ecoshape')
        temp_ecoshape_max_polygon = 'TempEcoshapeMaxPolygon' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.Statistics_analysis('pairwise_intersect_layer', temp_ecoshape_max_polygon,
                                  [['MaxDate', 'MAX']], 'EcoshapeID')

        # create RangeMapEcoshape records based on max date #and proportion overlap 
        EBARUtils.displayMessage(messages, 'Creating Range Map Ecoshape records')
        with arcpy.da.InsertCursor(param_geodatabase + '/RangeMapEcoshape',
                                   ['RangeMapID', 'EcoshapeID', 'Presence']) as insert_cursor:
            input_found = False
            #with arcpy.da.SearchCursor(temp_ecoshape_max_polygon,
            #                           ['EcoshapeID', 'MAX_PolygonPropn', 'MAX_MaxDate']) as search_cursor:
            with arcpy.da.SearchCursor(temp_ecoshape_max_polygon,
                                       ['EcoshapeID', 'MAX_MaxDate']) as search_cursor:
                for row in EBARUtils.searchCursor(search_cursor):
                    input_found = True
                    presence = 'X'
                    if row['MAX_MaxDate']:
                        if (datetime.datetime.now().year - row['MAX_MaxDate'].year) <= age_for_historical:
                            # eo rank not in ('H', 'H?', 'X', 'X?') or "new" date gets Present
                            presence = 'P'
                        else:
                            # otherwise Historical
                            presence = 'H'
                    insert_cursor.insertRow([range_map_id, row['EcoshapeID'], presence])
                if input_found:
                    del row
        if not input_found:
            EBARUtils.displayMessage(messages, 'WARNING: No inputs/buffers overlap ecoshapes')
            # terminate
            return

        # get ecoshape input counts by dataset
        EBARUtils.displayMessage(messages, 'Counting Ecoshape inputs by Dataset')
        temp_ecoshape_countby_dataset = 'TempEcoshapeCountByDataset' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.Statistics_analysis('pairwise_intersect_layer', temp_ecoshape_countby_dataset,
                                  [['InputPointID', 'COUNT']], ['EcoshapeID', 'InputDatasetID'])

        # get ecoshape input counts by source
        EBARUtils.displayMessage(messages, 'Counting Ecoshape Inputs by Dataset Source')
        temp_ecoshape_countby_source = 'TempEcoshapeCountBySource' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.AddJoin_management('pairwise_intersect_layer', 'InputDatasetID',
                                 param_geodatabase + '/InputDataset', 'InputDatasetID', 'KEEP_COMMON')
        arcpy.AddJoin_management('pairwise_intersect_layer', 'DatasetSourceID',
                                 param_geodatabase + '/DatasetSource', 'DatasetSourceID', 'KEEP_COMMON')
        arcpy.Statistics_analysis('pairwise_intersect_layer', temp_ecoshape_countby_source, [['InputPointID', 'COUNT']],
                                  ['EcoshapeID', table_name_prefix + 'DatasetSource.DatasetSourceName',
                                   table_name_prefix + 'DatasetSource.DatasetType'])
        arcpy.RemoveJoin_management('pairwise_intersect_layer', table_name_prefix + 'DatasetSource')
        arcpy.RemoveJoin_management('pairwise_intersect_layer', table_name_prefix + 'InputDataset')

        # apply Reviews, Presence categories and summaries to RangeMapEcoshape records
        EBARUtils.displayMessage(messages,
                                 'Applying Reviews, Presence categories and summaries to RangeMapEcoshape records')
        ecoshape_reviews = 0
        if len(prev_range_map_ids) > 0:
            arcpy.MakeTableView_management(param_geodatabase + '/EcoshapeReview', 'ecoshape_review_view')
            arcpy.AddJoin_management('ecoshape_review_view', 'ReviewID', param_geodatabase + '/Review', 'ReviewID')
        # loop existing ecoshapes
        with arcpy.da.UpdateCursor(param_geodatabase + '/RangeMapEcoshape',
                                   ['EcoshapeID', 'Presence', 'RangeMapEcoshapeNotes'],
                                   'RangeMapID = ' + str(range_map_id)) as update_cursor:
            for update_row in EBARUtils.updateCursor(update_cursor):
                # check for ecoshape "remove" reviews
                remove = False
                if len(prev_range_map_ids) > 0:
                    with arcpy.da.SearchCursor('ecoshape_review_view', [table_name_prefix + 'EcoshapeReview.OBJECTID'],
                                               table_name_prefix + 'Review.RangeMapID IN (' + \
                                                   prev_range_map_ids + ') AND ' + table_name_prefix + \
                                                   'EcoshapeReview.UseForMapGen = 1 AND ' + table_name_prefix + \
                                                   "EcoshapeReview.AddRemove = '2' AND "  + table_name_prefix + \
                                                   'EcoshapeReview.EcoshapeID = ' + \
                                                   str(update_row['EcoshapeID'])) as search_cursor:
                        for search_row in EBARUtils.searchCursor(search_cursor):
                            ecoshape_reviews += 1
                            remove = True
                if remove:
                    del search_row
                    update_cursor.deleteRow()
                else:
                    # kludge because arc ends up with different field names under Enterprise gdb after joining
                    field_names = [f.name for f in arcpy.ListFields(temp_ecoshape_countby_source) if f.aliasName in
                                   ['DatasetSourceName', 'DatasetType', 'FREQUENCY','frequency']]
                    id_field_name = [f.name for f in arcpy.ListFields(temp_ecoshape_countby_source) if f.aliasName ==
                                     'EcoshapeID'][0]
                    with arcpy.da.SearchCursor(temp_ecoshape_countby_source, field_names,
                                               id_field_name + ' = ' + str(update_row['EcoshapeID'])) as search_cursor:
                        summary = ''
                        presence = update_row['Presence']
                        for search_row in EBARUtils.searchCursor(search_cursor):
                            if len(summary) == 0:
                                summary = 'Input records - '
                            else:
                                summary += ', '
                            summary += str(search_row[field_names[2]]) + ' ' + search_row[field_names[0]]
                            # high-grade Presence Expected to Present for some dataset sources
                            if presence == 'X' and (search_row[field_names[1]] in
                                                    ('Element Occurrences', 'Source Features', 'Species Observations',
                                                     'Critical Habitat')):
                                presence = 'P'
                        if summary != '':
                            del search_row
                    update_cursor.updateRow([update_row['EcoshapeID'], presence, summary])
            del update_row
        # loop add review records
        add = False
        if len(prev_range_map_ids) > 0:
            with arcpy.da.SearchCursor('ecoshape_review_view', [table_name_prefix + 'EcoshapeReview.EcoshapeID'],
                                        table_name_prefix + 'Review.RangeMapID IN (' + \
                                            prev_range_map_ids + ') AND ' + table_name_prefix + \
                                            'EcoshapeReview.UseForMapGen = 1 AND ' + table_name_prefix + \
                                            "EcoshapeReview.AddRemove = '1'") as search_cursor:
                search_row = None
                for search_row in EBARUtils.searchCursor(search_cursor):
                    # check for ecoshape
                    add = True
                    with arcpy.da.UpdateCursor(param_geodatabase + '/RangeMapEcoshape', ['EcoshapeID'],
                                               'RangeMapID = ' + str(range_map_id) + ' AND EcoshapeID = ' + \
                                                   str(search_row[table_name_prefix + \
                                                   'EcoshapeReview.EcoshapeID'])) as update_cursor:
                        for update_row in EBARUtils.updateCursor(update_cursor):
                            add = False
                    if not add:
                        del update_row
                    else:
                        ecoshape_reviews += 1
                        with arcpy.da.InsertCursor(param_geodatabase + '/RangeMapEcoshape',
                                                   ['RangeMapID', 'EcoshapeID', 'Presence',
                                                    'RangeMapEcoshapeNotes']) as insert_cursor:
                            insert_cursor.insertRow([range_map_id,
                                                     search_row[table_name_prefix + 'EcoshapeReview.EcoshapeID'], 'X',
                                                     'Expert Ecoshape Review'])
                if search_row:
                    del search_row
        EBARUtils.setNewID(param_geodatabase + '/RangeMapEcoshape', 'RangeMapEcoshapeID',
                           'RangeMapID = ' + str(range_map_id))

        # create RangeMapEcoshapeInputDataset records based on summary
        EBARUtils.displayMessage(messages, 'Creating Range Map Ecoshape Input Dataset records')
        with arcpy.da.InsertCursor(param_geodatabase + '/RangeMapEcoshapeInputDataset',
                                   ['RangeMapEcoshapeID', 'InputDatasetID', 'InputDataSummary']) as insert_cursor:
            with arcpy.da.SearchCursor(param_geodatabase + '/RangeMapEcoshape', ['RangeMapEcoshapeID', 'EcoshapeID'],
                                       'RangeMapID = ' + str(range_map_id)) as rme_cursor:
                for rme_row in EBARUtils.searchCursor(rme_cursor):
                    with arcpy.da.SearchCursor(temp_ecoshape_countby_dataset,
                                               ['EcoshapeID', 'InputDatasetID', 'FREQUENCY']) as search_cursor:
                        for row in EBARUtils.searchCursor(search_cursor):
                            summary = str(row['FREQUENCY']) + ' input record(s)'
                            insert_cursor.insertRow([rme_row['RangeMapEcoshapeID'], row['InputDatasetID'], summary])
                        del row
                del rme_row
        with arcpy.da.SearchCursor(param_geodatabase + '/RangeMapEcoshape', ['RangeMapEcoshapeID'],
                                   'RangeMapID = ' + str(range_map_id)) as rme_cursor:
            for rme_row in EBARUtils.searchCursor(rme_cursor):
                EBARUtils.setNewID(param_geodatabase + '/RangeMapEcoshapeInputDataset',
                                   'RangeMapEcoshpInputDatasetID',
                                   'RangeMapEcoshapeID = ' + str(rme_row['RangeMapEcoshapeID']))
            del rme_row

        # get overall input counts by source (using original inputs)
        EBARUtils.displayMessage(messages, 'Counting overall inputs by Dataset Source')
        # select only those within ecoshapes
        arcpy.AddJoin_management('all_inputs_layer', 'InputDatasetID',
                                 param_geodatabase + '/InputDataset', 'InputDatasetID', 'KEEP_COMMON')
        arcpy.AddJoin_management('all_inputs_layer', 'DatasetSourceID',
                                 param_geodatabase + '/DatasetSource', 'DatasetSourceID', 'KEEP_COMMON')
        arcpy.SelectLayerByLocation_management('all_inputs_layer', 'INTERSECT', param_geodatabase + '/Ecoshape')
        temp_overall_countby_source = 'TempOverallCountBySource' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.Statistics_analysis('all_inputs_layer', temp_overall_countby_source, [['InputDatasetID', 'COUNT']],
                                  [table_name_prefix + 'DatasetSource.DatasetSourceName'])

        # get synonyms used
        EBARUtils.displayMessage(messages, 'Documenting Synonyms used')
        temp_unique_synonyms = 'TempUniqueSynonyms' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.Statistics_analysis('all_inputs_layer', temp_unique_synonyms, [['InputDatasetID', 'COUNT']],
                                  [table_name_prefix + temp_all_inputs + '.SynonymID'])
        arcpy.RemoveJoin_management('all_inputs_layer', table_name_prefix + 'DatasetSource')
        arcpy.RemoveJoin_management('all_inputs_layer', table_name_prefix + 'InputDataset')
        # build list of unique IDs
        synonym_ids = []
        # kludge because arc ends up with different field names under Enterprise gdb after joining
        id_field_name = [f.name for f in arcpy.ListFields(temp_unique_synonyms) if f.aliasName in ['SynonymID']][0]
        with arcpy.da.SearchCursor(temp_unique_synonyms, [id_field_name]) as search_cursor:
            for search_row in EBARUtils.searchCursor(search_cursor):
                if search_row[id_field_name]:
                    if search_row[id_field_name] not in synonym_ids:
                        synonym_ids.append(search_row[id_field_name])
                del search_row
        # get synonym names for IDs and combine with secondary names
        if len(synonym_ids) > 0:
            with arcpy.da.SearchCursor(param_geodatabase + '/Synonym', ['SynonymName', 'SHORT_CITATION_AUTHOR',
                                                                        'SHORT_CITATION_YEAR'],
                                       'SynonymID IN (' + ','.join(map(str, synonym_ids)) + ')') as search_cursor:
                found = False
                for search_row in EBARUtils.searchCursor(search_cursor):
                    found = True
                    if len(secondary_names) > 0:
                        secondary_names += ', '
                    secondary_names += search_row['SynonymName']
                    if search_row['SHORT_CITATION_AUTHOR']:
                        secondary_names += ' (' + search_row['SHORT_CITATION_AUTHOR']
                        if search_row['SHORT_CITATION_YEAR']:
                            secondary_names += ', ' + str(int(search_row['SHORT_CITATION_YEAR']))
                        secondary_names += ')'
                if found:
                    del search_row

        # update RangeMap date and metadata
        EBARUtils.displayMessage(messages, 'Updating Range Map record with overall summary')
        with arcpy.da.UpdateCursor('range_map_view', ['RangeDate', 'RangeMetadata', 'RangeMapNotes'],
                                   'RangeMapID = ' + str(range_map_id)) as update_cursor:
            for update_row in update_cursor:
                # kludge because arc ends up with different field names under Enterprise gdb after joining
                field_names = [f.name for f in arcpy.ListFields(temp_overall_countby_source) if f.aliasName in
                               ['DatasetSourceName','FREQUENCY','frequency']]
                with arcpy.da.SearchCursor(temp_overall_countby_source, field_names) as search_cursor:
                    summary = ''
                    for search_row in EBARUtils.searchCursor(search_cursor):
                        if len(summary) == 0:
                            summary = 'Input records - '
                        else:
                            summary += ', '
                        summary += str(search_row[field_names[1]]) + ' ' + search_row[field_names[0]]
                if ecoshape_reviews > 0:
                    if len(summary) > 0:
                        summary += '; '
                    summary += 'Expert Ecoshape Reviews - ' + str(ecoshape_reviews)
                    del search_row
                notes = 'Primary Species - ' + param_species
                if len(secondary_names) > 0:
                    notes += '; Synonyms - ' + secondary_names
                if additional_input_records > 0:
                    notes += '; Additional Input Records - ' + str(additional_input_records)
                update_cursor.updateRow([datetime.datetime.now(), summary, notes])

        # generate TOC entry and actual map!!!

        # temp clean-up
        if arcpy.Exists(temp_unique_synonyms):
            arcpy.Delete_management(temp_unique_synonyms)
        if arcpy.Exists(temp_overall_countby_source):
            arcpy.Delete_management(temp_overall_countby_source)
        if arcpy.Exists(temp_ecoshape_countby_source):
            arcpy.Delete_management(temp_ecoshape_countby_source)
        if arcpy.Exists(temp_ecoshape_countby_dataset):
            arcpy.Delete_management(temp_ecoshape_countby_dataset)
        if arcpy.Exists(temp_ecoshape_max_polygon):
            arcpy.Delete_management(temp_ecoshape_max_polygon)
        if arcpy.Exists(temp_pairwise_intersect):
            arcpy.Delete_management(temp_pairwise_intersect)
        if arcpy.Exists(temp_line_buffer):
            arcpy.Delete_management(temp_line_buffer)
        if arcpy.Exists(temp_point_buffer):
            arcpy.Delete_management(temp_point_buffer)
        ## trouble deleting on server only due to locks; could be layer?
        #if arcpy.Exists(temp_all_inputs):
        #    arcpy.Delete_management(temp_all_inputs)

        # end time
        end_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'End time: ' + str(end_time))
        elapsed_time = end_time - start_time
        EBARUtils.displayMessage(messages, 'Elapsed time: ' + str(elapsed_time))
        return
            

# controlling process
if __name__ == '__main__':
    grm = GenerateRangeMapTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:/GIS/EBAR/EBAR-KBA-Dev.gdb'
    param_species = arcpy.Parameter()
    param_species.value = 'Crataegus okennonii'
    param_secondary = arcpy.Parameter()
    param_secondary.value = None
    #param_secondary.value = "'Dodia verticalis'"
    #param_secondary.value = "'Dodia tarandus';'Dodia verticalis'"
    param_version = arcpy.Parameter()
    param_version.value = '0.99'
    param_stage = arcpy.Parameter()
    param_stage.value = 'Auto-generated'
    parameters = [param_geodatabase, param_species, param_secondary, param_version, param_stage]
    grm.RunGenerateRangeMapTool(parameters, None)
