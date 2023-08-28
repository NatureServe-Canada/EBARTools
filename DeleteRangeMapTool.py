# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2021 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: DeleteRangeMapTool.py
# ArcGIS Python tool for deleting a RangeMap and related records

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
#import sys
#import locale
import EBARUtils
import arcpy
import datetime


class DeleteRangeMapTool:
    """Delete Range Map and related records from the EBAR geodatabase"""
    def __init__(self):
        pass

    def runDeleteRangeMapTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        param_geodatabase = parameters[0].valueAsText
        param_range_map_id = parameters[1].valueAsText
        EBARUtils.displayMessage(messages, 'RangeMapID: ' + param_range_map_id)
        range_map_id = int(param_range_map_id)

        # use passed geodatabase as workspace (still seems to go to default geodatabase)
        arcpy.env.workspace = param_geodatabase

        # get table name prefix (needed for joined tables and feature classes in enterprise geodatabases)
        table_name_prefix = EBARUtils.getTableNamePrefix(param_geodatabase)

        # check for range map
        arcpy.MakeTableView_management('RangeMap', 'range_map_view')
        result = arcpy.SelectLayerByAttribute_management('range_map_view', 'NEW_SELECTION',
                                                         'RangeMapID = ' + param_range_map_id)
        select_count = int(result[1])
        if select_count == 0:
            # terminate with error
            EBARUtils.displayMessage(messages, 'ERROR: Range Map not found')
            return

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

        # check for marked for deletion
        if not EBARUtils.checkMarkedForDelete('range_map_view'):
            # terminate with error
            EBARUtils.displayMessage(messages, 'ERROR: RangeStage field must be set to "Delete"')
            return

        # perform deletes
        where_clause = 'RangeMapEcoshapeID IN (SELECT RangeMapEcoshapeID FROM RangeMapEcoshape WHERE RangeMapID = ' + \
            param_range_map_id + ')'
        delete_count = EBARUtils.deleteRows('RangeMapEcoshapeInputDataset', 'rmeid_view', where_clause)
        EBARUtils.displayMessage(messages, str(delete_count) + ' RangeMapEcoshapeInputDataset record(s) deleted')
        where_clause = 'ExcludeFromRangeMapID = ' + param_range_map_id
        delete_count = EBARUtils.deleteRows('InputFeedback', 'if_view', where_clause)
        EBARUtils.displayMessage(messages, str(delete_count) + ' InputFeedback record(s) deleted')
        where_clause = 'RangeMapID = ' + param_range_map_id
        delete_count = EBARUtils.deleteRows('RangeMapEcoshape', 'rme_view', where_clause)
        EBARUtils.displayMessage(messages, str(delete_count) + ' RangeMapEcoshape record(s) deleted')
        delete_count = EBARUtils.deleteRows('SecondaryInput', 'si_view', where_clause)
        EBARUtils.displayMessage(messages, str(delete_count) + ' SecondaryInput record(s) deleted')
        delete_count = EBARUtils.deleteRows('SecondarySpecies', 'ss_view', where_clause)
        EBARUtils.displayMessage(messages, str(delete_count) + ' SecondarySpecies record(s) deleted')
        delete_count = EBARUtils.deleteRows('Review', 'rev_view', where_clause)
        EBARUtils.displayMessage(messages, str(delete_count) + ' Review record(s) deleted')
        delete_count = EBARUtils.deleteRows('RangeMapInput', 'rmi_view', where_clause)
        EBARUtils.displayMessage(messages, str(delete_count) + ' RangeMapInput record(s) deleted')
        delete_count = EBARUtils.deleteRows('RangeMap', 'rm_view', where_clause)
        EBARUtils.displayMessage(messages, str(delete_count) + ' RangeMap record(s) deleted')


# # controlling process
# if __name__ == '__main__':
#     drm = DeleteRangeMapTool()
#     # hard code parameters for debugging
#     param_geodatabase = arcpy.Parameter()
#     param_geodatabase.value = 'C:/GIS/EBAR/EBAR-KBA-Dev.gdb'
#     param_range_map_id = arcpy.Parameter()
#     param_range_map_id.value = '70'
#     parameters = [param_geodatabase, param_range_map_id]
#     drm.runDeleteRangeMapTool(parameters, None)
