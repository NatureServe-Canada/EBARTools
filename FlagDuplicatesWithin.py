# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Samantha Stefanoff
# © NatureServe Canada 2024 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: FlagDuplicatesWithin.py
# ArcGIS Python tool for flagging InputPoint/Line/Polygon records with the same SpeciesID/MaxDate/Shape(location)
# within the same DatasetSource

# Notes:
# - command-line execution only, not yet converted to an interactive tool


import sys
import arcpy
import datetime
import EBARUtils
#import FlagBadDataUsingIDTool

# parameters
param_geodatabase = 'C:/GIS/EBAR/nsc-gis-ebarkba.sde'

# redirect output to file
start_time = datetime.datetime.now()
folder = 'C:/GIS/EBAR/LogFiles/'
filename = 'FlagDuplicatesWithin' + str(start_time.year) + str(start_time.month) + str(start_time.day) + \
    str(start_time.hour) + str(start_time.minute) + str(start_time.second) + '.txt'
logfile = open(folder + filename, 'w')
sys.stdout = logfile

try:
    EBARUtils.displayMessage(None, 'Start time: ' + str(start_time))

    # get table name prefix (needed for joined tables and feature classes in enterprise geodatabases)
    table_name_prefix = EBARUtils.getTableNamePrefix(param_geodatabase)

    # get relevant DatasetSourceIDs
    dss_ids = {}
    #dss_ids[1010] = 'T'
    row = None
    with arcpy.da.SearchCursor(param_geodatabase + '/DatasetSource', ['DatasetSourceID', 'DatasetSourceType'],
                               'CDCJurisdictionID IS NULL AND DatasetSourceID IN (1051,1010,5)') as cursor:
                               #'CDCJurisdictionID IS NULL AND DatasetSourceID NOT IN (1039,8,908,873,1034,1109,20,1028,1038,1050,1021,994,1129,10,1056,1057,1058,1059,1060,1061,1062,1063,961,914,1122,878,1124,1120,1136,1123,1137,1126,1127,1138,1139,1140,1121,1145,1141,1142,1144,1128,1143,1096,1097,6,1146,887,907,1,1051,1010,5)') as cursor:
                               #'DuplicatePriority IS NOT NULL AND CDCJurisdictionID IS NULL') as cursor:
        for row in EBARUtils.searchCursor(cursor):
            dss_ids[row['DatasetSourceID']] = row['DatasetSourceType']
            #dss_ids.append()
    if row:
        del row
    del cursor

    # # create instance of Flag tool for doing flagging
    # fbdui = FlagBadDataUsingIDTool.FlagBadDataUsingIDTool()

    # create table to store IDs for external flagging
    temp_dups_within = 'TempDupsWithin' + str(start_time.year) + str(start_time.month) + \
        str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
    arcpy.CreateTable_management(param_geodatabase, temp_dups_within)
    temp_dups_within = param_geodatabase + '/' + temp_dups_within
    arcpy.AddField_management(temp_dups_within, 'InputPointID', 'LONG')
    arcpy.AddField_management(temp_dups_within, 'InputLineID', 'LONG')
    arcpy.AddField_management(temp_dups_within, 'InputPolygonID', 'LONG')

    with arcpy.da.InsertCursor(temp_dups_within, ['InputPointID', 'InputLineID', 'InputPolygonID']) as insert_cursor:
        # loop dss_ids
        for dss_id in dss_ids.keys():
            EBARUtils.displayMessage(None, 'Checking DatasetSourceID ' + str(dss_id))

            # separate input feature classes for points, lines, polygons
            input_fcname = 'InputPoint'
            if dss_ids[dss_id] == 'L':
                input_fcname = 'InputLine'
            elif dss_ids[dss_id] == 'P':
                input_fcname = 'InputPolygon'
            arcpy.MakeFeatureLayer_management(param_geodatabase + '/' + input_fcname, 'input_lyr',
                                              'InputDatasetID IN (SELECT InputDatasetID FROM InputDataset WHERE ' + \
                                              'DatasetSourceID = ' + str(dss_id) + ')' + ' AND MaxDate IS NOT NULL')

            # get list of species for just the current DatasetSource
            species_ids = []
            #species_ids.append(15968)
            row = None
            with arcpy.da.SearchCursor('input_lyr', ['SpeciesID'], sql_clause=('DISTINCT SpeciesID',
                                                                               'ORDER BY SpeciesID')) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    species_ids.append(row['SpeciesID'])
            if row:
                del row
            del cursor
                
            arcpy.Delete_management('input_lyr')

            # loop species_ids
            for species_id in species_ids:
                EBARUtils.displayMessage(None, 'Checking SpeciesID ' + str(species_id))

                # select one species
                # arcpy.SelectLayerByAttribute_management('input_lyr', 'NEW_SELECTION', 'SpeciesID = ' + str(species_id))
                arcpy.MakeFeatureLayer_management(param_geodatabase + '/' + input_fcname, 'input_lyr' + str(species_id),
                                                  'InputDatasetID IN (SELECT InputDatasetID FROM InputDataset WHERE ' + \
                                                  'DatasetSourceID = ' + str(dss_id) + ')' + ' AND MaxDate IS NOT NULL' + \
                                                  ' AND SpeciesID = ' + str(species_id))

                # find duplicates
                temp_dups = param_geodatabase + '/TempDups' + str(start_time.year) + str(start_time.month) + \
                    str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
                arcpy.FindIdentical_management('input_lyr' + str(species_id), temp_dups, ['MaxDate', 'Shape'],
                                               output_record_option='ONLY_DUPLICATES')

                # loop duplicates
                result = arcpy.GetCount_management(temp_dups)
                if int(result[0]) > 0:
                    row = None
                    with arcpy.da.SearchCursor(temp_dups, ['IN_FID', 'FEAT_SEQ'],
                                            sql_clause=(None, 'ORDER BY FEAT_SEQ ASC, IN_FID DESC')) as cursor:
                        first_in_seq = True
                        for row in EBARUtils.searchCursor(cursor):
                            if not first_in_seq:
                                if row['FEAT_SEQ'] == cur_seq:
                                    # need EBAR's input feature ID for flagging
                                    input_point_id = None
                                    input_line_id = None
                                    input_polygon_id = None
                                    fid_row = None
                                    with arcpy.da.SearchCursor('input_lyr' + str(species_id), [input_fcname + 'ID'],
                                                               'OBJECTID = ' + str(row['IN_FID'])) as fid_cursor:
                                        for fid_row in EBARUtils.searchCursor(fid_cursor):
                                            if input_fcname == 'InputPoint':
                                                input_point_id = fid_row[input_fcname + 'ID']
                                                EBARUtils.displayMessage(None, 'Flagging duplicate with InputPointID '+
                                                                        str(input_point_id))
                                            if input_fcname == 'InputLine':
                                                input_line_id = fid_row[input_fcname + 'ID']
                                                EBARUtils.displayMessage(None, 'Flagging duplicate with InputLineID ' +
                                                                        str(input_line_id))
                                            if input_fcname == 'InputPolygon':
                                                input_polygon_id = fid_row[input_fcname + 'ID']
                                                EBARUtils.displayMessage(None, 'Flagging duplicate with InputPolygonID ' +
                                                                        str(input_polygon_id))
                                    if fid_row:
                                        del fid_row
                                    del fid_cursor
                                    # store ID for external flagging
                                    insert_cursor.insertRow([input_point_id, input_line_id, input_polygon_id])
                                    # # create BadData record, create InputFeedback record, delete Input record using ID
                                    # param_gdb = arcpy.Parameter()
                                    # param_gdb.value = param_geodatabase
                                    # param_input_point_id = arcpy.Parameter()
                                    # param_input_point_id.value = input_point_id
                                    # param_input_line_id = arcpy.Parameter()
                                    # param_input_line_id.value = input_line_id
                                    # param_input_polygon_id = arcpy.Parameter()
                                    # param_input_polygon_id.value = input_polygon_id
                                    # param_justification = arcpy.Parameter()
                                    # param_justification.value = 'Duplicate within DatasetSource'
                                    # param_undo = arcpy.Parameter()
                                    # param_undo.value = 'false'
                                    # parameters = [param_gdb, param_input_point_id, param_input_line_id, 
                                    #               param_input_polygon_id, param_justification, param_undo]
                                    # fbdui.runFlagBadDataUsingIDTool(parameters, None, quiet=True)
                                else:
                                    first_in_seq = True
                            if first_in_seq:
                                # keep first (newest) within each seq
                                cur_seq = row['FEAT_SEQ']
                                first_in_seq = False
                    if row:
                        del row
                    del cursor

                arcpy.Delete_management(temp_dups)
                arcpy.Delete_management('input_lyr' + str(species_id))

    del insert_cursor

    end_time = datetime.datetime.now()
    EBARUtils.displayMessage(None, 'End time: ' + str(datetime.datetime.now()))
    EBARUtils.displayMessage(None, 'Elapsed time: ' + str(end_time - start_time))

finally:
    logfile.close()
    sys.stdout = sys.__stdout__
