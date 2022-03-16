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
        EBARUtils.displayMessage(messages, 'RangeMapID: ' + param_range_map_id)
        range_map_id = int(param_range_map_id)

        # use passed geodatabase as workspace (still seems to go to default geodatabase)
        arcpy.env.workspace = param_geodatabase

        # get table name prefix (needed for joined tables and feature classes in enterprise geodatabases)
        table_name_prefix = EBARUtils.getTableNamePrefix(param_geodatabase)

	    # get primary and secondary species
        species_id, species_ids, scope = EBARUtils.getSpeciesAndScopeForRangeMap(param_geodatabase, range_map_id)
        if not species_id:
            EBARUtils.displayMessage(messages, 'ERROR: Range Map not found')
            # terminate with error
            return
            #raise arcpy.ExecuteError

        # # don't allow National scope
        # if scope == 'N':
        #     EBARUtils.displayMessage(messages, 'ERROR: Only range maps with Global or North American scope allowed')
        #     # terminate with error
        #     return
        #     #raise arcpy.ExecuteError

        # select range ecoshapes using RangeMapID
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/Ecoshape', 'range_ecoshape_layer')
        arcpy.SelectLayerByAttribute_management('range_ecoshape_layer', 'NEW_SELECTION',
                                                'EcoshapeID IN (SELECT EcoshapeID FROM RangeMapEcoshape WHERE ' +
                                                'RangeMapID = ' + str(range_map_id) + ')')
        # select subset of all ecoshapes for National (Canadian) scope
        if scope == 'N':
            arcpy.MakeFeatureLayer_management(param_geodatabase + '/Ecoshape', 'nat_ecoshape_layer')
            arcpy.SelectLayerByAttribute_management('nat_ecoshape_layer', 'NEW_SELECTION',
                                                    'JurisdictionID IN ' + EBARUtils.national_jur_ids)

        # process points
        # select all points for species and buffer
        EBARUtils.displayMessage(messages, 'Buffering Input Points')
        temp_point_buffer = EBARUtils.inputSelectAndBuffer(param_geodatabase, 'InputPoint', range_map_id,
                                                           table_name_prefix, species_ids, species_id, start_time)
        EBARUtils.displayMessage(messages, 'Appending to BadInputPoint any InputPoint that does not intersect range')
        arcpy.MakeFeatureLayer_management(temp_point_buffer, 'point_layer')
        # select any that don't intersect range
        arcpy.SelectLayerByLocation_management('point_layer', 'INTERSECT', 'range_ecoshape_layer', None,
                                               'NEW_SELECTION', 'INVERT')
        # subset points for national
        if scope == 'N':
            arcpy.SelectLayerByLocation_management('point_layer', 'INTERSECT', 'nat_ecoshape_layer', None,
                                                   'SUBSET_SELECTION')
        # select same set of original InputPoints
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/InputPoint', 'original_points')
        arcpy.SelectLayerByLocation_management('original_points', 'INTERSECT', 'point_layer')
        result = arcpy.GetCount_management('original_points')
        points_found = int(result[0])
        if points_found > 0:
            # create InputFeedback records
            with arcpy.da.SearchCursor('original_points', ['InputPointID']) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    with arcpy.da.InsertCursor(param_geodatabase + '/InputFeedback',
                                               ['BadInputPointID', 'InputFeedbackNotes']) as insert_cursor:
                        insert_cursor.insertRow([row['InputPointID'], 'Not in range with RangeMapID ' +
                                                 str(range_map_id)])
                del row
            # append to Bad and delete original
            #arcpy.Append_management('original_points', param_geodatabase + '/BadInputPoint', 'TEST')
            EBARUtils.appendUsingCursor('original_points', param_geodatabase + '/BadInputPoint')
            EBARUtils.displayMessage(messages, 'Deleting original points')
            arcpy.DeleteRows_management('original_points')

        # process lines
        # select all lines for species and buffer
        EBARUtils.displayMessage(messages, 'Buffering Input Lines')
        temp_line_buffer = EBARUtils.inputSelectAndBuffer(param_geodatabase, 'InputLine', range_map_id,
                                                          table_name_prefix, species_ids, species_id, start_time)
        EBARUtils.displayMessage(messages, 'Appending to BadInputLine any InputLine that does not intersect range')
        arcpy.MakeFeatureLayer_management(temp_line_buffer, 'line_layer')
        # select any that don't intersect range
        arcpy.SelectLayerByLocation_management('line_layer', 'INTERSECT', 'range_ecoshape_layer', None,
                                               'NEW_SELECTION', 'INVERT')
        # subset lines for national
        if scope == 'N':
            arcpy.SelectLayerByLocation_management('line_layer', 'INTERSECT', 'nat_ecoshape_layer', None,
                                                   'SUBSET_SELECTION')
        # select same set of original InputLines
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/InputLine', 'original_lines')
        arcpy.SelectLayerByLocation_management('original_lines', 'INTERSECT', 'line_layer')
        result = arcpy.GetCount_management('original_lines')
        lines_found = int(result[0])
        if lines_found > 0:
            # create InputFeedback records
            with arcpy.da.SearchCursor('original_lines', ['InputLineID']) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    with arcpy.da.InsertCursor(param_geodatabase + '/InputFeedback',
                                               ['BadInputLineID', 'InputFeedbackNotes']) as insert_cursor:
                        insert_cursor.insertRow([row['InputLineID'], 'Not in range with RangeMapID ' +
                                                 str(range_map_id)])
                del row
            # append to Bad and delete original
            #arcpy.Append_management('original_lines', param_geodatabase + '/BadInputLine', 'TEST')
            EBARUtils.appendUsingCursor('original_lines', param_geodatabase + '/BadInputLine')
            EBARUtils.displayMessage(messages, 'Deleting original lines')
            arcpy.DeleteRows_management('original_lines')

        # process polygons
        # select all polygons for species
        # (different than above because it works on a selection of full dataset,
        # not a buffered copy for relevant species only)
        EBARUtils.displayMessage(messages, 'Selecting Input Polygons')
        input_polygon_layer = EBARUtils.inputSelectAndBuffer(param_geodatabase, 'InputPolygon', range_map_id,
                                                             table_name_prefix, species_ids, species_id, start_time)
        EBARUtils.displayMessage(messages, 'Appending to BadInputPolygon any InputPolygon that does not intersect range')
        if len(arcpy.Describe(input_polygon_layer).FIDSet) > 0:
            # select any that don't intersect range
            arcpy.SelectLayerByLocation_management(input_polygon_layer, 'INTERSECT', 'range_ecoshape_layer', None,
                                                   'SUBSET_SELECTION', 'INVERT')
            # subset polygons for national
            if scope == 'N':
                arcpy.SelectLayerByLocation_management(input_polygon_layer, 'INTERSECT', 'nat_ecoshape_layer', None,
                                                       'SUBSET_SELECTION')
            polygons_found = len(arcpy.Describe(input_polygon_layer).FIDSet)
            if polygons_found > 0:
                # create InputFeedback records
                with arcpy.da.SearchCursor(input_polygon_layer, ['InputPolygonID']) as cursor:
                    for row in EBARUtils.searchCursor(cursor):
                        with arcpy.da.InsertCursor(param_geodatabase + '/InputFeedback',
                                                   ['BadInputPolygonID', 'InputFeedbackNotes']) as insert_cursor:
                            insert_cursor.insertRow([row['InputPolygonID'], 'Not in range with RangeMapID ' +
                                                     str(range_map_id)])
                    del row
                # append to Bad and delete original
                #arcpy.Append_management(input_polygon_layer, param_geodatabase + '/BadInputPolygon', 'TEST')
                EBARUtils.appendUsingCursor(input_polygon_layer, param_geodatabase + '/BadInputPolygon')
                EBARUtils.displayMessage(messages, 'Deleting original polygons')
                arcpy.DeleteRows_management(input_polygon_layer)

        # temp clean-up
        if arcpy.Exists(temp_point_buffer):
            arcpy.Delete_management(temp_point_buffer)
        if arcpy.Exists(temp_line_buffer):
            arcpy.Delete_management(temp_line_buffer)

        # results
        EBARUtils.displayMessage(messages, str(points_found) + ' Input Points flagged as Bad Data')
        EBARUtils.displayMessage(messages, str(lines_found) + ' Input Lines flagged as Bad Data')
        EBARUtils.displayMessage(messages, str(polygons_found) + ' Input Polygons flagged as Bad Data')

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
    param_range_map_id.value = '34'
    parameters = [param_geodatabase, param_range_map_id]
    fbdur.runFlagBadDataUsingRangeTool(parameters, None)
