# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Gabrielle Miller
# © NatureServe Canada 2021 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: FlagBadDataUsingIDTool.py
# ArcGIS Python tool for flagging bad input data using an InputPoint/Line/PolygonID

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import EBARUtils
import arcpy
import datetime


class FlagBadDataUsingIDTool:
    """Flag bad input data using an InputPoint/Line/PolygonID"""
    def __init__(self):
        pass

    def runFlagBadDataUsingIDTool(self, parameters, messages):
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
        param_input_point_id = parameters[1].valueAsText
        param_input_line_id = parameters[2].valueAsText
        param_input_polygon_id = parameters[3].valueAsText
        param_justification = parameters[4].valueAsText
        param_undo = parameters[5].valueAsText
        id_count = 0
        if param_input_point_id:
            id_count += 1
            input_table = param_geodatabase + '/InputPoint'
            bad_table  = param_geodatabase + '/BadInputPoint'
            id_field = 'InputPointID'
            id_value = param_input_point_id
        if param_input_line_id:
            id_count += 1
            input_table = param_geodatabase + '/InputLine'
            bad_table  = param_geodatabase + '/BadInputLine'
            id_field = 'InputLineID'
            id_value = param_input_line_id
        if param_input_polygon_id:
            id_count += 1
            input_table = param_geodatabase + '/InputPolygon'
            bad_table  = param_geodatabase + '/BadInputPolygon'
            id_field = 'InputPolygonID'
            id_value = param_input_polygon_id
        if id_count == 0:
            EBARUtils.displayMessage(messages, 'ERROR: Please provide one ID')
            # terminate with error
            return
        if id_count > 1:
            EBARUtils.displayMessage(messages, 'ERROR: Please provide only one ID')
            # terminate with error
            return
        if param_undo == 'false' and not param_justification:
            EBARUtils.displayMessage(messages, 'ERROR: Please provide a justification')
            # terminate with error
            return

        if param_undo == 'false':
            # check for record
            arcpy.MakeFeatureLayer_management(input_table, 'input_layer', id_field + ' = ' + id_value)
            result = arcpy.GetCount_management('input_layer')
            if int(result[0]) == 0:
                EBARUtils.displayMessage(messages, 'ERROR: input record with specified ID not found')
                # terminate with error
                return
            # check for related records
            arcpy.MakeTableView_management(param_geodatabase + '/Visit', 'visit_view', id_field + ' = ' + id_value)
            result = arcpy.GetCount_management('visit_view')
            if int(result[0]) > 0:
                EBARUtils.displayMessage(messages, 'ERROR: related Visit record prevents flagging')
                # terminate with error
                return
            arcpy.MakeTableView_management(param_geodatabase + '/InputFeedback', 'input_feedback_view',
                                              id_field + ' = ' + id_value)
            result = arcpy.GetCount_management('input_feedback_view')
            if int(result[0]) > 0:
                EBARUtils.displayMessage(messages, 'ERROR: related InputFeedback record prevents flagging')
                # terminate with error
                return
            arcpy.MakeTableView_management(param_geodatabase + '/SecondaryInput', 'secondary_input_view',
                                              id_field + ' = ' + id_value)
            result = arcpy.GetCount_management('secondary_input_view')
            if int(result[0]) > 0:
                EBARUtils.displayMessage(messages, 'ERROR: related SecondaryInput record prevents flagging')
                # terminate with error
                return
            # create InputFeedback record, append to bad, delete input
            EBARUtils.displayMessage(messages, 'Saving InputFeedback and appending Bad record')
            with arcpy.da.InsertCursor(param_geodatabase + '/InputFeedback',
                                       ['Bad' + id_field, 'Justification']) as insert_cursor:
                insert_cursor.insertRow([id_value, param_justification])
            #arcpy.Append_management('input_layer', bad_table, 'TEST')
            EBARUtils.appendUsingCursor('input_layer', bad_table)
            EBARUtils.displayMessage(messages, 'Deleting original Input record')
            arcpy.DeleteRows_management('input_layer')
        else:
            # check for record
            arcpy.MakeFeatureLayer_management(bad_table, 'bad_input_layer', id_field + ' = ' + id_value)
            result = arcpy.GetCount_management('bad_input_layer')
            if int(result[0]) == 0:
                EBARUtils.displayMessage(messages, 'ERROR: bad record with specified ID not found')
                # terminate with error
                return
            # delete InputFeedback record, append to input, delete bad
            EBARUtils.displayMessage(messages, 'Deleting InputFeedback and re-adding Input record')
            EBARUtils.deleteRows(param_geodatabase + '/InputFeedback', 'if_view', 'Bad' + id_field + ' = ' + id_value)
            EBARUtils.appendUsingCursor('bad_input_layer', input_table)
            EBARUtils.displayMessage(messages, 'Deleting Bad record')
            arcpy.DeleteRows_management('bad_input_layer')

        # end time
        end_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'End time: ' + str(end_time))
        elapsed_time = end_time - start_time
        EBARUtils.displayMessage(messages, 'Elapsed time: ' + str(elapsed_time))
        return


# controlling process
if __name__ == '__main__':
    fbdui = FlagBadDataUsingIDTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:/GIS/EBAR/EBAR-KBA-Dev.gdb'
    param_input_point_id = arcpy.Parameter()
    param_input_point_id.value = None
    param_input_line_id = arcpy.Parameter()
    param_input_line_id.value = '46'
    param_input_polygon_id = arcpy.Parameter()
    param_input_polygon_id.value = None
    param_justification = arcpy.Parameter()
    param_justification.value = 'Test rationale'
    param_undo = arcpy.Parameter()
    param_undo.value = 'false'
    parameters = [param_geodatabase, param_input_point_id, param_input_line_id, param_input_polygon_id,
                  param_justification, param_undo]
    fbdui.runFlagBadDataUsingIDTool(parameters, None)
