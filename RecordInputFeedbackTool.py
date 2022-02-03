# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Gabrielle Miller
# © NatureServe Canada 2022 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: RecordInputFeedbackTool.py
# ArcGIS Python tool for adding or removing records from the InputFeedback table

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import EBARUtils
import arcpy
import datetime


class RecordInputFeedbackTool:
    """Add or remove records from the InputFeedback table"""
    def __init__(self):
        pass

    def runRecordInputFeedbackTool(self, parameters, messages):
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
        param_notes = parameters[4].valueAsText
        param_exclude_from_range_map_id = parameters[5].valueAsText
        param_exclude_from_all_range_maps = parameters[6].valueAsText
        param_justification = parameters[7].valueAsText
        param_undo = parameters[8].valueAsText
        # need one ID
        id_count = 0
        if param_input_point_id:
            id_count += 1
            input_table = param_geodatabase + '/InputPoint'
            id_field = 'InputPointID'
            id_value = param_input_point_id
        if param_input_line_id:
            id_count += 1
            input_table = param_geodatabase + '/InputLine'
            id_field = 'InputLineID'
            id_value = param_input_line_id
        if param_input_polygon_id:
            id_count += 1
            input_table = param_geodatabase + '/InputPolygon'
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
        # need notes, or one exclude option plus justication, or one exclude option plus undo
        if param_notes:
            if (param_exclude_from_range_map_id or param_exclude_from_all_range_maps == 'true' or
                param_justification or param_undo):
                EBARUtils.displayMessage(messages, 'ERROR: Please provide notes or exclusions, not both')
                # terminate with error
                return
            if param_undo == 'true':
                EBARUtils.displayMessage(messages, 'ERROR: Notes can only be replaced, not undone')
                # terminate with error
                return
        else:
            if not (param_exclude_from_range_map_id or param_exclude_from_all_range_maps == 'true'):
                EBARUtils.displayMessage(messages, 'ERROR: Please provide notes or exclusions')
                # terminate with error
                return
            if param_exclude_from_range_map_id and param_exclude_from_all_range_maps == 'true':
                EBARUtils.displayMessage(messages, 'ERROR: Please provide only one exclusion')
                # terminate with error
                return
            if param_undo == 'false' and  not param_justification:
                EBARUtils.displayMessage(messages, 'ERROR: Please provide a justification')
                # terminate with error
                return

        # check for record
        arcpy.MakeFeatureLayer_management(input_table, 'input_layer', id_field + ' = ' + id_value)
        result = arcpy.GetCount_management('input_layer')
        if int(result[0]) == 0:
            EBARUtils.displayMessage(messages, 'ERROR: input record with specified ID not found')
            # terminate with error
            return

        if param_undo == 'false':
            # create InputFeedback record
            EBARUtils.displayMessage(messages, 'Saving InputFeedback  record')
            exclude_from_all_range_maps = False
            if param_exclude_from_all_range_maps == 'true':
                exclude_from_all_range_maps = True
            with arcpy.da.InsertCursor(param_geodatabase + '/InputFeedback',
                                       [id_field, 'Notes', 'ExcludeFromRangeMapID', 'ExcludeFromAllRangeMaps',
                                        'Justification']) as insert_cursor:
                insert_cursor.insertRow([id_value, param_notes, param_exclude_from_range_map_id,
                                         exclude_from_all_range_maps, param_justification])
        else:
            # check for record, including exclude if provided
            arcpy.MakeFeatureLayer_management(param_geodatabase + '/InputFeedback', 'input_feedback_layer',
                                              id_field + ' = ' + id_value)
            result = arcpy.GetCount_management('input_feedback_layer')
            if int(result[0]) == 0:
                EBARUtils.displayMessage(messages, 'ERROR: InputFeedback record with specified ID not found')
                # terminate with error
                return

            # delete InputFeedback record
            EBARUtils.displayMessage(messages, 'Deleting InputFeedback record')
            with arcpy.da.UpdateCursor(param_geodatabase + '/InputFeedback',
                                       [id_field], 'Bad' + id_field + ' = ' + id_value) as update_cursor:
                update_row = None
                for update_row in update_cursor:
                    update_cursor.deleteRow()
                if update_row:
                    del update_row

        # end time
        end_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'End time: ' + str(end_time))
        elapsed_time = end_time - start_time
        EBARUtils.displayMessage(messages, 'Elapsed time: ' + str(elapsed_time))
        return


# controlling process
if __name__ == '__main__':
    rif = RecordInputFeedbackTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:/GIS/EBAR/EBAR-KBA-Dev.gdb'
    param_input_point_id = arcpy.Parameter()
    param_input_point_id.value = None
    param_input_line_id = arcpy.Parameter()
    param_input_line_id.value = '40'
    param_input_polygon_id = arcpy.Parameter()
    param_input_polygon_id.value = None
    param_notes = arcpy.Parameter()
    param_notes.value = None
    param_exclude_from_range_map_id = arcpy.Parameter()
    param_exclude_from_range_map_id.value = '123'
    param_exclude_from_all_range_maps = arcpy.Parameter()
    param_exclude_from_all_range_maps.value = 'false'
    param_justification = arcpy.Parameter()
    param_justification.value = 'Test rationale'
    param_undo = arcpy.Parameter()
    param_undo.value = 'false'
    parameters = [param_geodatabase, param_input_point_id, param_input_line_id, param_input_polygon_id, param_notes,
                  param_justification, param_exclude_from_range_map_id, param_exclude_from_all_range_maps, param_undo]
    rif.runFlagBadDataUsingIDTool(parameters, None)
