# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Samantha Stefanoff, Christine Terwissen
# © NatureServe Canada 2025 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: FlagBadDataUsingRangeTool.py
# ArcGIS Python tool for using reviewed range to identify and flag input data that is in ecoshapes removed by expert
# review

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import arcpy.management
import EBARUtils
import arcpy
import datetime
import FlagBadDataUsingIDTool


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
        species_id, species_ids, scope, range_date, publish, include_in_download_table = \
            EBARUtils.getDetailsForRangeMap(param_geodatabase, range_map_id)
        if not species_id:
            EBARUtils.displayMessage(messages, 'ERROR: Range Map not found')
            # terminate with error
            return
        # else:
        #     # DEBUG
        #     EBARUtils.displayMessage(messages, 'SpeciesID: ' + str(species_id))

        # only allow fully expert reviewed (high quality) range
        high_quality = False
        if publish and include_in_download_table:
            if publish == 1 and include_in_download_table == 1:
                high_quality = True
        if not high_quality:
            EBARUtils.displayMessage(messages,
                                     'ERROR: Range Map must be fully reviewed (i.e., published and of high quality)')
            # terminate with error
            return

        # # only allow published range
        # published = False
        # if publish:
        #     if publish == 1:
        #         published = True
        # if not published:
        #     EBARUtils.displayMessage(messages,
        #                              'ERROR: Range Map must be published')
        #     # terminate with error
        #     return

        # # get all RangeMapIDs for species (primary + secondary) and scope
        # range_map_ids = EBARUtils.getRelatedRangeMapIDs(param_geodatabase, range_map_id)

        # # don't allow National scope
        # if scope == 'N':
        #     EBARUtils.displayMessage(messages, 'ERROR: Only range maps with Global or North American scope allowed')
        #     # terminate with error
        #     return
        #     #raise arcpy.ExecuteError

        # # select removed range ecoshapes using RangeMapID
        # arcpy.MakeFeatureLayer_management(param_geodatabase + '/Ecoshape', 'removed_ecoshape_layer',
        #                                   'EcoshapeID IN (SELECT EcoshapeID FROM RangeMapEcoshape WHERE ' +
        #                                   'RangeMapID IN (' + range_map_ids + ') AND Presence IS NULL)')
        # # arcpy.SelectLayerByAttribute_management('removed_ecoshape_layer', 'NEW_SELECTION',
        # #                                         'EcoshapeID IN (SELECT EcoshapeID FROM RangeMapEcoshape WHERE ' +
        # #                                         'RangeMapID = ' + str(range_map_id) + ' AND Presence IS NULL)')
        # result = arcpy.management.GetCount('removed_ecoshape_layer')
        # if int(result[0]) == 0:
        #     # display message and stop
        #     EBARUtils.displayMessage(messages, 'ERROR: Range Map has no Ecoshapes that were removed by expert review')
        #     return

        # select range ecoshapes using RangeMapID
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/Ecoshape', 'range_ecoshape_layer',
                                          'EcoshapeID IN (SELECT EcoshapeID FROM RangeMapEcoshape WHERE ' +
                                          'RangeMapID = ' + param_range_map_id + ' AND Presence IS NOT NULL)')
        result = arcpy.management.GetCount('range_ecoshape_layer')
        if int(result[0]) == 0:
            # display message and stop
            EBARUtils.displayMessage(messages, 'ERROR: Range Map has no Ecoshapes')
            return

        # select subsets of all ecoshapes for National (Canadian) scope
        if scope == 'N':
            EBARUtils.displayMessage(messages, 'Selecting subset of Ecoshapes for National (Canadian) scope')
            arcpy.MakeFeatureLayer_management(param_geodatabase + '/Ecoshape', 'nat_ecoshape_layer',
                                              'JurisdictionID IN ' + EBARUtils.national_jur_ids)
            # also need non-Canadian (international) ecoshapes
            arcpy.MakeFeatureLayer_management(param_geodatabase + '/Ecoshape', 'intl_ecoshape_layer',
                                              'JurisdictionID NOT IN ' + EBARUtils.national_jur_ids)

        # use related tool for doing actual flagging
        fbdui = FlagBadDataUsingIDTool.FlagBadDataUsingIDTool()

        # process points
        # select all points acquired before range map was generated
        EBARUtils.displayMessage(messages, 'Buffering Input Points for primary species')
        temp_point_buffer = EBARUtils.inputSelectAndBuffer(param_geodatabase, 'InputPoint', range_map_id,
                                                           table_name_prefix, str(species_id), start_time, range_date)
        EBARUtils.displayMessage(messages, 'Flagging any InputPoint that does not intersect range')
        arcpy.MakeFeatureLayer_management(temp_point_buffer, 'point_layer')
        # select any that don't intersect range ecoshapes
        arcpy.SelectLayerByLocation_management('point_layer', 'INTERSECT', 'range_ecoshape_layer', None,
                                               'NEW_SELECTION', 'INVERT')
        points_found = int(arcpy.GetCount_management('point_layer')[0])
        # subset points for national
        if scope == 'N':
            arcpy.SelectLayerByLocation_management('point_layer', 'INTERSECT', 'nat_ecoshape_layer', None,
                                                   'SUBSET_SELECTION')
            points_found = int(arcpy.GetCount_management('point_layer')[0])
            if points_found > 0:
                arcpy.SelectLayerByLocation_management('point_layer', 'INTERSECT', 'intl_ecoshape_layer',
                                                       None, 'SUBSET_SELECTION', 'INVERT')
                points_found = int(arcpy.GetCount_management('point_layer')[0])
        # select same set of original InputPoints
        if points_found > 0:
            input_point_ids = ''
            with arcpy.da.SearchCursor('point_layer', ['InputPointID']) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    if len(input_point_ids) > 0:
                        input_point_ids += ','
                    input_point_ids += str(row['InputPointID'])
            del row, cursor
            arcpy.MakeFeatureLayer_management(param_geodatabase + '/InputPoint', 'original_points',
                                              'InputPointID IN (' + input_point_ids + ')')
            with arcpy.da.SearchCursor('original_points', ['InputPointID']) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    # # create InputFeedback, append to Bad, delete original
                    # EBARUtils.displayMessage(messages, 'Flagging InputPointID ' + str(row['InputPointID']))
                    # param_gdb = arcpy.Parameter()
                    # param_gdb.value = param_geodatabase
                    # param_input_point_id = arcpy.Parameter()
                    # param_input_point_id.value = str(row['InputPointID'])
                    # param_input_line_id = arcpy.Parameter()
                    # param_input_line_id.value = None
                    # param_input_polygon_id = arcpy.Parameter()
                    # param_input_polygon_id.value = None
                    # param_justification = arcpy.Parameter()
                    # param_justification.value = 'Record flagged as bad because it is within an expert removed ecoshape'
                    # param_undo = arcpy.Parameter()
                    # param_undo.value = 'false'
                    # parameters = [param_gdb, param_input_point_id, param_input_line_id, param_input_polygon_id,
                    #               param_justification, param_undo]
                    # fbdui.runFlagBadDataUsingIDTool(parameters, None)
                    # create InputFeedback
                    EBARUtils.displayMessage(messages,
                                             'Creating InputFeedback for InputPointID ' + str(row['InputPointID']))
                    # with arcpy.da.InsertCursor(param_geodatabase + '/InputFeedback',
                    #                            ['BadInputPointID', 'Justification']) as insert_cursor:
                    #     insert_cursor.insertRow([row['InputPointID'], 'Not in reviewed range with RangeMapID ' +
                    #                              str(range_map_id)])
                    with arcpy.da.InsertCursor(param_geodatabase + '/InputFeedback',
                                               ['InputPointID', 'Justification', 'ExcludeFromAllRangeMaps']) as insert_cursor:
                        insert_cursor.insertRow([row['InputPointID'], 'Not in reviewed range with RangeMapID ' +
                                                 str(range_map_id), 1])
                    del insert_cursor
            del row, cursor
            # # append to Bad, delete original
            # EBARUtils.displayMessage(messages, 'Appending BadInputPoint(s)')
            # EBARUtils.appendUsingCursor('original_points', param_geodatabase + '/BadInputPoint')
            # EBARUtils.displayMessage(messages, 'Deleting original point(s)')
            # arcpy.DeleteRows_management('original_points')

        # process lines
        # select all lines acquired before range map was generated
        EBARUtils.displayMessage(messages, 'Buffering Input Lines for primary species')
        temp_line_buffer = EBARUtils.inputSelectAndBuffer(param_geodatabase, 'InputLine', range_map_id,
                                                          table_name_prefix, str(species_id), start_time, range_date)
        EBARUtils.displayMessage(messages, 'Flagging any InputLine that does not intersect range')
        arcpy.MakeFeatureLayer_management(temp_line_buffer, 'line_layer')
        # select any that don't intersect range
        arcpy.SelectLayerByLocation_management('line_layer', 'INTERSECT', 'range_ecoshape_layer', None,
                                               'NEW_SELECTION', 'INVERT')
        lines_found = int(arcpy.GetCount_management('line_layer')[0])
        # subset lines for national
        if scope == 'N':
            arcpy.SelectLayerByLocation_management('line_layer', 'INTERSECT', 'nat_ecoshape_layer', None,
                                                   'SUBSET_SELECTION')
            lines_found = int(arcpy.GetCount_management('line_layer')[0])
            if lines_found > 0:
                arcpy.SelectLayerByLocation_management('line_layer', 'INTERSECT', 'intl_ecoshape_layer', None,
                                                    'SUBSET_SELECTION', 'INVERT')
                lines_found = int(arcpy.GetCount_management('line_layer')[0])
        # select same set of original InputLines
        if lines_found > 0:
            input_line_ids = ''
            with arcpy.da.SearchCursor('line_layer', ['InputLineID']) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    if len(input_line_ids) > 0:
                        input_line_ids += ','
                    input_line_ids += str(row['InputLineID'])
            del row, cursor
            arcpy.MakeFeatureLayer_management(param_geodatabase + '/InputLine', 'original_lines',
                                              'InputLineID IN (' + input_line_ids + ')')
            with arcpy.da.SearchCursor('original_lines', ['InputLineID']) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    # # create InputFeedback, append to Bad, delete original
                    # EBARUtils.displayMessage(messages, 'Flagging InputLineID ' + str(row['InputLineID']))
                    # param_gdb = arcpy.Parameter()
                    # param_gdb.value = param_geodatabase
                    # param_input_point_id = arcpy.Parameter()
                    # param_input_point_id.value = None
                    # param_input_line_id = arcpy.Parameter()
                    # param_input_line_id.value = str(row['InputLineID'])
                    # param_input_polygon_id = arcpy.Parameter()
                    # param_input_polygon_id.value = None
                    # param_justification = arcpy.Parameter()
                    # param_justification.value = 'Record flagged as bad because it is within an expert removed ecoshape'
                    # param_undo = arcpy.Parameter()
                    # param_undo.value = 'false'
                    # parameters = [param_gdb, param_input_point_id, param_input_line_id, param_input_polygon_id,
                    #               param_justification, param_undo]
                    # fbdui.runFlagBadDataUsingIDTool(parameters, None)
                    # create InputFeedback
                    EBARUtils.displayMessage(messages,
                                             'Creating InputFeedback for InputLineID ' + str(row['InputLineID']))
                    # with arcpy.da.InsertCursor(param_geodatabase + '/InputFeedback',
                    #                            ['BadInputLineID', 'Justification']) as insert_cursor:
                    #     insert_cursor.insertRow([row['InputLineID'], 'Not in reviewed range with RangeMapID ' +
                    #                              str(range_map_id)])
                    with arcpy.da.InsertCursor(param_geodatabase + '/InputFeedback',
                                               ['InputLineID', 'Justification', 'ExcludeFromAllRangeMaps']) as insert_cursor:
                        insert_cursor.insertRow([row['InputLineID'], 'Not in reviewed range with RangeMapID ' +
                                                 str(range_map_id), 1])
                    del insert_cursor
            del row, cursor
            # # append to Bad, delete original
            # EBARUtils.displayMessage(messages, 'Appending BadInputLine(s)')
            # EBARUtils.appendUsingCursor('original_lines', param_geodatabase + '/BadInputLine')
            # EBARUtils.displayMessage(messages, 'Deleting original line(s)')
            # arcpy.DeleteRows_management('original_lines')

        # process polygons
        # select all polygons acquired before range map was generated
        # (different from above because it works on a selection of full dataset,
        # not a buffered copy for relevant species only)
        EBARUtils.displayMessage(messages, 'Selecting Input Polygons for primary species')
        input_polygon_layer = EBARUtils.inputSelectAndBuffer(param_geodatabase, 'InputPolygon', range_map_id,
                                                             table_name_prefix, str(species_id), start_time,
                                                             range_date)
        polygons_found = int(arcpy.GetCount_management(input_polygon_layer)[0])
        if polygons_found > 0:
            EBARUtils.displayMessage(messages, 'Flagging any InputPolygon that does not intersect range')
            # select any that don't intersect range
            arcpy.SelectLayerByLocation_management(input_polygon_layer, 'INTERSECT', 'range_ecoshape_layer',
                                                   None, 'SUBSET_SELECTION', 'INVERT')
            polygons_found = int(arcpy.GetCount_management(input_polygon_layer)[0])
            # subset polygons for national
            if scope == 'N':
                arcpy.SelectLayerByLocation_management(input_polygon_layer, 'INTERSECT', 'nat_ecoshape_layer', None,
                                                       'SUBSET_SELECTION')
                polygons_found = int(arcpy.GetCount_management(input_polygon_layer)[0])
                if polygons_found > 0:
                    arcpy.SelectLayerByLocation_management(input_polygon_layer, 'INTERSECT', 'intl_ecoshape_layer',
                                                           None, 'SUBSET_SELECTION', 'INVERT')
                    polygons_found = int(arcpy.GetCount_management(input_polygon_layer)[0])
            if polygons_found > 0:
                # create InputFeedback records
                with arcpy.da.SearchCursor(input_polygon_layer, ['InputPolygonID']) as cursor:
                    for row in EBARUtils.searchCursor(cursor):
                        # # create InputFeedback, append to Bad, delete original
                        # EBARUtils.displayMessage(messages, 'Flagging InputPolygonID ' + str(row['InputPolygonID']))
                        # param_gdb = arcpy.Parameter()
                        # param_gdb.value = param_geodatabase
                        # param_input_point_id = arcpy.Parameter()
                        # param_input_point_id.value = None
                        # param_input_line_id = arcpy.Parameter()
                        # param_input_line_id.value = None
                        # param_input_polygon_id = arcpy.Parameter()
                        # param_input_polygon_id.value = str(row['InputPolygonID'])
                        # param_justification = arcpy.Parameter()
                        # param_justification.value = 'Record flagged as bad because it is within an expert removed ' + \
                        #     'ecoshape'
                        # param_undo = arcpy.Parameter()
                        # param_undo.value = 'false'
                        # parameters = [param_gdb, param_input_point_id, param_input_line_id, param_input_polygon_id,
                        #               param_justification, param_undo]
                        # fbdui.runFlagBadDataUsingIDTool(parameters, None)
                        # create InputFeedback
                        EBARUtils.displayMessage(messages,
                                                 'Creating InputFeedback for InputPolygonID ' +
                                                 str(row['InputPolygonID']))
                        # with arcpy.da.InsertCursor(param_geodatabase + '/InputFeedback',
                        #                            ['BadInputPolygonID', 'Justification']) as insert_cursor:
                        #     insert_cursor.insertRow([row['InputPolygonID'], 'Not in reviewed range with RangeMapID ' +
                        #                             str(range_map_id)])
                        with arcpy.da.InsertCursor(param_geodatabase + '/InputFeedback',
                                                   ['InputPolygonID', 'Justification', 'ExcludeFromAllRangeMaps']) as insert_cursor:
                            insert_cursor.insertRow([row['InputPolygonID'], 'Not in reviewed range with RangeMapID ' +
                                                    str(range_map_id), 1])
                        del insert_cursor
                del row, cursor
                # # append to Bad, delete original
                # EBARUtils.displayMessage(messages, 'Appending BadInputPolygon(s)')
                # EBARUtils.appendUsingCursor(input_polygon_layer, param_geodatabase + '/BadInputPolygon')
                # EBARUtils.displayMessage(messages, 'Deleting original polygon(s)')
                # arcpy.DeleteRows_management(input_polygon_layer)

        # temp clean-up
        if arcpy.Exists(temp_point_buffer):
            arcpy.Delete_management(temp_point_buffer)
        if arcpy.Exists(temp_line_buffer):
            arcpy.Delete_management(temp_line_buffer)
        if arcpy.Exists('range_ecoshape_layer'):
            arcpy.Delete_management('range_ecoshape_layer')
        if arcpy.Exists('nat_ecoshape_layer'):
            arcpy.Delete_management('nat_ecoshape_layer')
        if arcpy.Exists('intl_ecoshape_layer'):
            arcpy.Delete_management('intl_ecoshape_layer')
        if arcpy.Exists('point_layer'):
            arcpy.Delete_management('point_layer')
        if arcpy.Exists('original_points'):
            arcpy.Delete_management('original_points')
        if arcpy.Exists('line_layer'):
            arcpy.Delete_management('line_layer')
        if arcpy.Exists('original_lines'):
            arcpy.Delete_management('original_lines')
        if arcpy.Exists(input_polygon_layer):
            arcpy.Delete_management(input_polygon_layer)

        # results
        # EBARUtils.displayMessage(messages, str(points_found) + ' Input Points flagged as Bad Data')
        # EBARUtils.displayMessage(messages, str(lines_found) + ' Input Lines flagged as Bad Data')
        # EBARUtils.displayMessage(messages, str(polygons_found) + ' Input Polygons flagged as Bad Data')
        EBARUtils.displayMessage(messages, str(points_found) + ' Input Points flagged to Exclude From All Range Maps')
        EBARUtils.displayMessage(messages, str(lines_found) + ' Input Lines flagged to Exclude From All Range Maps')
        EBARUtils.displayMessage(messages, str(polygons_found) + ' Input Polygons to Exclude From All Range Maps')

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
    param_geodatabase.value = 'C:/GIS/EBAR/nsc-gis-ebarkba.sde'
    param_range_map_id = arcpy.Parameter()
    for rmid in (4476,4280,4601,4604,4606,4613,4379,4605,4618,4619,4623,4627,4629,4630,4631,4632,4634,4635,4636,4637,4638,4639,4640,4641,4642,4643,4644,4645,4646,4648,4650,4651,4653,4620,4621,4654,4633,4656,4657,4665,4668,4655,4667,4669,4670,4671,4672,4673,4674,4676,4677,4678,4679,4680,4681,4683,4685,4687,4690,4691,4693,4694,4695,4696,4697,4698,4700,4734):
        param_range_map_id.value = str(rmid)
        parameters = [param_geodatabase, param_range_map_id]
        fbdur.runFlagBadDataUsingRangeTool(parameters, None)
