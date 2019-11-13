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
        #max_buffer_size = 25000
        ## proportion of point buffer that must be within ecoshape to get Present; otherwise gets Presence Expected
        #buffer_proportion_overlap = 0.6
        # number of years beyond which Presence gets set to Historical
        age_for_historical = 40

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        if parameters:
            # passed from tool user interface
            param_geodatabase = parameters[0].valueAsText
            param_species = parameters[1].valueAsText
            param_secondary = parameters[2].valueAsText
            if param_secondary:
                param_secondary = param_secondary.replace("'", '')
                param_secondary = param_secondary.split(';')
            param_version = parameters[3].valueAsText
            param_stage = parameters[4].valueAsText
        else:
            # for debugging, hard code parameters
            param_geodatabase = 'C:/GIS/EBAR/EBAR_outputs.gdb'
            param_species = 'Micranthes spicata'
            param_secondary = None
            param_version = '1.0'
            param_stage = 'Auto-generated'

        # use passed geodatabase as workspace (still seems to go to default geodatabase)
        arcpy.env.workspace = param_geodatabase

        # check for species
        species_id = EBARUtils.checkSpecies(param_species, param_geodatabase)
        if not species_id:
            EBARUtils.displayMessage(messages, 'ERROR: Species not found')
            # terminate with error
            raise arcpy.ExecuteError

        # check for secondary species
        species_ids = str(species_id)
        secondary_names = ''
        if param_secondary:
            for secondary in param_secondary:
                secondary_id = EBARUtils.checkSpecies(secondary, param_geodatabase)
                if not secondary_id:
                    EBARUtils.displayMessage(messages, 'ERROR: Secondary species not found')
                    # terminate with error
                    raise arcpy.ExecuteError
                species_ids += ',' + str(secondary_id)
                secondary_names += secondary + ', '

        # check for range map record and add if necessary
        EBARUtils.displayMessage(messages, 'Checking for existing range map')
        range_map_id = None
        arcpy.MakeTableView_management(param_geodatabase + '/RangeMap', 'range_map_view')
        with arcpy.da.SearchCursor('range_map_view', ['RangeMapID'],
                                   'PrimarySpeciesID = ' + str(species_id) +
                                   " AND RangeVersion = '" + param_version +
                                   "' AND RangeStage = '" + param_stage + "'") as cursor:
            for row in EBARUtils.searchCursor(cursor):
                range_map_id = row['RangeMapID']
            if range_map_id:
                # found
                del row

        if range_map_id:
            # check for completed Reviews or Reviews in progress
            review_found = False
            review_completed = False
            ecoshape_review = False
            # use multi-table joins
            arcpy.AddJoin_management('range_map_view', 'RangeMapID',
                                      param_geodatabase + '/ReviewRequest', 'RangeMapID', 'KEEP_COMMON')
            arcpy.AddJoin_management('range_map_view', 'ReviewRequest.ReviewRequestID',
                                      param_geodatabase + '/Review', 'ReviewRequestID', 'KEEP_COMMON')

            # check for completed reviews, and if so terminate
            with arcpy.da.SearchCursor('range_map_view', ['Review.DateCompleted']) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    review_found = True
                    if row['DateCompleted']:
                        review_completed = True
                        break
                if review_found:
                    del row
            if review_completed:
                EBARUtils.displayMessage(messages, 'ERROR: Range Map already exists with completed review(s)')
                # terminate with error
                raise arcpy.ExecuteError

            # check for reviews in progress, and if so terminate
            arcpy.AddJoin_management('range_map_view', 'Review.ReviewID',
                                     param_geodatabase + '/RangeMapEcoshapeReview', 'ReviewID', 'KEEP_COMMON')
            with arcpy.da.SearchCursor('range_map_view',
                                       ['RangeMapEcoshapeReview.RangeMapEcoshapeReviewID']) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    ecoshape_review = True
                    break
                if ecoshape_review:
                    del row
            if ecoshape_review:
                EBARUtils.displayMessage(messages, 'ERROR: Range Map already exists with review(s) in progress')
                # terminate with error
                raise arcpy.ExecuteError

            arcpy.RemoveJoin_management('range_map_view', 'RangeMapEcoshapeReview')
            arcpy.RemoveJoin_management('range_map_view', 'Review')
            arcpy.RemoveJoin_management('range_map_view', 'ReviewRequest')

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
            # create RangeMap record
            with arcpy.da.InsertCursor('range_map_view',
                                       ['PrimarySpeciesID', 'RangeVersion', 'RangeStage']) as cursor:
                range_map_id = cursor.insertRow([species_id, param_version, param_stage])
            EBARUtils.setNewID(param_geodatabase + '/RangeMap', 'RangeMapID', 'OBJECTID = ' + str(range_map_id))
            EBARUtils.displayMessage(messages, 'Range Map record created')

        # create SecondarySpecies records
        if param_secondary:
            with arcpy.da.InsertCursor(param_geodatabase + '/SecondarySpecies',
                                       ['RangeMapID', 'SpeciesID']) as cursor:
                for secondary in param_secondary:
                    secondary_id = EBARUtils.checkSpecies(secondary, param_geodatabase)
                    cursor.insertRow([range_map_id, secondary_id])
            EBARUtils.setNewID(param_geodatabase + '/SecondarySpecies', 'SecondarySpeciesID',
                               'RangeMapID = ' + str(range_map_id))
            EBARUtils.displayMessage(messages, 'Secondary Species records created')

        # select all points for species and buffer
        EBARUtils.displayMessage(messages, 'Buffering Input Points')
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/InputPoint', 'input_point_layer')
        arcpy.SelectLayerByAttribute_management('input_point_layer', 'NEW_SELECTION',
                                                'SpeciesID IN (' + species_ids + ') AND (Accuracy IS NULL'
                                                ' OR Accuracy <= ' + str(EBARUtils.worst_accuracy) + ')')
#        EBARUtils.checkAddField('input_point_layer', 'buffer', 'LONG')
#        code_block = '''
#def GetBuffer(accuracy):
#    ret = accuracy
#    if not ret:
#        ret = ''' + str(default_buffer_size) + '''
#    if ret > ''' + str(max_buffer_size) + ''':
#        ret = ''' + str(max_buffer_size) + '''
#    return ret'''
#        arcpy.CalculateField_management('input_point_layer', 'buffer', 'GetBuffer(!Accuracy!)', 'PYTHON3', code_block)
        if arcpy.Exists('TempPointBuffer'):
            arcpy.Delete_management('TempPointBuffer')
        #arcpy.Buffer_analysis('input_point_layer', 'TempPointBuffer', 'buffer')
        arcpy.Buffer_analysis('input_point_layer', 'TempPointBuffer', default_buffer_size)

        # select all polygons for species
        EBARUtils.displayMessage(messages, 'Selecting Input Polygons')
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/InputPolygon', 'input_polygon_layer')
        arcpy.SelectLayerByAttribute_management('input_polygon_layer', 'NEW_SELECTION',
                                                'SpeciesID IN (' + species_ids + ') AND (Accuracy IS NULL'
                                                ' OR Accuracy <= ' + str(EBARUtils.worst_accuracy) + ')')

        # merge buffer polygons and input polygons
        EBARUtils.displayMessage(messages, 'Merging Buffered Points and Input Polygons')
        if arcpy.Exists('TempAllInputs'):
            arcpy.Delete_management('TempAllInputs')
        arcpy.Merge_management(['TempPointBuffer', 'input_polygon_layer'], 'TempAllInputs', None, 'ADD_SOURCE_INFO')

        # eo ranks, when available, override dates in determining historical (fake the date to accomplish this)
        EBARUtils.displayMessage(messages, 'Applying EO Ranks, where available, to determine historical records')
        result = arcpy.SelectLayerByAttribute_management('TempAllInputs', 'NEW_SELECTION',
                                                         "EORank IN ('H', 'H?', 'X', 'X?')")
        if int(result[1]) > 0:
            # 1000 years in the past
            fake_date_expr = 'datetime.datetime(datetime.datetime.now().year - 1000, 1, 1)'
            arcpy.CalculateField_management('TempAllInputs', 'MaxDate', fake_date_expr)
        result = arcpy.SelectLayerByAttribute_management('TempAllInputs', 'NEW_SELECTION',
                                                         "EORank IS NOT NULL AND EORank NOT IN ('H', 'H?', 'X', 'X?')")
        if int(result[1]) > 0:
            # 1000 years in the future
            fake_date_expr = 'datetime.datetime(datetime.datetime.now().year + 1000, 1, 1)'
            arcpy.CalculateField_management('TempAllInputs', 'MaxDate', fake_date_expr)
        arcpy.SelectLayerByAttribute_management('TempAllInputs', 'CLEAR_SELECTION')

        # pairwise intersect buffers and ecoshape polygons
        EBARUtils.displayMessage(messages, 'Pairwise Intersecting All Inputs with Ecoshapes')
        if arcpy.Exists('TempPairwiseIntersect'):
            arcpy.Delete_management('TempPairwiseIntersect')
        arcpy.PairwiseIntersect_analysis(['TempAllInputs',  param_geodatabase + '/Ecoshape'],
                                         'TempPairwiseIntersect')
        arcpy.AddIndex_management('TempPairwiseIntersect', 'InputDatasetID', 'idid_idx')
        arcpy.MakeFeatureLayer_management('TempPairwiseIntersect', 'pairwise_intersect_layer')

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
        if arcpy.Exists('TempEcoshapeMaxPolygon'):
            arcpy.Delete_management('TempEcoshapeMaxPolygon')
        arcpy.Statistics_analysis('pairwise_intersect_layer', 'TempEcoshapeMaxPolygon',
                                  [['MaxDate', 'MAX']], 'EcoshapeID')

        # create RangeMapEcoshape records based on max date #and proportion overlap 
        EBARUtils.displayMessage(messages, 'Creating Range Map Ecoshape records')
        with arcpy.da.InsertCursor(param_geodatabase + '/RangeMapEcoshape',
                                   ['RangeMapID', 'EcoshapeID', 'Presence']) as insert_cursor:
            input_found = False
            #with arcpy.da.SearchCursor('TempEcoshapeMaxPolygon',
            #                           ['EcoshapeID', 'MAX_PolygonPropn', 'MAX_MaxDate']) as search_cursor:
            with arcpy.da.SearchCursor('TempEcoshapeMaxPolygon',
                                       ['EcoshapeID', 'MAX_MaxDate']) as search_cursor:
                for row in EBARUtils.searchCursor(search_cursor):
                    input_found = True
                    # undated / no eo rank gets Presence Expected
                    presence = 'X'
                    if row['MAX_MaxDate']:
                        if (datetime.datetime.now().year - row['MAX_MaxDate'].year) <= age_for_historical:
                            # eo rank not in ('H', 'H?', 'X', 'X?') or "new" date gets Present
                            presence = 'P'
                        else:
                            # otherwise Historical
                            presence = 'H'
                    #presence = 'H'
                    #if row['MAX_MaxDate']:
                    #    if (datetime.datetime.now().year - row['MAX_MaxDate'].year) <= age_for_historical:
                    #        presence = 'X'
                    #        if row['MAX_PolygonPropn'] >= buffer_proportion_overlap:
                    #            presence = 'P'
                    insert_cursor.insertRow([range_map_id, row['EcoshapeID'], presence])
                if input_found:
                    del row
        if not input_found:
            EBARUtils.displayMessage(messages, 'WARNING: No inputs/buffers overlap ecoshapes')
            # terminate
            return
        EBARUtils.setNewID(param_geodatabase + '/RangeMapEcoshape', 'RangeMapEcoshapeID',
                           'RangeMapID = ' + str(range_map_id))

        # get ecoshape input counts by dataset
        EBARUtils.displayMessage(messages, 'Counting Ecoshape inputs by Dataset')
        if arcpy.Exists('TempEcoshapeCountByDataset'):
            arcpy.Delete_management('TempEcoshapeCountByDataset')
        arcpy.Statistics_analysis('pairwise_intersect_layer', 'TempEcoshapeCountByDataset',
                                  [['InputPointID', 'COUNT']], ['EcoshapeID', 'InputDatasetID'])

        # create RangeMapEcoshapeInputDataset records based on summary
        EBARUtils.displayMessage(messages, 'Creating Range Map Ecoshape Input Dataset records')
        ecoshape_summary = ''
        with arcpy.da.InsertCursor(param_geodatabase + '/RangeMapEcoshapeInputDataset',
                                   ['RangeMapEcoshapeID', 'InputDatasetID', 'InputDataSummary']) as insert_cursor:
            with arcpy.da.SearchCursor(param_geodatabase + '/RangeMapEcoshape', ['RangeMapEcoshapeID', 'EcoshapeID'],
                                       'RangeMapID = ' + str(range_map_id)) as rme_cursor:
                for rme_row in EBARUtils.searchCursor(rme_cursor):
                    with arcpy.da.SearchCursor('TempEcoshapeCountByDataset',
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

        # get ecoshape input counts by source
        EBARUtils.displayMessage(messages, 'Counting Ecoshape Inputs by Dataset Source')
        if arcpy.Exists('TempEcoshapeCountBySource'):
            arcpy.Delete_management('TempEcoshapeCountBySource')
        arcpy.AddJoin_management('pairwise_intersect_layer', 'InputDatasetID',
                                 param_geodatabase + '/InputDataset', 'InputDatasetID', 'KEEP_COMMON')
        arcpy.AddJoin_management('pairwise_intersect_layer', 'DatasetSourceID',
                                 param_geodatabase + '/DatasetSource', 'DatasetSourceID', 'KEEP_COMMON')
        arcpy.Statistics_analysis('pairwise_intersect_layer', 'TempEcoshapeCountBySource', [['InputPointID', 'COUNT']],
                                  ['EcoshapeID', 'DatasetSource.DatasetSourceName'])
        arcpy.RemoveJoin_management('pairwise_intersect_layer', 'DatasetSource')
        arcpy.RemoveJoin_management('pairwise_intersect_layer', 'InputDataset')

        # update range map ecoshapes with summary (and high-grade presence for some polygon dataset sources)
        EBARUtils.displayMessage(messages, 'Updating Range Map Ecoshape records with summary')
        with arcpy.da.UpdateCursor(param_geodatabase + '/RangeMapEcoshape',
                                   ['EcoshapeID', 'Presence', 'RangeMapEcoshapeNotes'],
                                   'RangeMapID = ' + str(range_map_id)) as update_cursor:
            for update_row in EBARUtils.updateCursor(update_cursor):
                with arcpy.da.SearchCursor('TempEcoshapeCountBySource',
                                           ['DatasetSource_DatasetSourceName', 'FREQUENCY'],
                                           'TempPairwiseIntersect_EcoshapeID = ' + \
                                           str(update_row['EcoshapeID'])) as search_cursor:
                    summary = ''
                    presence = update_row['Presence']
                    for search_row in EBARUtils.searchCursor(search_cursor):
                        if len(summary) > 0:
                            summary += ', '
                        summary += search_row['DatasetSource_DatasetSourceName'] + ': ' + \
                            str(search_row['FREQUENCY']) + ' input record(s)'
                        # high-grade Presence Expected to Present for some dataset sources
                        if presence == 'X' and (search_row['DatasetSource_DatasetSourceName'] in
                                                ('Element Occurrences', 'Source Feature Polygons',
                                                 'Source Feature Lines', 'Source Feature Points',
                                                 'Species Observation Polygons')):
                            presence = 'P'
                    del search_row
                update_cursor.updateRow([update_row['EcoshapeID'], presence, summary])
            del update_row

        # get overall input counts by source (using original inputs)
        EBARUtils.displayMessage(messages, 'Counting overall inputs by Dataset Source')
        # select only those within ecoshapes
        arcpy.MakeFeatureLayer_management('TempAllInputs', 'all_inputs_layer')
        arcpy.AddJoin_management('all_inputs_layer', 'InputDatasetID',
                                 param_geodatabase + '/InputDataset', 'InputDatasetID', 'KEEP_COMMON')
        arcpy.AddJoin_management('all_inputs_layer', 'DatasetSourceID',
                                 param_geodatabase + '/DatasetSource', 'DatasetSourceID', 'KEEP_COMMON')
        arcpy.SelectLayerByLocation_management('all_inputs_layer', 'INTERSECT', param_geodatabase + '/Ecoshape')
        if arcpy.Exists('TempOverallCountBySource'):
            arcpy.Delete_management('TempOverallCountBySource')
        arcpy.Statistics_analysis('all_inputs_layer', 'TempOverallCountBySource', [['InputPointID', 'COUNT']],
                                  ['DatasetSource.DatasetSourceName'])

        # update RangeMap date and metadata
        EBARUtils.displayMessage(messages, 'Updating Range Map record with overall summary')
        with arcpy.da.UpdateCursor('range_map_view', ['RangeDate', 'RangeMetadata', 'RangeMapNotes'],
                                   'RangeMapID = ' + str(range_map_id)) as update_cursor:
            for update_row in update_cursor:
                with arcpy.da.SearchCursor('TempOverallCountBySource',
                                           ['DatasetSource_DatasetSourceName', 'FREQUENCY']) as search_cursor:
                    summary = ''
                    for search_row in EBARUtils.searchCursor(search_cursor):
                        if len(summary) > 0:
                            summary += ', '
                        summary += search_row['DatasetSource_DatasetSourceName'] + ': ' + \
                            str(search_row['FREQUENCY']) + ' input record(s)'
                    del search_row
                notes = 'Primary Species: ' + param_species + '; Secondary Species: ' + secondary_names
                update_cursor.updateRow([datetime.datetime.now(), summary, notes])

        # generate TOC entry and actual map!!!

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
    grm.RunGenerateRangeMapTool(None, None)
