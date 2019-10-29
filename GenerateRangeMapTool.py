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
        # buffer size in metres, used if Accuracy not provided
        default_buffer_size = 10
        max_buffer_size = 100000
        # proportion of point buffer that must be within ecoshape to get Present; otherwise gets Presence Expected
        buffer_proportion_overlap = 0.6
        # number of years beyond which Presence gets set to Historical
        age_for_historical = 40
        if not messages:
            # for debugging, set workspace location
            arcpy.env.workspace = 'C:/GIS/EBAR/EBAR_outputs.gdb'

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
            param_species = 'Bombus bohemicus'
            param_secondary = ['Bombus occidentalis', 'Bombus suckleyi']
            param_version = '1.0'
            param_stage = 'Auto-generated'

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
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/InputPoint', 'input_point_layer')
        arcpy.SelectLayerByAttribute_management('input_point_layer', 'NEW_SELECTION',
                                                'SpeciesID IN (' + species_ids + ')')
        EBARUtils.displayMessage(messages, 'Input Points selected')
        EBARUtils.checkAddField('input_point_layer', 'buffer', 'LONG')
        code_block = '''
def GetBuffer(accuracy):
    ret = accuracy
    if not ret:
        ret = ''' + str(default_buffer_size) + '''
    if ret > ''' + str(max_buffer_size) + ''':
        ret = ''' + str(max_buffer_size) + '''
    return ret'''
        arcpy.CalculateField_management('input_point_layer', 'buffer', 'GetBuffer(!Accuracy!)', 'PYTHON3', code_block)
        if arcpy.Exists('TempPointBuffer'):
            arcpy.Delete_management('TempPointBuffer')
        arcpy.Buffer_analysis('input_point_layer', 'TempPointBuffer', 'buffer')
        EBARUtils.displayMessage(messages, 'Input Points buffered')

        # pairwise intersect buffers and ecoshape polygons
        if arcpy.Exists('TempPairwiseIntersect'):
            arcpy.Delete_management('TempPairwiseIntersect')
        arcpy.PairwiseIntersect_analysis(['TempPointBuffer',  param_geodatabase + '/Ecoshape'],
                                         'TempPairwiseIntersect')
        arcpy.AddIndex_management('TempPairwiseIntersect', 'InputDatasetID', 'idid_idx')
        arcpy.MakeFeatureLayer_management('TempPairwiseIntersect', 'pairwise_intersect_layer')
        EBARUtils.displayMessage(messages, 'Buffered Points pairwise intersected with Ecoshapes')

        # calculate proportion buffer per ecoshape piece based on size of full buffer
        # calculate total size of pieces for each buffer (will not equal original buffer size if outside ecoshapes)
        EBARUtils.checkAddField('pairwise_intersect_layer', 'BufferPropn', 'FLOAT')
        # calculate total size of buffer (will not equal original buffer size if it extends outside ecoshapes)
        if arcpy.Exists('TempTotalArea'):
            arcpy.Delete_management('TempTotalArea')
        arcpy.Statistics_analysis('pairwise_intersect_layer', 'TempTotalArea', [['Shape_Area', 'SUM']],
                                  'FID_TempPointBuffer')
        arcpy.AddJoin_management('pairwise_intersect_layer', 'FID_TempPointBuffer', 'TempTotalArea',
                                 'FID_TempPointBuffer')
        arcpy.CalculateField_management('pairwise_intersect_layer', 'TempPairwiseIntersect.BufferPropn',
                                        '!TempPairwiseIntersect.Shape_Area! / !TempTotalArea.SUM_Shape_Area!',
                                        'PYTHON3')
        arcpy.RemoveJoin_management('pairwise_intersect_layer', 'TempTotalArea')
        EBARUtils.displayMessage(messages, 'Proportion of Buffer per Ecoshape calculated')

        # get max buffer proportion per ecoshape
        if arcpy.Exists('TempEcoshapeMaxBuffer'):
            arcpy.Delete_management('TempEcoshapeMaxBuffer')
        arcpy.Statistics_analysis('pairwise_intersect_layer', 'TempEcoshapeMaxBuffer',
                                  [['BufferPropn', 'MAX'], ['MaxDate', 'MAX']], 'EcoshapeID')
        EBARUtils.displayMessage(messages, 'Maximum Buffer Proportion and Date per Ecoshape determined')

        # create RangeMapEcoshape records based on proportion overlap and max date
        with arcpy.da.InsertCursor(param_geodatabase + '/RangeMapEcoshape',
                                   ['RangeMapID', 'EcoshapeID', 'Presence']) as insert_cursor:
            input_found = False
            with arcpy.da.SearchCursor('TempEcoshapeMaxBuffer',
                                       ['EcoshapeID', 'MAX_BufferPropn', 'MAX_MaxDate']) as search_cursor:
                for row in EBARUtils.searchCursor(search_cursor):
                    input_found = True
                    presence = 'H'
                    if (datetime.datetime.now().year - row['MAX_MaxDate'].year) <= age_for_historical:
                        presence = 'X'
                        if row['MAX_BufferPropn'] >= buffer_proportion_overlap:
                            presence = 'P'
                    insert_cursor.insertRow([range_map_id, row['EcoshapeID'], presence])
                if input_found:
                    del row
        if not input_found:
            EBARUtils.displayMessage(messages, 'WARNING: No inputs/buffers overlap ecoshapes')
            # terminate
            return
        EBARUtils.setNewID(param_geodatabase + '/RangeMapEcoshape', 'RangeMapEcoshapeID',
                           'RangeMapID = ' + str(range_map_id))
        EBARUtils.displayMessage(messages, 'Range Map Ecoshape records created')

        # get ecoshape input counts by dataset
        if arcpy.Exists('TempEcoshapeCountByDataset'):
            arcpy.Delete_management('TempEcoshapeCountByDataset')
        arcpy.Statistics_analysis('pairwise_intersect_layer', 'TempEcoshapeCountByDataset',
                                  [['InputPointID', 'COUNT']], ['EcoshapeID', 'InputDatasetID'])
        EBARUtils.displayMessage(messages, 'Ecoshape input counts by Dataset determined')

        # create RangeMapEcoshapeInputDataset records based on summary
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
        EBARUtils.displayMessage(messages, 'Range Map Ecoshape Input Dataset records created')

        # get ecoshape input counts by source
        if arcpy.Exists('TempEcoshapeCountBySource'):
            arcpy.Delete_management('TempEcoshapeCountBySource')
        arcpy.AddJoin_management('pairwise_intersect_layer', 'InputDatasetID',
                                 param_geodatabase + '/InputDataset', 'InputDatasetID')
        arcpy.Statistics_analysis('pairwise_intersect_layer', 'TempEcoshapeCountBySource', [['InputPointID', 'COUNT']],
                                  ['EcoshapeID', 'InputDataset.DatasetSource'])
        EBARUtils.displayMessage(messages, 'Ecoshape input counts by Dataset Source determined')

        # update range map ecoshapes with summary
        with arcpy.da.UpdateCursor(param_geodatabase + '/RangeMapEcoshape', ['EcoshapeID', 'RangeMapEcoshapeNotes'],
                                   'RangeMapID = ' + str(range_map_id)) as update_cursor:
            for update_row in EBARUtils.updateCursor(update_cursor):
                with arcpy.da.SearchCursor('TempEcoshapeCountBySource', ['InputDataset_DatasetSource', 'FREQUENCY'],
                                           'TempPairwiseIntersect_EcoshapeID = ' + \
                                               str(update_row['EcoshapeID'])) as search_cursor:
                    summary = ''
                    for search_row in EBARUtils.searchCursor(search_cursor):
                        if len(summary) > 0:
                            summary += ', '
                        summary += search_row['InputDataset_DatasetSource'] + ': ' + str(search_row['FREQUENCY']) + \
                            ' input record(s)'
                    del search_row
                update_cursor.updateRow([update_row['EcoshapeID'], summary])
            del update_row
        EBARUtils.displayMessage(messages, 'Range Map Ecoshape records updated with summary')

        # get overall input counts by source
        if arcpy.Exists('TempOverallCountBySource'):
            arcpy.Delete_management('TempOverallCountBySource')
        arcpy.Statistics_analysis('pairwise_intersect_layer', 'TempOverallCountBySource', [['InputPointID', 'COUNT']],
                                  'InputDataset.DatasetSource')
        arcpy.RemoveJoin_management('pairwise_intersect_layer', 'InputDataset')
        EBARUtils.displayMessage(messages, 'Overall input counts by Dataset Source determined')

        # update RangeMap date and metadata
        with arcpy.da.UpdateCursor('range_map_view', ['RangeDate', 'RangeMetadata', 'RangeMapNotes'],
                                   'RangeMapID = ' + str(range_map_id)) as update_cursor:
            for update_row in update_cursor:
                with arcpy.da.SearchCursor('TempOverallCountBySource',
                                           ['InputDataset_DatasetSource', 'FREQUENCY']) as search_cursor:
                    summary = ''
                    for search_row in EBARUtils.searchCursor(search_cursor):
                        if len(summary) > 0:
                            summary += ', '
                        summary += search_row['InputDataset_DatasetSource'] + ': ' + str(search_row['FREQUENCY']) + \
                            ' input record(s)'
                    del search_row
                notes = 'Primary Species: ' + param_species + '; Secondary Species: ' + secondary_names
                update_cursor.updateRow([datetime.datetime.now(), summary, notes])
        EBARUtils.displayMessage(messages, 'Range Map record updated with overall summary')

        # generate actual map!!!

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
