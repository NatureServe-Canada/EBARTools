# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2020 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: FlagBadDataUsingRangeTool.py
# ArcGIS Python tool for using reviewed range to identify and flag bad input data

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import EBARUtils
import arcpy
import datetime

class FlagBadDataUsingRangeTool:
    """Use reviewed range to identify and flag bad input data"""
    def __init__(self):
        pass

    def runFlagBadDataUsingRangeTool(self, parameters, messages):
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
        param_range_map_id = parameters[1].valueAsText
        range_map_id = int(param_range_map_id)

        # use passed geodatabase as workspace (still seems to go to default geodatabase)
        arcpy.env.workspace = param_geodatabase

        # get table name prefix (needed for joined tables and feature classes in enterprise geodatabases)
        table_name_prefix = EBARUtils.getTableNamePrefix(param_geodatabase)

	    # get primary and secondary species
        species_id, species_ids = EBARUtils.getSpeciesForRangeMap(param_geodatabase, range_map_id)
        if not species_id:
            EBARUtils.displayMessage(messages, 'ERROR: Range Map not found')
            # terminate with error
            return
            #raise arcpy.ExecuteError

        # select ecoshapes using RangeMapID
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/Ecoshape', 'ecoshape_layer')
        arcpy.SelectLayerByAttribute_management('ecoshape_layer', 'NEW_SELECTION',
                                                'EcoshapeID IN (SELECT EcoshapeID FROM RangeMapEcoshape WHERE ' +
                                                'RangeMapID = ' + str(range_map_id) + ')')

        # process points
        # select all points for species and buffer
        EBARUtils.displayMessage(messages, 'Buffering Input Points')
        temp_point_buffer = EBARUtils.inputSelectAndBuffer(param_geodatabase, 'InputPoint', range_map_id,
                                                           table_name_prefix, species_ids, species_id, start_time)
        arcpy.MakeFeatureLayer_management(temp_point_buffer, 'point_layer')
        EBARUtils.displayMessage(messages, 'Marking as Bad Data any Input Points that do not intersect range')
        # select any that don't intersect range
        arcpy.SelectLayerByLocation_management('point_layer', 'INTERSECT', 'ecoshape_layer', None, 'NEW_SELECTION',
                                               'INVERT')
        # create InputFeedback record with BadData flag
        with arcpy.da.SearchCursor('point_layer', ['InputPointID']) as cursor:
            points_found = 0
            for row in EBARUtils.searchCursor(cursor):
                points_found += 1
                with arcpy.da.InsertCursor(param_geodatabase + '/InputFeedback',
                                           ['InputPointID', 'InputFeedbackNotes', 'BadData']) as insert_cursor:
                    insert_cursor.insertRow([row['InputPointID'], 'Not in range with RangeMapID ' + str(range_map_id),
                                             1])
            if points_found > 0:
                del row

        ## process lines
        ## select all lines for species and buffer
        #EBARUtils.displayMessage(messages, 'Buffering Input Lines')
        #temp_line_buffer = EBARUtils.inputSelectAndBuffer(param_geodatabase, 'InputLine', range_map_id,
        #                                                  table_name_prefix, species_ids, species_id, start_time)

        ## process polygons
        ## select all polygons for species
        #EBARUtils.displayMessage(messages, 'Selecting Input Polygons')
        #input_polygon_layer = EBARUtils.inputSelectAndBuffer(param_geodatabase, 'InputPolygon', range_map_id,
        #                                                     table_name_prefix, species_ids, species_id, start_time)

        # temp clean-up
        if arcpy.Exists(temp_point_buffer):
            arcpy.Delete_management(temp_point_buffer)
        #if arcpy.Exists(temp_line_buffer):
        #    arcpy.Delete_management(temp_line_buffer)

        # results
        EBARUtils.displayMessage(messages, str(points_found) + ' points flagged as BadData')

        # end time
        end_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'End time: ' + str(end_time))
        elapsed_time = end_time - start_time
        EBARUtils.displayMessage(messages, 'Elapsed time: ' + str(elapsed_time))
        return


# controlling process
if __name__ == '__main__':
    fbdur = FlagBadDataUsingRangeTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:/GIS/EBAR/EBAR-KBA-Dev.gdb'
    param_range_map_id = arcpy.Parameter()
    param_range_map_id.value = '69'
    parameters = [param_geodatabase, param_range_map_id]
    fbdur.runFlagBadDataUsingRangeTool(parameters, None)
