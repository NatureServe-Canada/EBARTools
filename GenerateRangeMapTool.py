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

    def runGenerateRangeMapTool(self, parameters, messages):
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
        EBARUtils.displayMessage(messages, 'Species Scientific Name: ' + param_species)
        param_secondary = parameters[2].valueAsText
        if param_secondary:
            EBARUtils.displayMessage(messages, 'Secondary Species: ' + param_secondary)
            param_secondary = param_secondary.replace("'", '')
            param_secondary = param_secondary.split(';')
        param_version = parameters[3].valueAsText
        EBARUtils.displayMessage(messages, 'Range Version: ' + param_version)
        param_stage = parameters[4].valueAsText
        EBARUtils.displayMessage(messages, 'Range Stage: ' + param_stage)
        param_scope = parameters[5].valueAsText
        national_jur_ids = None
        scope = None
        if param_scope:
            EBARUtils.displayMessage(messages, 'Scope: ' + param_scope)
            if param_scope == 'Canadian':
                national_jur_ids = '(1,2,3,4,5,6,7,8,9,10,11,12,13)'
                scope = 'N'
            if param_scope == 'Global':
                scope = 'G'
            if param_scope == 'North American':
                scope = 'A'

        # use passed geodatabase as workspace (still seems to go to default geodatabase)
        arcpy.env.workspace = param_geodatabase

        # get table name prefix (needed for joined tables and feature classes in enterprise geodatabases)
        table_name_prefix = EBARUtils.getTableNamePrefix(param_geodatabase)

        # check for species
        species_id, short_citation = EBARUtils.checkSpecies(param_species.lower(), param_geodatabase)
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
        synonyms_used = ''
        #additional_input_records = 0
        #excluded_input_records = 0
        if param_secondary:
            for secondary in param_secondary:
                secondary_id, short_citation = EBARUtils.checkSpecies(secondary.lower(), param_geodatabase)
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
                    synonyms_used += ', '
                secondary_names += secondary + short_citation
                synonyms_used += secondary

        # check for range map record and add if necessary
        EBARUtils.displayMessage(messages, 'Checking for existing Range Map')
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
                        # range map to be generated already exists
                        range_map_id = row['RangeMapID']
                        # remove from list of range maps to be used later for applying reviews
                        prev_range_map.remove(range_map_id)
                    if row['RangeVersion'] != param_version:
                        # also remove from list of range maps to be used later for applying reviews
                        prev_range_map.remove(row['RangeMapID'])
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
                EBARUtils.displayMessage(messages, 'ERROR: Range Map already exists with completed Review(s)')
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
                    EBARUtils.displayMessage(messages, 'ERROR: Range Map already exists with Review(s) in progress')
                    # terminate with error
                    return
                    #raise arcpy.ExecuteError

                arcpy.RemoveJoin_management('range_map_view', table_name_prefix + 'EcoshapeReview')
            arcpy.RemoveJoin_management('range_map_view', table_name_prefix + 'Review')

            # check if published, and if so terminate
            with arcpy.da.SearchCursor('range_map_view', ['IncludeInDownloadTable', 'RangeMapScope']) as cursor:
                published = False
                for row in EBARUtils.searchCursor(cursor):
                    if (row['IncludeInDownloadTable'] in [1, 2, 3, 4]) and (row['RangeMapScope'] == scope):
                        published = True
                        break
                if published:
                    del row
            if published:
                EBARUtils.displayMessage(messages, 'ERROR: Range Map already published')
                # terminate with error
                return
                #raise arcpy.ExecuteError

            # no reviews completed or in progress, so delete any existing related records
            EBARUtils.displayMessage(messages, 'Range Map already exists with but with no Review(s) completed or in '
                                               'progress, so existing related records will be deleted')
            # consider replacing the following code blocks with select then Delete Rows tools
            with arcpy.da.SearchCursor(param_geodatabase + '/RangeMapEcoshape', ['RangeMapEcoshapeID'],
                                       'RangeMapID = ' + str(range_map_id)) as rme_cursor:
                for rme_row in EBARUtils.searchCursor(rme_cursor):
                    with arcpy.da.UpdateCursor(param_geodatabase + '/RangeMapEcoshapeInputDataset',
                                               ['RangeMapEcoshpInputDatasetID'],
                                                'RangeMapEcoshapeID = ' + \
                                                str(rme_row['RangeMapEcoshapeID'])) as rmeid_cursor:
                        rmeid_row = None
                        for rmeid_row in EBARUtils.updateCursor(rmeid_cursor):
                            rmeid_cursor.deleteRow()
                        if rmeid_row:
                            del rmeid_row
            with arcpy.da.UpdateCursor(param_geodatabase + '/RangeMapEcoshape', ['RangeMapEcoshapeID'],
                                       'RangeMapID = ' + str(range_map_id)) as rme_cursor:
                rme_row = None
                for rme_row in EBARUtils.updateCursor(rme_cursor):
                    rme_cursor.deleteRow()
                if rme_row:
                    del rme_row
                    EBARUtils.displayMessage(messages, 'Existing Range Map Ecoshape records deleted')
            with arcpy.da.UpdateCursor(param_geodatabase + '/SecondarySpecies', ['SecondarySpeciesID'],
                                       'RangeMapID = ' + str(range_map_id)) as es_cursor:
                es_row = None
                for es_row in EBARUtils.updateCursor(es_cursor):
                    es_cursor.deleteRow()
                if es_row:
                    del es_row
                    EBARUtils.displayMessage(messages, 'Existing Secondary Species records deleted')
            with arcpy.da.UpdateCursor(param_geodatabase + '/RangeMapInput', ['OBJECTID'],
                                       'RangeMapID = ' + str(range_map_id)) as rmi_cursor:
                rmi_row = None
                for rmi_row in EBARUtils.updateCursor(rmi_cursor):
                    rmi_cursor.deleteRow()
                if rmi_row:
                    del rmi_row
                    EBARUtils.displayMessage(messages, 'Existing Range Map Input records deleted')

        else:
            arcpy.SelectLayerByAttribute_management('range_map_view', 'CLEAR_SELECTION')
            # create RangeMap record
            with arcpy.da.InsertCursor('range_map_view',
                                       ['SpeciesID', 'RangeVersion', 'RangeStage', 'RangeDate', 'RangeMapNotes',
                                        'IncludeInEBARReviewer', 'RangeMapScope', 'SynonymsUsed']) as cursor:
                notes = 'Primary Species Name - ' + param_species
                if len(secondary_names) > 0:
                    notes += '; Synonyms - ' + secondary_names
                object_id = cursor.insertRow([species_id, param_version, param_stage, datetime.datetime.now(),
                                              notes, 0, scope, synonyms_used])
            range_map_id = EBARUtils.getUniqueID(param_geodatabase + '/RangeMap', 'RangeMapID', object_id)
            EBARUtils.displayMessage(messages, 'Range Map record created')
            # create SecondarySpecies records
            if param_secondary:
                with arcpy.da.InsertCursor(param_geodatabase + '/SecondarySpecies',
                                           ['RangeMapID', 'SpeciesID']) as cursor:
                    for secondary in param_secondary:
                        secondary_id, short_citation = EBARUtils.checkSpecies(secondary, param_geodatabase)
                        cursor.insertRow([range_map_id, secondary_id])
                EBARUtils.displayMessage(messages, 'Secondary Species records created')

        # select all points for species and buffer
        EBARUtils.displayMessage(messages, 'Buffering Input Points')
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/InputPoint', 'input_point_layer')
        # select any from secondary inputs (chicken and egg - RangeMapID must already exist!)
        arcpy.AddJoin_management('input_point_layer', 'InputPointID', param_geodatabase + '/SecondaryInput',
                                 'InputPointID')
        arcpy.SelectLayerByAttribute_management('input_point_layer', 'NEW_SELECTION',
                                                table_name_prefix + 'SecondaryInput.RangeMapID = ' + str(range_map_id))
        arcpy.RemoveJoin_management('input_point_layer', table_name_prefix + 'SecondaryInput')
        # add "real" points to selection based on type
        arcpy.AddJoin_management('input_point_layer', 'InputDatasetID',
                                 param_geodatabase + '/InputDataset', 'InputDatasetID', 'KEEP_COMMON')
        arcpy.AddJoin_management('input_point_layer', 'DatasetSourceID',
                                 param_geodatabase + '/DatasetSource', 'DatasetSourceID', 'KEEP_COMMON')
        where_clause = table_name_prefix + 'InputPoint.SpeciesID IN (' + species_ids + ') AND (' + \
                       table_name_prefix + 'InputPoint.Accuracy IS NULL OR ' + table_name_prefix + \
                       'InputPoint.Accuracy <= ' + str(EBARUtils.worst_accuracy) + ') AND ((' + \
                       table_name_prefix + "DatasetSource.DatasetType IN ('Element Occurrences', 'Source Features'," + \
                       " 'Species Observations') AND " + table_name_prefix + 'InputPoint.MaxDate IS NOT NULL) OR (' + \
                       table_name_prefix + "DatasetSource.DatasetType IN ('Critical Habitat', 'Range Estimate'," + \
                       " 'Habitat Suitabilty')))"
        arcpy.SelectLayerByAttribute_management('input_point_layer', 'ADD_TO_SELECTION', where_clause)
        arcpy.RemoveJoin_management('input_point_layer', table_name_prefix + 'DatasetSource')
        arcpy.RemoveJoin_management('input_point_layer', table_name_prefix + 'InputDataset')
        # remove excluded points from selection
        arcpy.AddJoin_management('input_point_layer', 'InputPointID', param_geodatabase + '/InputFeedback',
                                 'InputPointID')
        #arcpy.SelectLayerByAttribute_management('input_point_layer', 'REMOVE_FROM_SELECTION',
        #                                        table_name_prefix + 'InputFeedback.ExcludeFromRangeMaps = 1')
        arcpy.SelectLayerByAttribute_management('input_point_layer', 'REMOVE_FROM_SELECTION',
                                                table_name_prefix + 'InputFeedback.ExcludeFromRangeMapID = ' + \
                                                    str(range_map_id))
        arcpy.SelectLayerByAttribute_management('input_point_layer', 'REMOVE_FROM_SELECTION',
                                                table_name_prefix + 'InputFeedback.BadData = 1')
        arcpy.RemoveJoin_management('input_point_layer', table_name_prefix + 'InputFeedback')
        # add field for buffer
        EBARUtils.checkAddField('input_point_layer', 'buffer', 'LONG')
        code_block = '''
def GetBuffer(accuracy):
    ret = accuracy
    if not ret:
        ret = ''' + str(default_buffer_size) + '''
    elif ret <= 0:
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
        arcpy.RemoveJoin_management('input_line_layer', table_name_prefix + 'SecondaryInput')
        # add "real" lines to selection based on type
        arcpy.AddJoin_management('input_line_layer', 'InputDatasetID',
                                 param_geodatabase + '/InputDataset', 'InputDatasetID', 'KEEP_COMMON')
        arcpy.AddJoin_management('input_line_layer', 'DatasetSourceID',
                                 param_geodatabase + '/DatasetSource', 'DatasetSourceID', 'KEEP_COMMON')
        where_clause = table_name_prefix + 'InputLine.SpeciesID IN (' + species_ids + ') AND (' + \
                       table_name_prefix + 'InputLine.Accuracy IS NULL OR ' + table_name_prefix + \
                       'InputLine.Accuracy <= ' + str(EBARUtils.worst_accuracy) + ') AND ((' + \
                       table_name_prefix + "DatasetSource.DatasetType IN ('Element Occurrences', 'Source Features'," + \
                       " 'Species Observations') AND " + table_name_prefix + 'InputLine.MaxDate IS NOT NULL) OR (' + \
                       table_name_prefix + "DatasetSource.DatasetType IN ('Critical Habitat', 'Range Estimate'," + \
                       " 'Habitat Suitabilty')))"
        arcpy.SelectLayerByAttribute_management('input_line_layer', 'ADD_TO_SELECTION', where_clause)
        arcpy.RemoveJoin_management('input_line_layer', table_name_prefix + 'DatasetSource')
        arcpy.RemoveJoin_management('input_line_layer', table_name_prefix + 'InputDataset')
        # remove excluded lines from selection
        arcpy.AddJoin_management('input_line_layer', 'InputLineID', param_geodatabase + '/InputFeedback',
                                 'InputLineID')
        #arcpy.SelectLayerByAttribute_management('input_line_layer', 'REMOVE_FROM_SELECTION',
        #                                        table_name_prefix + 'InputFeedback.ExcludeFromRangeMaps = 1')
        arcpy.SelectLayerByAttribute_management('input_line_layer', 'REMOVE_FROM_SELECTION',
                                                table_name_prefix + 'InputFeedback.ExcludeFromRangeMapID = ' + \
                                                    str(range_map_id))
        arcpy.SelectLayerByAttribute_management('input_line_layer', 'REMOVE_FROM_SELECTION',
                                                table_name_prefix + 'InputFeedback.BadData = 1')
        arcpy.RemoveJoin_management('input_line_layer', table_name_prefix + 'InputFeedback')
        # buffer
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
        arcpy.RemoveJoin_management('input_polygon_layer', table_name_prefix + 'SecondaryInput')
        # add "real" polygons to selection based on type
        arcpy.AddJoin_management('input_polygon_layer', 'InputDatasetID',
                                 param_geodatabase + '/InputDataset', 'InputDatasetID', 'KEEP_COMMON')
        arcpy.AddJoin_management('input_polygon_layer', 'DatasetSourceID',
                                 param_geodatabase + '/DatasetSource', 'DatasetSourceID', 'KEEP_COMMON')
        where_clause = table_name_prefix + 'InputPolygon.SpeciesID IN (' + species_ids + ') AND (' + \
                       table_name_prefix + 'InputPolygon.Accuracy IS NULL OR ' + table_name_prefix + \
                       'InputPolygon.Accuracy <= ' + str(EBARUtils.worst_accuracy) + ') AND ((' + \
                       table_name_prefix + "DatasetSource.DatasetType IN ('Element Occurrences', 'Source Features'," + \
                       " 'Species Observations') AND " + table_name_prefix + 'InputPolygon.MaxDate IS NOT NULL) OR (' + \
                       table_name_prefix + "DatasetSource.DatasetType = 'Element Occurrences' AND " + \
                       table_name_prefix + 'InputPolygon.EORank IS NOT NULL) OR (' + table_name_prefix + \
                       "DatasetSource.DatasetType IN ('Critical Habitat', 'Range Estimate', 'Habitat Suitabilty')))"
        arcpy.SelectLayerByAttribute_management('input_polygon_layer', 'ADD_TO_SELECTION', where_clause)
        arcpy.RemoveJoin_management('input_polygon_layer', table_name_prefix + 'DatasetSource')
        arcpy.RemoveJoin_management('input_polygon_layer', table_name_prefix + 'InputDataset')
        # remove excluded lines from selection
        arcpy.AddJoin_management('input_polygon_layer', 'InputPolygonID', param_geodatabase + '/InputFeedback',
                                 'InputPolygonID')
        #arcpy.SelectLayerByAttribute_management('input_polygon_layer', 'REMOVE_FROM_SELECTION',
        #                                        table_name_prefix + 'InputFeedback.ExcludeFromRangeMaps = 1')
        arcpy.SelectLayerByAttribute_management('input_polygon_layer', 'REMOVE_FROM_SELECTION',
                                                table_name_prefix + 'InputFeedback.ExcludeFromRangeMapID = ' + \
                                                    str(range_map_id))
        arcpy.SelectLayerByAttribute_management('input_polygon_layer', 'REMOVE_FROM_SELECTION',
                                                table_name_prefix + 'InputFeedback.BadData = 1')
        arcpy.RemoveJoin_management('input_polygon_layer', table_name_prefix + 'InputFeedback')

        # merge buffer polygons and input polygons
        EBARUtils.displayMessage(messages, 'Merging Buffered Points and Lines and Input Polygons')
        temp_all_inputs = 'TempAllInputs' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.Merge_management([temp_point_buffer, temp_line_buffer, 'input_polygon_layer'], temp_all_inputs, None,
                               'ADD_SOURCE_INFO')
        EBARUtils.checkAddField(temp_all_inputs, 'RangeMapID', 'LONG')
        arcpy.CalculateField_management(temp_all_inputs, 'RangeMapID', range_map_id)
        EBARUtils.checkAddField(temp_all_inputs, 'OriginalGeometryType', 'TEXT')
        code_block = '''
def GetGeometryType(input_point_id, input_line_id, input_polygon_id):
    ret = 'P'
    if input_line_id:
        ret = 'L'
    elif input_polygon_id:
        ret = 'Y'
    return ret'''
        arcpy.CalculateField_management(temp_all_inputs, 'OriginalGeometryType',
                                        'GetGeometryType(!InputPointID!, !InputLineID!, !InputPolygonID!)', 'PYTHON3',
                                        code_block)
        EBARUtils.checkAddField(temp_all_inputs, 'TempDate', 'DATE')
        arcpy.CalculateField_management(temp_all_inputs, 'TempDate', '!MaxDate!', 'PYTHON3')
        arcpy.MakeFeatureLayer_management(temp_all_inputs, 'all_inputs_layer')

        # eo ranks, when available, override dates in determining historical (fake the date to accomplish this)
        EBARUtils.displayMessage(messages, 'Applying EO Ranks, where available, to determine historical records')
        result = arcpy.SelectLayerByAttribute_management('all_inputs_layer', 'NEW_SELECTION',
                                                         "EORank IN ('H', 'H?', 'X', 'X?')")
        if int(result[1]) > 0:
            # 1000 years in the past
            fake_date_expr = 'datetime.datetime(datetime.datetime.now().year - 1000, 1, 1)'
            arcpy.CalculateField_management('all_inputs_layer', 'TempDate', fake_date_expr)
        result = arcpy.SelectLayerByAttribute_management('all_inputs_layer', 'NEW_SELECTION',
                                                         'TempDate IS NULL AND EORank IS NOT NULL ' + \
                                                             "AND EORank NOT IN (' ', 'H', 'H?', 'X', 'X?')")
                                                             #"AND EORank NOT IN (' ', 'F', 'F?', 'H', 'H?', 'NR', " + \
                                                             #"'U', 'X', 'X?,')")
        if int(result[1]) > 0:
            # 1000 years in the future
            fake_date_expr = 'datetime.datetime(datetime.datetime.now().year + 1000, 1, 1)'
            arcpy.CalculateField_management('all_inputs_layer', 'TempDate', fake_date_expr)
        arcpy.SelectLayerByAttribute_management('all_inputs_layer', 'CLEAR_SELECTION')

        # pairwise intersect buffers and ecoshape polygons
        EBARUtils.displayMessage(messages, 'Pairwise Intersecting All Inputs with Ecoshapes')
        if national_jur_ids:
            arcpy.MakeFeatureLayer_management(param_geodatabase + '/Ecoshape', 'ecoshape_layer',
                                              'JurisdictionID IN ' + national_jur_ids)
        else:
            arcpy.MakeFeatureLayer_management(param_geodatabase + '/Ecoshape', 'ecoshape_layer')
        temp_pairwise_intersect = 'TempPairwiseIntersect' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.PairwiseIntersect_analysis(['all_inputs_layer',  'ecoshape_layer'], temp_pairwise_intersect)
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
        #                          [['PolygonPropn', 'MAX'], ['TempDate', 'MAX']], 'EcoshapeID')

        # get max date by type per ecoshape
        EBARUtils.displayMessage(messages, 'Determining Maximum Date per Ecoshape and DatasetType')
        temp_ecoshape_max_polygon = 'TempEcoshapeMaxPolygon' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.AddJoin_management('pairwise_intersect_layer', 'InputDatasetID',
                                 param_geodatabase + '/InputDataset', 'InputDatasetID', 'KEEP_COMMON')
        arcpy.AddJoin_management('pairwise_intersect_layer', 'DatasetSourceID',
                                 param_geodatabase + '/DatasetSource', 'DatasetSourceID', 'KEEP_COMMON')
        arcpy.Statistics_analysis('pairwise_intersect_layer', temp_ecoshape_max_polygon,
                                  [['TempDate', 'MAX']], [table_name_prefix + temp_pairwise_intersect + '.EcoshapeID',
                                                         table_name_prefix + 'DatasetSource.DatasetType'])
        arcpy.RemoveJoin_management('pairwise_intersect_layer', table_name_prefix + 'DatasetSource')
        arcpy.RemoveJoin_management('pairwise_intersect_layer', table_name_prefix + 'InputDataset')

        # create RangeMapEcoshape records based on dataset type and max date #and proportion overlap 
        EBARUtils.displayMessage(messages, 'Creating Range Map Ecoshape records based on DatasetType and Maximum Date')
        with arcpy.da.InsertCursor(param_geodatabase + '/RangeMapEcoshape',
                                   ['RangeMapID', 'EcoshapeID', 'Presence']) as insert_cursor:
            input_found = False
            #with arcpy.da.SearchCursor(temp_ecoshape_max_polygon,
            #                           ['EcoshapeID', 'MAX_PolygonPropn', 'MAX_TempDate']) as search_cursor:
            #with arcpy.da.SearchCursor(temp_ecoshape_max_polygon,
            #                           [temp_pairwise_intersect + '_EcoshapeID', 'DatasetSource_DatasetType',
            #                            'MAX_' + temp_pairwise_intersect + '_TempDate'],
            #                            sql_clause=(None, 'ORDER BY ' + temp_pairwise_intersect + \
            #                                '_EcoshapeID')) as search_cursor:
            # kludge because arc ends up with different field names under Enterprise gdb after joining
            field_names = [f.name for f in arcpy.ListFields(temp_ecoshape_max_polygon) if f.aliasName in
                            ['EcoshapeID', 'DatasetType',
                             'MAX_' + table_name_prefix + temp_pairwise_intersect + '.tempdate',
                             'MAX_' + table_name_prefix + temp_pairwise_intersect + '.TempDate']]
            id_field_name = [f.name for f in arcpy.ListFields(temp_ecoshape_max_polygon) if f.aliasName ==
                             'EcoshapeID'][0]
            with arcpy.da.SearchCursor(temp_ecoshape_max_polygon, field_names,
                                       sql_clause=(None, 'ORDER BY ' + id_field_name)) as search_cursor:
                ecoshape_id = None
                # start at "lowest" level
                presence = 'H'
                for row in EBARUtils.searchCursor(search_cursor):
                    input_found = True
                    if ecoshape_id:
                        if row[field_names[0]] != ecoshape_id:
                            # save previous ecoshape
                            insert_cursor.insertRow([range_map_id, ecoshape_id, presence])
                            # start new ecoshape
                            ecoshape_id = None
                            presence = 'H'
                    ecoshape_id = row[field_names[0]]
                    # only check for "upgrades"
                    if row[field_names[1]] in ['Habitat Suitability', 'Range Estimate']:
                        if presence == 'H':
                            presence = 'X'
                    if row[field_names[2]]:
                        if ((row[field_names[1]] == 'Critical Habitat') or
                            (row[field_names[1]] in ['Element Occurrences', 'Source Features',
                                                     'Species Observations'] and
                             (datetime.datetime.now().year - row[field_names[2]].year)
                             <= age_for_historical)):
                            if presence in ['H', 'X']:
                                presence = 'P'
                if input_found:
                    # save final ecoshape
                    insert_cursor.insertRow([range_map_id, ecoshape_id, presence])
                    del row
        if not input_found:
            EBARUtils.displayMessage(messages, 'WARNING: No inputs/buffers overlap ecoshapes')
            ## terminate
            #return

        # get ecoshape input counts by dataset
        EBARUtils.displayMessage(messages, 'Counting Ecoshape Inputs by Dataset')
        temp_ecoshape_countby_dataset = 'TempEcoshapeCountByDataset' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.Statistics_analysis('pairwise_intersect_layer', temp_ecoshape_countby_dataset,
                                  [['InputPointID', 'COUNT']], ['EcoshapeID', 'InputDatasetID'])

        ## get ecoshape input counts by source and restricted input counts
        #EBARUtils.displayMessage(messages, 'Counting Ecoshape Inputs by Dataset Source and Restricted Inputs')
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
        #temp_ecoshape_restricted = 'TempEcoshapeRestricted' + str(start_time.year) + str(start_time.month) + \
        #    str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        #arcpy.SelectLayerByAttribute_management('pairwise_intersect_layer', 'NEW_SELECTION',
        #                                        table_name_prefix + "InputDataset.Restrictions IN ('R', 'E')")
        #arcpy.Statistics_analysis('pairwise_intersect_layer', temp_ecoshape_restricted, [['InputPointID', 'COUNT']],
        #                          ['EcoshapeID'])
        #arcpy.SelectLayerByAttribute_management('pairwise_intersect_layer', 'CLEAR_SELECTION')
        arcpy.RemoveJoin_management('pairwise_intersect_layer', table_name_prefix + 'DatasetSource')
        arcpy.RemoveJoin_management('pairwise_intersect_layer', table_name_prefix + 'InputDataset')

        # apply Reviews and summaries to RangeMapEcoshape records
        EBARUtils.displayMessage(messages,
                                 'Applying Reviews and summaries to Range Map Ecoshape records')
        #ecoshape_reviews = 0
        if len(prev_range_map_ids) > 0:
            arcpy.MakeTableView_management(param_geodatabase + '/EcoshapeReview', 'ecoshape_review_view')
            arcpy.AddJoin_management('ecoshape_review_view', 'EcoshapeID', param_geodatabase + '/Ecoshape', 'EcoshapeID')
            arcpy.AddJoin_management('ecoshape_review_view', 'ReviewID', param_geodatabase + '/Review', 'ReviewID')
        # loop existing range map ecoshapes
        with arcpy.da.UpdateCursor(param_geodatabase + '/RangeMapEcoshape',
                                   ['EcoshapeID', 'Presence', 'RangeMapEcoshapeNotes', 'MigrantStatus'],
                                   'RangeMapID = ' + str(range_map_id)) as update_cursor:
            update_row = None
            for update_row in EBARUtils.updateCursor(update_cursor):
                # check for ecoshape "remove" reviews
                remove = False
                if len(prev_range_map_ids) > 0:
                    with arcpy.da.SearchCursor('ecoshape_review_view', [table_name_prefix + 'EcoshapeReview.OBJECTID'],
                                               table_name_prefix + 'Review.RangeMapID IN (' + \
                                               prev_range_map_ids + ') AND ' + table_name_prefix + \
                                               'Review.UseForMapGen = 1 AND ' + table_name_prefix + \
                                               'EcoshapeReview.UseForMapGen = 1 AND ' + table_name_prefix + \
                                               "EcoshapeReview.Markup = 'R' AND "  + table_name_prefix + \
                                               'EcoshapeReview.EcoshapeID = ' + \
                                               str(update_row['EcoshapeID'])) as search_cursor:
                        for search_row in EBARUtils.searchCursor(search_cursor):
                            #ecoshape_reviews += 1
                            remove = True
                if remove:
                    del search_row
                    update_cursor.deleteRow()
                else:
                    # update
                    # kludge because arc ends up with different field names under Enterprise gdb after joining
                    field_names = [f.name for f in arcpy.ListFields(temp_ecoshape_countby_source) if f.aliasName in
                                   ['DatasetSourceName', 'DatasetType', 'FREQUENCY', 'frequency']]
                    id_field_name = [f.name for f in arcpy.ListFields(temp_ecoshape_countby_source) if f.aliasName ==
                                     'EcoshapeID'][0]
                    with arcpy.da.SearchCursor(temp_ecoshape_countby_source, field_names,
                                               id_field_name + ' = ' + str(update_row['EcoshapeID'])) as search_cursor:
                        summary = ''
                        presence = update_row['Presence']
                        migrant_status = update_row['MigrantStatus']
                        for search_row in EBARUtils.searchCursor(search_cursor):
                            if len(summary) > 0:
                                summary += ', '
                            summary += str(search_row[field_names[2]]) + ' ' + search_row[field_names[0]]
                        if len(summary) > 0:
                            del search_row
                    ## get restricted count
                    ## kludge because arc ends up with different field names under Enterprise gdb after joining
                    #field_names = [f.name for f in arcpy.ListFields(temp_ecoshape_restricted) if f.aliasName in
                    #               ['FREQUENCY', 'frequency']]
                    #id_field_name = [f.name for f in arcpy.ListFields(temp_ecoshape_restricted) if f.aliasName ==
                    #                 'EcoshapeID'][0]
                    #restricted = 0
                    #with arcpy.da.SearchCursor(temp_ecoshape_restricted, field_names,
                    #                           id_field_name + ' = ' + str(update_row['EcoshapeID'])) as search_cursor:
                    #    for search_row in EBARUtils.searchCursor(search_cursor):
                    #        restricted = search_row[field_names[0]]
                    #    if restricted > 0:
                    #        del search_row
                    #        summary = 'Input records (' + str(restricted) + ' RESTRICTED) - ' + summary
                    #    else:
                    #        summary = 'Input records - ' + summary
                    summary = 'Input records - ' + summary
                    # check for ecoshape "update" reviews
                    if len(prev_range_map_ids) > 0:
                        with arcpy.da.SearchCursor('ecoshape_review_view',
                                                   [table_name_prefix + 'EcoshapeReview.Markup',
                                                    table_name_prefix + 'EcoshapeReview.MigrantStatus'],
                                                   table_name_prefix + 'Review.RangeMapID IN (' + \
                                                   prev_range_map_ids + ') AND ' + table_name_prefix + \
                                                   'Review.UseForMapGen = 1 AND ' + table_name_prefix + \
                                                   'EcoshapeReview.UseForMapGen = 1 AND ' + table_name_prefix + \
                                                   "EcoshapeReview.Markup IN ('P', 'X', 'H') AND "  + table_name_prefix + \
                                                   'EcoshapeReview.EcoshapeID = ' + \
                                                   str(update_row['EcoshapeID'])) as search_cursor:
                            search_row = None
                            for search_row in EBARUtils.searchCursor(search_cursor):
                                #ecoshape_reviews += 1
                                presence = search_row[table_name_prefix + 'EcoshapeReview.Markup']
                                migrant_status = search_row[table_name_prefix + 'EcoshapeReview.MigrantStatus']
                            if search_row:
                                del search_row
                    update_cursor.updateRow([update_row['EcoshapeID'], presence, summary, migrant_status])
            if update_row:
                del update_row
        # loop review records and check for need to add
        if len(prev_range_map_ids) > 0:
            condition = table_name_prefix + 'Review.RangeMapID IN (' + \
                prev_range_map_ids + ') AND ' + table_name_prefix + \
                'Review.UseForMapGen = 1 AND ' + table_name_prefix + \
                'EcoshapeReview.UseForMapGen = 1 AND ' + table_name_prefix + \
                "EcoshapeReview.Markup IN ('P', 'X', 'H')"
            if scope == 'N':
                condition += ' AND ' + table_name_prefix + 'Ecoshape.JurisdictionID IN ' + national_jur_ids
            with arcpy.da.SearchCursor('ecoshape_review_view',
                                       [table_name_prefix + 'EcoshapeReview.EcoshapeID',
                                        table_name_prefix + 'EcoshapeReview.Markup',
                                        table_name_prefix + 'EcoshapeReview.MigrantStatus'],
                                       condition) as search_cursor:
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
                        #ecoshape_reviews += 1
                        with arcpy.da.InsertCursor(param_geodatabase + '/RangeMapEcoshape',
                                                   ['RangeMapID', 'EcoshapeID', 'Presence',
                                                    'RangeMapEcoshapeNotes', 'MigrantStatus']) as insert_cursor:
                            insert_cursor.insertRow([range_map_id,
                                                     search_row[table_name_prefix + 'EcoshapeReview.EcoshapeID'],
                                                     search_row[table_name_prefix + 'EcoshapeReview.Markup'],
                                                     'Expert Ecoshape Review',
                                                     search_row[table_name_prefix + 'EcoshapeReview.MigrantStatus']])
                if search_row:
                    del search_row

        # create RangeMapEcoshapeInputDataset records based on summary
        EBARUtils.displayMessage(messages, 'Creating Range Map Ecoshape Input Dataset records')
        with arcpy.da.SearchCursor(param_geodatabase + '/RangeMapEcoshape', ['RangeMapEcoshapeID', 'EcoshapeID'],
                                   'RangeMapID = ' + str(range_map_id)) as rme_cursor:
            rme_row = None
            for rme_row in EBARUtils.searchCursor(rme_cursor):
                with arcpy.da.SearchCursor(temp_ecoshape_countby_dataset,
                                            ['EcoshapeID', 'InputDatasetID', 'FREQUENCY'],
                                            'EcoshapeID = ' + str(rme_row['EcoshapeID'])) as search_cursor:
                    row = None
                    for row in EBARUtils.searchCursor(search_cursor):
                        summary = str(row['FREQUENCY']) + ' input record(s)'
                        with arcpy.da.InsertCursor(param_geodatabase + '/RangeMapEcoshapeInputDataset',
                                                   ['RangeMapEcoshapeID', 'InputDatasetID',
                                                    'InputDataSummary']) as insert_cursor:
                            insert_cursor.insertRow([rme_row['RangeMapEcoshapeID'], row['InputDatasetID'], summary])
                    if row:
                        del row
            if rme_row:
                del rme_row

        ## get overall input counts by source and restricted input counts (using original inputs)
        #EBARUtils.displayMessage(messages, 'Counting Overall Inputs by Dataset Source and Restricted Inputs')
        # get overall input counts by source
        EBARUtils.displayMessage(messages, 'Counting Overall Inputs by Dataset Source')
        # select only those within ecoshapes
        arcpy.AddJoin_management('all_inputs_layer', 'InputDatasetID',
                                 param_geodatabase + '/InputDataset', 'InputDatasetID', 'KEEP_COMMON')
        arcpy.AddJoin_management('all_inputs_layer', 'DatasetSourceID',
                                 param_geodatabase + '/DatasetSource', 'DatasetSourceID', 'KEEP_COMMON')
        arcpy.SelectLayerByLocation_management('all_inputs_layer', 'INTERSECT', 'ecoshape_layer')
        temp_overall_countby_source = 'TempOverallCountBySource' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.Statistics_analysis('all_inputs_layer', temp_overall_countby_source, [['InputDatasetID', 'COUNT']],
                                  [table_name_prefix + 'DatasetSource.DatasetSourceName'])
        #temp_overall_restricted = 'TempOverallRestricted' + str(start_time.year) + str(start_time.month) + \
        #    str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        #arcpy.Statistics_analysis('all_inputs_layer', temp_overall_restricted, [['InputDatasetID', 'COUNT']],
        #                          [table_name_prefix + 'InputDataset.Restrictions'])

        # create RangeMapInput records from Non-restricted for overlay display in EBAR Reviewer
        EBARUtils.displayMessage(messages, 'Creating Range Map Input records for overlay display in EBAR Reviewer')
        temp_restrictions = 'TempRestrictions' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.TableToTable_conversion(param_geodatabase + '/RestrictedJurisdictionSpecies', param_geodatabase,
                                      temp_restrictions, 'SpeciesID IN (' + species_ids + ')')
        arcpy.AddJoin_management('all_inputs_layer', table_name_prefix + 'DatasetSource.CDCJurisdictionID',
                                 param_geodatabase + '/' + temp_restrictions, 'CDCJurisdictionID', 'KEEP_ALL')
        arcpy.SelectLayerByAttribute_management('all_inputs_layer', 'SUBSET_SELECTION',
                                                '(' + table_name_prefix + "InputDataset.Restrictions = 'N') OR" +
                                                '(' + table_name_prefix + "InputDataset.Restrictions = 'R' AND " +
                                                table_name_prefix + "DatasetSource.RestrictionBySpecies = 1 AND " +
                                                table_name_prefix + "DatasetSource.CDCJurisdictionID IS NOT NULL AND " +
                                                table_name_prefix + temp_restrictions + '.SpeciesID IS NULL)')
        arcpy.AddJoin_management('all_inputs_layer', 'SpeciesID',
                                 param_geodatabase + '/BIOTICS_ELEMENT_NATIONAL', 'SpeciesID', 'KEEP_COMMON')
        arcpy.AddJoin_management('all_inputs_layer', 'SynonymID',
                                 param_geodatabase + '/Synonym', 'SynonymID', 'KEEP_ALL')
        field_mappings = arcpy.FieldMappings()
        field_mappings.addFieldMap(EBARUtils.createFieldMap('all_inputs_layer',
                                                            table_name_prefix + temp_all_inputs + '.RangeMapID',
                                                            'RangeMapID', 'LONG'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap('all_inputs_layer', table_name_prefix + \
                                                            temp_all_inputs + '.OriginalGeometryType',
                                                            'OriginalGeometryType', 'TEXT'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap('all_inputs_layer', table_name_prefix + \
                                                            'BIOTICS_ELEMENT_NATIONAL.NATIONAL_SCIENTIFIC_NAME',
                                                            'NationalScientificName', 'TEXT'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap('all_inputs_layer',
                                                            table_name_prefix + 'Synonym.SynonymName',
                                                            'SynonymName', 'TEXT'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap('all_inputs_layer',
                                                            table_name_prefix + 'DatasetSource.DatasetSourceName',
                                                            'DatasetSourceName', 'TEXT'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap('all_inputs_layer',
                                                            table_name_prefix + 'DatasetSource.DatasetType',
                                                            'DatasetType', 'TEXT'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap('all_inputs_layer',
                                                            table_name_prefix + temp_all_inputs + '.Accuracy',
                                                            'Accuracy', 'LONG'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap('all_inputs_layer',
                                                            table_name_prefix + temp_all_inputs + '.MaxDate',
                                                            'MaxDate', 'DATE'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap('all_inputs_layer', table_name_prefix + \
                                                            temp_all_inputs + '.CoordinatesObscured',
                                                            'CoordinatesObscured', 'SHORT'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap('all_inputs_layer',
                                                            table_name_prefix + temp_all_inputs + '.EORank',
                                                            'EORank', 'TEXT'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap('all_inputs_layer',
                                                            table_name_prefix + temp_all_inputs + '.URI',
                                                            'URI', 'TEXT'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap('all_inputs_layer', table_name_prefix + \
                                                            temp_all_inputs + '.DatasetSourceUniqueID',
                                                            'DatasetSourceUniqueID', 'TEXT'))
        arcpy.Append_management('all_inputs_layer', param_geodatabase + '/RangeMapInput', 'NO_TEST', field_mappings)
        arcpy.RemoveJoin_management('all_inputs_layer', table_name_prefix + 'Synonym')
        arcpy.RemoveJoin_management('all_inputs_layer', table_name_prefix + 'BIOTICS_ELEMENT_NATIONAL')

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
            search_row = None
            for search_row in EBARUtils.searchCursor(search_cursor):
                if search_row[id_field_name]:
                    if search_row[id_field_name] not in synonym_ids:
                        synonym_ids.append(search_row[id_field_name])
            if search_row:
                del search_row
        # get synonym names for IDs and combine with secondary names
        if len(synonym_ids) > 0:
            with arcpy.da.SearchCursor(param_geodatabase + '/Synonym', ['SynonymName', 'SHORT_CITATION_AUTHOR',
                                                                        'SHORT_CITATION_YEAR'],
                                       'SynonymID IN (' + ','.join(map(str, synonym_ids)) + ')') as search_cursor:
                search_row = None
                for search_row in EBARUtils.searchCursor(search_cursor):
                    if len(secondary_names) > 0:
                        secondary_names += ', '
                        synonyms_used += ', '
                    secondary_names += search_row['SynonymName']
                    synonyms_used += search_row['SynonymName']
                    if search_row['SHORT_CITATION_AUTHOR']:
                        secondary_names += ' (' + search_row['SHORT_CITATION_AUTHOR']
                        if search_row['SHORT_CITATION_YEAR']:
                            secondary_names += ', ' + str(int(search_row['SHORT_CITATION_YEAR']))
                        secondary_names += ')'
                if search_row:
                    del search_row

        # count expert reviews and calcuate average star rating
        EBARUtils.displayMessage(messages, 'Summarizing Expert Reviews')
        completed_expert_reviews = 0
        null_rating_reviews = 0
        star_rating_sum = 0
        if len(prev_range_map_ids) > 0:
            with arcpy.da.SearchCursor(param_geodatabase + '/Review', ['OverallStarRating'],
                                       'RangeMapID IN (' + prev_range_map_ids +
                                       ') AND DateCompleted IS NOT NULL AND UseForMapGen = 1') as cursor:
                row = None
                for row in EBARUtils.searchCursor(cursor):
                    completed_expert_reviews += 1
                    if row['OverallStarRating']:
                        star_rating_sum += row['OverallStarRating']
                    else:
                        null_rating_reviews += 1
                if row:
                    del row

        # update RangeMap metadata
        EBARUtils.displayMessage(messages, 'Updating Range Map record with Overall Summary')
        with arcpy.da.UpdateCursor('range_map_view',
                                   ['RangeMetadata', 'RangeDate', 'RangeMapNotes', 'RangeMapScope', 'SynonymsUsed'],
                                   'RangeMapID = ' + str(range_map_id)) as update_cursor:
            for update_row in update_cursor:
                # Metadata
                # input records
                # kludge because arc ends up with different field names under Enterprise gdb after joining
                field_names = [f.name for f in arcpy.ListFields(temp_overall_countby_source) if f.aliasName in
                               ['DatasetSourceName', 'FREQUENCY', 'frequency']]
                with arcpy.da.SearchCursor(temp_overall_countby_source, field_names) as search_cursor:
                    summary = ''
                    for search_row in EBARUtils.searchCursor(search_cursor):
                        if len(summary) > 0:
                            summary += ', '
                        summary += str(search_row[field_names[1]]) + ' ' + search_row[field_names[0]]
                    if len(summary) > 0:
                        del search_row
                summary = 'Input Records - ' + summary
                # expert reviews
                summary += '; Expert Reviews - ' + str(completed_expert_reviews)
                if completed_expert_reviews - null_rating_reviews > 0:
                    summary += ' (average star rating = ' + str(star_rating_sum /
                                                                (completed_expert_reviews - null_rating_reviews)) + ')'
                ## expert reviews
                #if ecoshape_reviews > 0:
                #    summary += '; Ecoshape Reviews Applied - ' + str(ecoshape_reviews)
                #if ecoshape_reviews > 0:
                #    if len(summary) > 0:
                #        summary += '; '
                #    summary += 'Expert Ecoshape Reviews - ' + str(ecoshape_reviews)

                # Notes
                ## restricted count
                ## kludge because arc ends up with different field names under Enterprise gdb after joining
                #field_names = [f.name for f in arcpy.ListFields(temp_overall_restricted) if f.aliasName in
                #               ['Restrictions', 'FREQUENCY', 'frequency']]
                #with arcpy.da.SearchCursor(temp_overall_restricted, field_names) as search_cursor:
                #    restricted = 0
                #    for search_row in EBARUtils.searchCursor(search_cursor):
                #        if search_row[field_names[0]] in ['R', 'E']:
                #            restricted += search_row[field_names[1]]
                #    if restricted > 0:
                #        del search_row
                #        summary = 'Input Records (' + str(restricted) + ' RESTRICTED) - ' + summary
                #    else:
                #        summary = 'Input Records - ' + summary
                notes = 'Primary Species Name - ' + param_species
                if len(secondary_names) > 0:
                    notes += '; Synonyms - ' + secondary_names
                ## additional input records
                #if additional_input_records > 0:
                #    notes += '; Additional Input Records - ' + str(additional_input_records)
                ## excluded input records
                #if excluded_input_records > 0:
                #    notes += '; Excluded Input Records - ' + str(excluded_input_records)
                update_cursor.updateRow([summary, datetime.datetime.now(), notes, scope, synonyms_used])

        # generate TOC entry and actual map!!!

        # temp clean-up
        if arcpy.Exists(temp_unique_synonyms):
            arcpy.Delete_management(temp_unique_synonyms)
        if arcpy.Exists(temp_overall_countby_source):
            arcpy.Delete_management(temp_overall_countby_source)
        #if arcpy.Exists(temp_overall_restricted):
        #    arcpy.Delete_management(temp_overall_restricted)
        if arcpy.Exists(temp_ecoshape_countby_source):
            arcpy.Delete_management(temp_ecoshape_countby_source)
        #if arcpy.Exists(temp_ecoshape_restricted):
        #    arcpy.Delete_management(temp_ecoshape_restricted)
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
        if arcpy.Exists(temp_restrictions):
            arcpy.Delete_management(temp_restrictions)
        # trouble deleting on server only due to locks; could be layer?
        if param_geodatabase[-4:].lower() == '.gdb':
            if arcpy.Exists(temp_all_inputs):
                arcpy.Delete_management(temp_all_inputs)

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
    param_species.value = 'Abronia latifolia'
    param_secondary = arcpy.Parameter()
    param_secondary.value = None
    #param_secondary.value = "'Dodia verticalis'"
    #param_secondary.value = "'Dodia tarandus';'Dodia verticalis'"
    param_version = arcpy.Parameter()
    param_version.value = '1.0'
    param_stage = arcpy.Parameter()
    param_stage.value = 'Auto-generated'
    param_scope = arcpy.Parameter()
    #param_scope.value = 'Canadian'
    param_scope.value = None
    parameters = [param_geodatabase, param_species, param_secondary, param_version, param_stage, param_scope]
    grm.runGenerateRangeMapTool(parameters, None)
