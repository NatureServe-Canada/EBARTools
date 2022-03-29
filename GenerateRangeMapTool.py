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
from attr import fields_dict
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
                national_jur_ids = EBARUtils.national_jur_ids
                scope = 'N'
            if param_scope == 'Global':
                scope = 'G'
            if param_scope == 'North American':
                scope = 'A'
        param_jurisdictions_covered = parameters[6].valueAsText
        # convert to Python list
        param_jurisdictions_list = []
        if param_jurisdictions_covered:
            param_jurisdictions_list = param_jurisdictions_covered.replace("'", '')
            param_jurisdictions_list = param_jurisdictions_list.split(';')
            jur_ids_comma = EBARUtils.buildJurisdictionList(param_geodatabase, param_jurisdictions_list)
        param_custom_polygons_covered = parameters[7].valueAsText
        param_differentiate_usage_type = parameters[8].valueAsText

        # use passed geodatabase as workspace (still seems to go to default geodatabase)
        arcpy.env.workspace = param_geodatabase

        # get table name prefix (needed for joined tables and feature classes in enterprise geodatabases)
        table_name_prefix = EBARUtils.getTableNamePrefix(param_geodatabase)

        # check for species
        #species_id, short_citation = EBARUtils.checkSpecies(param_species.lower(), param_geodatabase)
        species_id, author_name = EBARUtils.checkSpecies(param_species.lower(), param_geodatabase)
        if not species_id:
            EBARUtils.displayMessage(messages, 'ERROR: Species not found')
            # terminate with error
            return
            #raise arcpy.ExecuteError
        #param_species += '' + short_citation
        param_species = '<i>' + param_species + '</i> ' + author_name

        # check for secondary species
        species_ids = str(species_id)
        secondary_ids = []
        secondary_names = ''
        # now contains only synonyms, not secondary species
        synonyms_used = ''
        if param_secondary:
            for secondary in param_secondary:
                secondary_id, author_name = EBARUtils.checkSpecies(secondary.lower(), param_geodatabase)
                if not secondary_id:
                    EBARUtils.displayMessage(messages, 'ERROR: Secondary species not found')
                    # terminate with error
                    return
                species_ids += ',' + str(secondary_id)
                if secondary_id in secondary_ids:
                    EBARUtils.displayMessage(messages, 'ERROR: Same secondary species specified more than once')
                    # terminate with error
                    return
                secondary_ids.append(secondary_id)
                if len(secondary_names) > 0:
                    secondary_names += ', '
                    #synonyms_used += ', '
                secondary_names += '<i>' + secondary + '</i> ' + author_name
                #synonyms_used += secondary

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
        row = None
        with arcpy.da.SearchCursor('range_map_view', [table_name_prefix + 'RangeMap.RangeMapID',
                                                      table_name_prefix + 'SecondarySpecies.SpeciesID']) as cursor:
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
        del cursor
        arcpy.RemoveJoin_management('range_map_view', table_name_prefix + 'SecondarySpecies')
        # check candidates for secondary match
        for candidate in match_candidate:
            if (candidate_secondary_match_count[candidate] == len(secondary_ids) and
                candidate_secondary_count[candidate] == len(secondary_ids)):
                prev_range_map.append(candidate)
                prev_range_map_ids = ','.join(map(str, prev_range_map))
        if len(prev_range_map_ids) > 0:
            # check prev for matching version and stage
            row = None
            with arcpy.da.SearchCursor('range_map_view', ['RangeMapID', 'RangeVersion', 'RangeStage'],
                                       'RangeMapID IN (' + prev_range_map_ids + ')') as cursor:
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
            if row:
                del row
            del cursor

        if range_map_id:
            arcpy.SelectLayerByAttribute_management('range_map_view', 'NEW_SELECTION',
                                                    'RangeMapID = ' + str(range_map_id))

            # check for completed or in progress reviews
            review_completed, ecoshape_review = EBARUtils.checkReview('range_map_view', table_name_prefix)
            if review_completed:
                # terminate with error
                EBARUtils.displayMessage(messages, 'ERROR: Range Map already exists with completed Review(s)')
                return
            if ecoshape_review:
                # terminate with error
                EBARUtils.displayMessage(messages, 'ERROR: Range Map already exists with Review(s) in progress')
                return

            # check for published
            if EBARUtils.checkPublished('range_map_view'):
                # terminate with error
                EBARUtils.displayMessage(messages, 'ERROR: Range Map has been published')
                return

            # no reviews completed or in progress, so delete any existing related records
            EBARUtils.displayMessage(messages, 'Range Map already exists with but with no Review(s) completed or in '
                                               'progress, so existing related records will be deleted')
            # consider replacing the following code blocks with select then Delete Rows tools
            rme_row = None
            with arcpy.da.SearchCursor(param_geodatabase + '/RangeMapEcoshape', ['RangeMapEcoshapeID'],
                                       'RangeMapID = ' + str(range_map_id)) as rme_cursor:
                for rme_row in EBARUtils.searchCursor(rme_cursor):
                    rmeid_row = None
                    with arcpy.da.UpdateCursor(param_geodatabase + '/RangeMapEcoshapeInputDataset',
                                               ['RangeMapEcoshpInputDatasetID'],
                                                'RangeMapEcoshapeID = ' + \
                                                str(rme_row['RangeMapEcoshapeID'])) as rmeid_cursor:
                        for rmeid_row in EBARUtils.updateCursor(rmeid_cursor):
                            rmeid_cursor.deleteRow()
                    if rmeid_row:
                        del rmeid_row
                    del rmeid_cursor
            rme_row = None
            with arcpy.da.UpdateCursor(param_geodatabase + '/RangeMapEcoshape', ['RangeMapEcoshapeID'],
                                       'RangeMapID = ' + str(range_map_id)) as rme_cursor:
                for rme_row in EBARUtils.updateCursor(rme_cursor):
                    rme_cursor.deleteRow()
            if rme_row:
                del rme_row
                EBARUtils.displayMessage(messages, 'Existing Range Map Ecoshape records deleted')
            del rme_cursor
            es_row = None
            with arcpy.da.UpdateCursor(param_geodatabase + '/SecondarySpecies', ['SecondarySpeciesID'],
                                       'RangeMapID = ' + str(range_map_id)) as es_cursor:
                for es_row in EBARUtils.updateCursor(es_cursor):
                    es_cursor.deleteRow()
            if es_row:
                del es_row
                EBARUtils.displayMessage(messages, 'Existing Secondary Species records deleted')
            del es_cursor
            rmi_row = None
            with arcpy.da.UpdateCursor(param_geodatabase + '/RangeMapInput', ['OBJECTID'],
                                       'RangeMapID = ' + str(range_map_id)) as rmi_cursor:
                for rmi_row in EBARUtils.updateCursor(rmi_cursor):
                    rmi_cursor.deleteRow()
            if rmi_row:
                del rmi_row
                EBARUtils.displayMessage(messages, 'Existing Range Map Input records deleted')
            del rmi_cursor

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
            del cursor
            range_map_id = EBARUtils.getUniqueID(param_geodatabase + '/RangeMap', 'RangeMapID', object_id)
            EBARUtils.displayMessage(messages, 'Range Map record created')

        # create SecondarySpecies records
        if param_secondary:
            with arcpy.da.InsertCursor(param_geodatabase + '/SecondarySpecies',
                                       ['RangeMapID', 'SpeciesID']) as cursor:
                for secondary in param_secondary:
                    #secondary_id, short_citation = EBARUtils.checkSpecies(secondary, param_geodatabase)
                    secondary_id, author_name = EBARUtils.checkSpecies(secondary, param_geodatabase)
                    cursor.insertRow([range_map_id, secondary_id])
            del cursor
            EBARUtils.displayMessage(messages, 'Secondary Species records created')

        # select all points for species and buffer
        EBARUtils.displayMessage(messages, 'Buffering Input Points')
        temp_point_buffer = EBARUtils.inputSelectAndBuffer(param_geodatabase, 'InputPoint', range_map_id,
                                                           table_name_prefix, species_ids, species_id, start_time)

        # select all lines for species and buffer
        EBARUtils.displayMessage(messages, 'Buffering Input Lines')
        temp_line_buffer = EBARUtils.inputSelectAndBuffer(param_geodatabase, 'InputLine', range_map_id,
                                                          table_name_prefix, species_ids, species_id, start_time)

        # select all polygons for species
        EBARUtils.displayMessage(messages, 'Selecting Input Polygons')
        input_polygon_layer = EBARUtils.inputSelectAndBuffer(param_geodatabase, 'InputPolygon', range_map_id,
                                                             table_name_prefix, species_ids, species_id, start_time)

        # merge buffer polygons and input polygons
        EBARUtils.displayMessage(messages, 'Merging Buffered Points and Lines and Input Polygons')
        temp_all_inputs = 'TempAllInputs' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        #arcpy.Merge_management([temp_point_buffer, temp_line_buffer, 'input_polygon_layer'], temp_all_inputs, None,
        #                       'ADD_SOURCE_INFO')
        arcpy.Merge_management([temp_point_buffer, temp_line_buffer, input_polygon_layer], temp_all_inputs, None,
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
                                                         'EORank IS NOT NULL ' + \
                                                         "AND EORank NOT IN ('', ' ', 'H', 'H?', 'X', 'X?')")
                                                         #"AND EORank NOT IN (' ', 'F', 'F?', 'H', 'H?', 'NR', " + \
                                                         #"'U', 'X', 'X?,')")
        if int(result[1]) > 0:
            # 1000 years in the future
            fake_date_expr = 'datetime.datetime(datetime.datetime.now().year + 1000, 1, 1)'
            arcpy.CalculateField_management('all_inputs_layer', 'TempDate', fake_date_expr)
        arcpy.SelectLayerByAttribute_management('all_inputs_layer', 'CLEAR_SELECTION')

        # pairwise intersect buffers and ecoshape polygons
        EBARUtils.displayMessage(messages, 'Pairwise Intersecting All Inputs with Ecoshapes')
        if national_jur_ids or param_jurisdictions_covered:
            where_clause = ''
            if national_jur_ids:
                where_clause = 'JurisdictionID IN ' + national_jur_ids
            if param_jurisdictions_covered:
                if len(where_clause) > 0:
                    where_clause += ' AND '
                where_clause += 'JurisdictionID IN ' + jur_ids_comma
            #arcpy.MakeFeatureLayer_management(param_geodatabase + '/Ecoshape', 'ecoshape_layer',
            #                                  'JurisdictionID IN ' + national_jur_ids)
            arcpy.MakeFeatureLayer_management(param_geodatabase + '/EcoshapeCoastalBuffer', 'ecoshape_layer',
                                              where_clause)
        else:
            #arcpy.MakeFeatureLayer_management(param_geodatabase + '/Ecoshape', 'ecoshape_layer')
            arcpy.MakeFeatureLayer_management(param_geodatabase + '/EcoshapeCoastalBuffer', 'ecoshape_layer')
        if param_custom_polygons_covered:
            arcpy.SelectLayerByLocation_management('ecoshape_layer', 'INTERSECT', param_custom_polygons_covered)
        temp_pairwise_intersect = 'TempPairwiseIntersect' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.PairwiseIntersect_analysis(['all_inputs_layer',  'ecoshape_layer'], temp_pairwise_intersect)
        arcpy.AddIndex_management(temp_pairwise_intersect, 'InputDatasetID', 'idid_idx')
        arcpy.MakeFeatureLayer_management(temp_pairwise_intersect, 'pairwise_intersect_layer')

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
                             <= EBARUtils.age_for_historical)):
                            if presence in ['H', 'X']:
                                presence = 'P'
                if input_found:
                    # save final ecoshape
                    insert_cursor.insertRow([range_map_id, ecoshape_id, presence])
                    del row
            del search_cursor
        del insert_cursor
        if not input_found:
            EBARUtils.displayMessage(messages, 'WARNING: No inputs/buffers overlap ecoshapes')

        # get ecoshape input counts by dataset
        EBARUtils.displayMessage(messages, 'Counting Ecoshape Inputs by Dataset')
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

        # apply Reviews and summaries to RangeMapEcoshape records
        EBARUtils.displayMessage(messages,
                                 'Applying Reviews and summaries to Range Map Ecoshape records')
        if len(prev_range_map_ids) > 0:
            arcpy.MakeTableView_management(param_geodatabase + '/EcoshapeReview', 'ecoshape_review_view')
            arcpy.AddJoin_management('ecoshape_review_view', 'EcoshapeID', param_geodatabase + '/Ecoshape', 'EcoshapeID')
            arcpy.AddJoin_management('ecoshape_review_view', 'ReviewID', param_geodatabase + '/Review', 'ReviewID')
        # loop existing range map ecoshapes
        update_row = None
        with arcpy.da.UpdateCursor(param_geodatabase + '/RangeMapEcoshape',
                                   ['EcoshapeID', 'RangeMapEcoshapeID', 'RangeMapID', 'Presence',
                                    'RangeMapEcoshapeNotes', 'MigrantStatus'],
                                   'RangeMapID = ' + str(range_map_id)) as update_cursor:
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
                            remove = True
                    del search_cursor
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
                    summary = ''
                    with arcpy.da.SearchCursor(temp_ecoshape_countby_source, field_names,
                                               id_field_name + ' = ' + str(update_row['EcoshapeID'])) as search_cursor:
                        presence = update_row['Presence']
                        migrant_status = update_row['MigrantStatus']
                        for search_row in EBARUtils.searchCursor(search_cursor):
                            if len(summary) > 0:
                                summary += ', '
                            summary += str(search_row[field_names[2]]) + ' ' + search_row[field_names[0]]
                    if len(summary) > 0:
                        del search_row
                    del search_cursor
                    summary = 'Input records - ' + summary
                    # check for ecoshape "update" reviews
                    if len(prev_range_map_ids) > 0:
                        search_row = None
                        with arcpy.da.SearchCursor('ecoshape_review_view',
                                                   [table_name_prefix + 'EcoshapeReview.Markup',
                                                    table_name_prefix + 'EcoshapeReview.EcoshapeReviewNotes',
                                                    table_name_prefix + 'EcoshapeReview.Username',
                                                    table_name_prefix + 'EcoshapeReview.MigrantStatus'],
                                                   table_name_prefix + 'Review.RangeMapID IN (' + \
                                                   prev_range_map_ids + ') AND ' + table_name_prefix + \
                                                   'Review.UseForMapGen = 1 AND ' + table_name_prefix + \
                                                   'EcoshapeReview.UseForMapGen = 1 AND ' + table_name_prefix + \
                                                   "EcoshapeReview.Markup IN ('P', 'X', 'H') AND "  + table_name_prefix + \
                                                   'EcoshapeReview.EcoshapeID = ' + \
                                                   str(update_row['EcoshapeID'])) as search_cursor:
                            for search_row in EBARUtils.searchCursor(search_cursor):
                                presence = search_row[table_name_prefix + 'EcoshapeReview.Markup']
                                migrant_status = search_row[table_name_prefix + 'EcoshapeReview.MigrantStatus']
                                # get expert name and publish settings to populate reviewer comments
                                with arcpy.da.SearchCursor(param_geodatabase + '/Expert',
                                                           ['ExpertName', 'PublishName', 'PublishComments'],
                                                           "Username = '" + search_row[table_name_prefix +
                                                           'EcoshapeReview.Username'] + "'") as expert_cursor:
                                    expert_comment = None
                                    summary += '; Expert Ecoshape Review'
                                    for expert_row in EBARUtils.searchCursor(expert_cursor):
                                        if expert_row['PublishName']:
                                            expert_comment = expert_row['ExpertName']
                                        else:
                                            expert_comment = 'Anonymous'
                                        expert_comment += ' Reviewer Comment - '
                                        if expert_row['PublishComments']:
                                            expert_comment += search_row[table_name_prefix + \
                                                'EcoshapeReview.EcoshapeReviewNotes']
                                        else:
                                            expert_comment += 'Unpublished'
                                        summary += '<br>' + expert_comment
                                    if expert_comment:
                                        del expert_row
                        if search_row:
                            del search_row
                        del search_cursor
                    update_cursor.updateRow([update_row['EcoshapeID'], update_row['RangeMapEcoshapeID'],
                                             update_row['RangeMapID'], presence, summary, migrant_status])
        if update_row:
            del update_row
        del update_cursor

        # loop review records and check for need to add
        if len(prev_range_map_ids) > 0:
            condition = table_name_prefix + 'Review.RangeMapID IN (' + \
                prev_range_map_ids + ') AND ' + table_name_prefix + \
                'Review.UseForMapGen = 1 AND ' + table_name_prefix + \
                'EcoshapeReview.UseForMapGen = 1 AND ' + table_name_prefix + \
                "EcoshapeReview.Markup IN ('P', 'X', 'H')"
            if scope == 'N' or param_jurisdictions_covered or param_custom_polygons_covered:
                ecoshape_ids_comma = '('
                search_row = None
                with arcpy.da.SearchCursor('ecoshape_layer', ['EcoshapeID']) as search_cursor:
                    for search_row in EBARUtils.searchCursor(search_cursor):
                        if len(ecoshape_ids_comma) > 1:
                            ecoshape_ids_comma += ', '
                        ecoshape_ids_comma += str(search_row['EcoshapeID'])
                if search_row:
                    del search_row
                del search_cursor
                ecoshape_ids_comma += ')'
                condition += ' AND ' + table_name_prefix + 'EcoshapeReview.EcoshapeID IN ' + ecoshape_ids_comma
            search_row = None
            with arcpy.da.SearchCursor('ecoshape_review_view',
                                       [table_name_prefix + 'EcoshapeReview.EcoshapeID',
                                        table_name_prefix + 'EcoshapeReview.Markup',
                                        table_name_prefix + 'EcoshapeReview.EcoshapeReviewNotes',
                                        table_name_prefix + 'EcoshapeReview.Username',
                                        table_name_prefix + 'EcoshapeReview.MigrantStatus'],
                                       condition) as search_cursor:
                for search_row in EBARUtils.searchCursor(search_cursor):
                    # check for ecoshape
                    add = True
                    with arcpy.da.UpdateCursor(param_geodatabase + '/RangeMapEcoshape', ['EcoshapeID'],
                                               'RangeMapID = ' + str(range_map_id) + ' AND EcoshapeID = ' +
                                               str(search_row[table_name_prefix +
                                               'EcoshapeReview.EcoshapeID'])) as update_cursor:
                        for update_row in EBARUtils.updateCursor(update_cursor):
                            add = False
                    if not add:
                        del update_row
                    else:
                        # get expert name and publish settings to populate reviewer comments
                        with arcpy.da.SearchCursor(param_geodatabase + '/Expert',
                                                    ['ExpertName', 'PublishName', 'PublishComments'],
                                                    "Username = '" + search_row[table_name_prefix +
                                                    'EcoshapeReview.Username'] + "'") as expert_cursor:
                            expert_comment = None
                            notes = 'Expert Ecoshape Review'
                            for expert_row in EBARUtils.searchCursor(expert_cursor):
                                if expert_row['PublishName']:
                                    expert_comment = expert_row['ExpertName']
                                else:
                                    expert_comment = 'Anonymous'
                                expert_comment += ' Reviewer Comment - '
                                if expert_row['PublishComments']:
                                    expert_comment += search_row[table_name_prefix + \
                                        'EcoshapeReview.EcoshapeReviewNotes']
                                else:
                                    expert_comment += 'Unpublished'
                                notes += '<br>' + expert_comment
                            if expert_comment:
                                del expert_row
                        with arcpy.da.InsertCursor(param_geodatabase + '/RangeMapEcoshape',
                                                   ['RangeMapID', 'EcoshapeID', 'Presence',
                                                    'RangeMapEcoshapeNotes', 'MigrantStatus']) as insert_cursor:
                            insert_cursor.insertRow([range_map_id,
                                                     search_row[table_name_prefix + 'EcoshapeReview.EcoshapeID'],
                                                     search_row[table_name_prefix + 'EcoshapeReview.Markup'],
                                                     notes,
                                                     search_row[table_name_prefix + 'EcoshapeReview.MigrantStatus']])
                    del update_cursor
            if search_row:
                del search_row
            del search_cursor

        # create RangeMapEcoshapeInputDataset records based on summary
        EBARUtils.displayMessage(messages, 'Creating Range Map Ecoshape Input Dataset records')
        rme_row = None
        with arcpy.da.SearchCursor(param_geodatabase + '/RangeMapEcoshape', ['RangeMapEcoshapeID', 'EcoshapeID'],
                                   'RangeMapID = ' + str(range_map_id)) as rme_cursor:
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
                del search_cursor
        if rme_row:
            del rme_row
        del rme_cursor

        # migratory
        if param_differentiate_usage_type == 'true':
            # set UsageType from input data
            EBARUtils.displayMessage(messages, 'Applying Breeding and Behaviour Codes to set UsageType')

            # get BBCode domain values
            domains = arcpy.da.ListDomains(param_geodatabase)
            for domain in domains:
                if domain.name == 'BreedingAndBehaviourCode':
                    bbc_domain_values = domain.codedValues

            # summarize all input records by ecoshape
            usage_type_stats = param_geodatabase + '/TempUTSTats' + str(start_time.year) + str(start_time.month) + \
                str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
            arcpy.Statistics_analysis(temp_pairwise_intersect, usage_type_stats, [['EcoshapeID', 'COUNT']],
                                      ['EcoshapeID', 'BreedingAndBehaviourCode'])
            row = None
            with arcpy.da.SearchCursor(usage_type_stats, ['EcoshapeID', 'BreedingAndBehaviourCode'],
                                       sql_clause=(None, 'ORDER BY EcoshapeID')) as cursor:
                prev_ecoshape_id = None
                usage_type = None
                for row in EBARUtils.searchCursor(cursor):
                    if row['EcoshapeID'] != prev_ecoshape_id:
                        if prev_ecoshape_id and usage_type:
                            # save previous
                            update_row = None
                            with arcpy.da.UpdateCursor(param_geodatabase + '/RangeMapEcoshape', ['UsageType'],
                                                       'RangeMapID = ' + str(range_map_id) + ' AND EcoshapeID = ' +
                                                       str(prev_ecoshape_id)) as update_cursor:
                                for update_row in EBARUtils.updateCursor(update_cursor):
                                    update_cursor.updateRow([usage_type])
                            if update_row:
                                del update_row
                            del update_cursor
                        # reset for new ecoshape
                        prev_ecoshape_id = row['EcoshapeID']
                        usage_type = None
                    # any confirmation in ecoshape prevails
                    if row['BreedingAndBehaviourCode']:
                        if 'Confirmed' in bbc_domain_values[row['BreedingAndBehaviourCode']]:
                            usage_type = 'B'
                        elif ('Probable' in bbc_domain_values[row['BreedingAndBehaviourCode']] or
                            'Possible' in bbc_domain_values[row['BreedingAndBehaviourCode']]) and usage_type != 'B':
                            usage_type = 'P'
            if row:
                if prev_ecoshape_id and usage_type:
                    # save final
                    update_row = None
                    with arcpy.da.UpdateCursor(param_geodatabase + '/RangeMapEcoshape', ['UsageType'],
                                                'RangeMapID = ' + str(range_map_id) + ' AND EcoshapeID = ' +
                                                str(prev_ecoshape_id)) as update_cursor:
                        for update_row in EBARUtils.updateCursor(update_cursor):
                            update_cursor.updateRow([usage_type])
                    if update_row:
                        del update_row
                    del update_cursor
                del row
            del cursor

            # apply UsageType from reviews
        
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
        # field_dict = {}
        # field_dict['RangeMapID'] = table_name_prefix + temp_all_inputs + '.RangeMapID'
        # field_dict['OriginalGeometryType'] = table_name_prefix + temp_all_inputs + '.OriginalGeometryType'
        # field_dict['NationalScientificName'] = table_name_prefix + 'BIOTICS_ELEMENT_NATIONAL.NATIONAL_SCIENTIFIC_NAME'
        # field_dict['SynonymName'] = table_name_prefix + 'Synonym.SynonymName'
        # field_dict['DatasetSourceName'] = table_name_prefix + 'DatasetSource.DatasetSourceName'
        # field_dict['DatasetType'] = table_name_prefix + 'DatasetSource.DatasetType'
        # field_dict['Accuracy'] = table_name_prefix + temp_all_inputs + '.Accuracy'
        # field_dict['MaxDate'] = table_name_prefix + temp_all_inputs + '.MaxDate'
        # field_dict['CoordinatesObscured'] = table_name_prefix + temp_all_inputs + '.CoordinatesObscured'
        # field_dict['EORank'] = table_name_prefix + temp_all_inputs + '.EORank'
        # field_dict['URI'] = table_name_prefix + temp_all_inputs + '.URI'
        # field_dict['DatasetSourceUniqueID'] = table_name_prefix + temp_all_inputs + '.DatasetSourceUniqueID'
        # field_dict['SHAPE@'] = 'SHAPE@'
        # EBARUtils.appendUsingCursor('all_inputs_layer', param_geodatabase + '/RangeMapInput', field_dict=field_dict)
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
        search_row = None
        with arcpy.da.SearchCursor(temp_unique_synonyms, [id_field_name]) as search_cursor:
            for search_row in EBARUtils.searchCursor(search_cursor):
                if search_row[id_field_name]:
                    if search_row[id_field_name] not in synonym_ids:
                        synonym_ids.append(search_row[id_field_name])
        if search_row:
            del search_row
        del search_cursor
        # get synonym names for IDs (no longer combined with secondary names)
        synonym_authors = ''
        if len(synonym_ids) > 0:
            search_row = None
            with arcpy.da.SearchCursor(param_geodatabase + '/Synonym', ['SynonymName', 'AUTHOR_NAME'],
                                       'SynonymID IN (' + ','.join(map(str, synonym_ids)) + ')') as search_cursor:
                for search_row in EBARUtils.searchCursor(search_cursor):
                    if len(synonyms_used) > 0:
                        #secondary_names += ', '
                        synonyms_used += ', '
                        synonym_authors += ', '
                    #secondary_names += search_row['SynonymName']
                    #secondary_names += '<i>' + search_row['SynonymName'] + '</i>'
                    synonyms_used += search_row['SynonymName']
                    synonym_authors += '<i>' + search_row['SynonymName'] + '</i>'
                    if search_row['AUTHOR_NAME']:
                        #secondary_names += ' ' + search_row['AUTHOR_NAME']
                        synonym_authors += ' ' + search_row['AUTHOR_NAME']
            if search_row:
                del search_row
            del search_cursor

        # count expert reviews and and compile reviewer details (if publishable)
        EBARUtils.displayMessage(messages, 'Summarizing Expert Reviews')
        completed_expert_reviews = 0
        #null_rating_reviews = 0
        #star_rating_sum = 0
        experts_comments = []
        experts = []
        anonymous_count = 0
        if len(prev_range_map_ids) > 0:
            row = None
            with arcpy.da.SearchCursor(param_geodatabase + '/Review', ['OverallStarRating', 'ReviewNotes', 'Username'],
                                       'RangeMapID IN (' + prev_range_map_ids +
                                       ') AND DateCompleted IS NOT NULL AND UseForMapGen = 1') as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    completed_expert_reviews += 1
                    # if row['OverallStarRating']:
                    #     star_rating_sum += row['OverallStarRating']
                    # else:
                    #     null_rating_reviews += 1
                    # get expert name and publish settings to populate reviewer comments
                    expert_comment = None
                    with arcpy.da.SearchCursor(param_geodatabase + '/Expert',
                                               ['ExpertName', 'PublishName', 'PublishComments'],
                                               "Username = '" + row['Username'] + "'") as expert_cursor:
                        for expert_row in EBARUtils.searchCursor(expert_cursor):
                            if expert_row['PublishName']:
                                expert_name =  expert_row['ExpertName']
                            else:
                                expert_name = 'Anonymous'
                                anonymous_count += 1
                            experts.append(expert_name)
                            expert_comment = expert_name
                            expert_comment += ' Reviewer Comment - '
                            if expert_row['PublishComments']:
                                expert_comment += row['ReviewNotes']
                            else:
                                expert_comment += 'Unpublished'
                            experts_comments.append(expert_comment)
                    if expert_comment:
                        del expert_row
                    del expert_cursor
            if row:
                del row
            del cursor

        # update RangeMap metadata
        EBARUtils.displayMessage(messages, 'Updating Range Map record with Overall Summary')
        update_row = None
        with arcpy.da.UpdateCursor('range_map_view',
                                   ['RangeMetadata', 'RangeDate', 'RangeMapNotes', 'RangeMapScope', 'SynonymsUsed',
                                    'ReviewerComments'],
                                   'RangeMapID = ' + str(range_map_id)) as update_cursor:
            for update_row in update_cursor:
                # Metadata
                # input records
                # kludge because arc ends up with different field names under Enterprise gdb after joining
                field_names = [f.name for f in arcpy.ListFields(temp_overall_countby_source) if f.aliasName in
                               ['DatasetSourceName', 'FREQUENCY', 'frequency']]
                summary = ''
                with arcpy.da.SearchCursor(temp_overall_countby_source, field_names) as search_cursor:
                    for search_row in EBARUtils.searchCursor(search_cursor):
                        if len(summary) > 0:
                            summary += ', '
                        summary += str(search_row[field_names[1]]) + ' ' + search_row[field_names[0]]
                if len(summary) > 0:
                    del search_row
                del search_cursor
                summary = 'Input Records - ' + summary
                # expert reviews
                summary += '; Expert Reviews - '
                first = True
                for expert_name in experts:
                    if expert_name != 'Anonymous':
                        if not first:
                            summary += ', '
                        first = False
                        summary += expert_name
                if anonymous_count > 0:
                    if not first:
                        summary += ', '
                    summary += str(anonymous_count) + ' Anonymous'
                reviewer_comments = ''
                for expert_comment in experts_comments:
                    if len(reviewer_comments) > 0:
                        reviewer_comments += '<br>'
                    reviewer_comments += expert_comment
                # Notes
                notes = 'Primary Species - ' + param_species
                if len(secondary_names) > 0:
                    notes += '; Secondary Species - ' + secondary_names
                if len(synonym_authors) > 0:
                    notes += '; Synonyms - ' + synonym_authors
                update_cursor.updateRow([summary, datetime.datetime.now(), notes, scope, synonyms_used,
                                         reviewer_comments])
        if update_row:
            del update_row
        del update_cursor

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
        if arcpy.Exists(temp_restrictions):
            arcpy.Delete_management(temp_restrictions)
        if arcpy.Exists(usage_type_stats):
            arcpy.Delete_management(usage_type_stats)
        # trouble deleting on server only due to locks; could be layer?
        #if param_geodatabase[-4:].lower() == '.gdb':
        #    if arcpy.Exists(temp_all_inputs):
        #        arcpy.Delete_management(temp_all_inputs)

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
    param_species.value = 'Aechmophorus occidentalis' #'Acalypta cooleyi' #Bombus suckleyi #'Micranthes spicata'
    param_secondary = arcpy.Parameter()
    param_secondary.value = None
    #param_secondary.value = "'Schistochilopsis incisa var. opacifolia'" #"'Dodia tarandus';'Dodia verticalis'"
    param_version = arcpy.Parameter()
    param_version.value = '1.0'
    param_stage = arcpy.Parameter()
    param_stage.value = 'Auto-generated' #'Expert reviewed test00'
    param_scope = arcpy.Parameter()
    param_scope.value = None
    #param_scope.value = 'Canadian'
    param_jurisdictions_covered = arcpy.Parameter()
    param_jurisdictions_covered.value = None
    #param_jurisdictions_covered.value = "'British Columbia'"
    param_custom_polygons_covered = arcpy.Parameter()
    param_custom_polygons_covered.value = None
    #param_custom_polygons_covered.value = 'C:/GIS/EBAR/EBARServer.gdb/Custom'
    param_differentiate_usage_type = arcpy.Parameter()
    param_differentiate_usage_type.value = 'true'
    parameters = [param_geodatabase, param_species, param_secondary, param_version, param_stage, param_scope,
                  param_jurisdictions_covered, param_custom_polygons_covered, param_differentiate_usage_type]
    grm.runGenerateRangeMapTool(parameters, None)
