# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Samantha Stefanoff
# © NatureServe Canada 2024 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: FlagDuplicatesGBIFiNat.py
# ArcGIS Python tool for flagging InputPoint/Line/Polygon records with the same provider unique identifier
# across GBIF, iNaturalist.ca and iNaturalist.org DatasetSources

# Notes:
# - command-line execution only, not yet converted to an interactive tool


import sys
import arcpy
import datetime
import EBARUtils
import FlagBadDataUsingIDTool


# parameters
param_geodatabase = 'C:/GIS/EBAR/nsc-gis-ebarkba.sde'

# redirect output to file
start_time = datetime.datetime.now()
folder = 'C:/GIS/EBAR/LogFiles/'
filename = 'FlagDuplicatesGBIFiNat' + str(start_time.year) + str(start_time.month) + str(start_time.day) + \
    str(start_time.hour) + str(start_time.minute) + str(start_time.second) + '.txt'
logfile = open(folder + filename, 'w')
sys.stdout = logfile

# create instance of Flag tool for doing flagging
fbdui = FlagBadDataUsingIDTool.FlagBadDataUsingIDTool()

try:
    EBARUtils.displayMessage(None, 'Start time: ' + str(start_time))
    # priority is iNat.ca original (1110) then iNat.ca unrestricted (1010) then iNat.org (5) then GBIF (1)
    # need to process, including actual flagging, in order
    # 1. iNat.ca original vs iNat.ca unrestricted
    #  can use DatasetSourceUniqueID exact match
    #  always keep former? YES
    # 2. iNat.ca original vs iNat.org
    #  can use DatasetSourceUniqueID exact match
    #  always keep former? YES
    # 3. iNat.ca unrestricted vs iNat.org
    #  can use DatasetSourceUniqueID exact match
    #  always keep former? YES
    # 4. iNat.ca/org vs GBIF
    #  can use URI but not exact match
    #  ensure GBIF OriginalInstitutionCode is 'iNaturalist'
    #  ensure URI begins with http; extract integer after last /
    #  always keep former

    # 1/2. iNat.ca original vs iNat.ca unrestricted and iNat.org
    EBARUtils.displayMessage(None, 'Checking iNat.ca original vs iNat.ca unrestricted and iNat.org')
    # # create table to store IDs for external flagging
    # temp_dups = 'TempDups_iNatcaOrig_iNatcaUnres_iNatorg_' + str(start_time.year) + str(start_time.month) + \
    #     str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
    # arcpy.CreateTable_management(param_geodatabase, temp_dups)
    # temp_dups = param_geodatabase + '/' + temp_dups
    # arcpy.AddField_management(temp_dups, 'InputPointID', 'LONG')
    # arcpy.AddField_management(temp_dups, 'DatasetSourceUniqueID', 'TEXT')
    # with arcpy.da.InsertCursor(temp_dups, ['InputPointID', 'DatasetSourceUniqueID']) as insert_cursor:

    # loop species
    row = None
    with arcpy.da.SearchCursor(param_geodatabase + '/Species', ['SpeciesID'],
                                sql_clause=(None, 'ORDER BY SpeciesID')) as cursor:
        for row in EBARUtils.searchCursor(cursor):
            EBARUtils.displayMessage(None, 'Checking SpeciesID ' + str(row['SpeciesID']))

            # retrieve all DatasetSourceUniqueIDs for iNat.ca original
            original_ids = []
            original_row = None
            where_clause = 'InputDatasetID IN (SELECT InputDatasetID FROM InputDataset WHERE ' + \
                'DatasetSourceID = 1110)' + ' AND SpeciesID = ' + str(row['SpeciesID'])
            with arcpy.da.SearchCursor(param_geodatabase + '\InputPoint', ['DatasetSourceUniqueID'],
                                        where_clause) as original_cursor:
                for original_row in EBARUtils.searchCursor(original_cursor):
                    original_ids.append(original_row['DatasetSourceUniqueID'])
            if original_row:
                del original_row
            del original_cursor

            # retrieve each DatasetSourceUniqueID for iNat.ca unrestricted
            unrestricted_row = None
            where_clause = 'InputDatasetID IN (SELECT InputDatasetID FROM InputDataset WHERE ' + \
                'DatasetSourceID = 1010)' + ' AND SpeciesID = ' + str(row['SpeciesID'])
            with arcpy.da.SearchCursor(param_geodatabase + '\InputPoint', ['InputPointID',
                                                                            'DatasetSourceUniqueID'],
                                        where_clause) as unrestricted_cursor:
                for unrestricted_row in EBARUtils.searchCursor(unrestricted_cursor):
                    # check if in original
                    if unrestricted_row['DatasetSourceUniqueID'] in original_ids:
                        EBARUtils.displayMessage(None, 'Flagging duplicate with InputPointID ' + \
                                                    str(unrestricted_row['InputPointID']) + \
                                                    ' and DatasetSourceUniqueID ' + \
                                                    unrestricted_row['DatasetSourceUniqueID'])
                        # create BadData record, create InputFeedback record, delete Input record using ID
                        param_gdb = arcpy.Parameter()
                        param_gdb.value = param_geodatabase
                        param_input_point_id = arcpy.Parameter()
                        param_input_point_id.value = unrestricted_row['InputPointID']
                        param_input_line_id = arcpy.Parameter()
                        param_input_line_id.value = None
                        param_input_polygon_id = arcpy.Parameter()
                        param_input_polygon_id.value = None
                        param_justification = arcpy.Parameter()
                        param_justification.value = 'Duplicate with iNaturalist.ca (original coordinates for obscured records)'
                        param_undo = arcpy.Parameter()
                        param_undo.value = 'false'
                        parameters = [param_gdb, param_input_point_id, param_input_line_id, 
                                      param_input_polygon_id, param_justification, param_undo]
                        fbdui.runFlagBadDataUsingIDTool(parameters, None, quiet=True)
                        # # store ID for external flagging
                        # insert_cursor.insertRow([unrestricted_row['InputPointID'],
                        #                          unrestricted_row['DatasetSourceUniqueID']])
            if unrestricted_row:
                del unrestricted_row
            del unrestricted_cursor

            # retrieve each DatasetSourceUniqueID for iNat.org
            org_row = None
            where_clause = 'InputDatasetID IN (SELECT InputDatasetID FROM InputDataset WHERE ' + \
                'DatasetSourceID = 5)' + ' AND SpeciesID = ' + str(row['SpeciesID'])
            with arcpy.da.SearchCursor(param_geodatabase + '\InputPoint', ['InputPointID',
                                                                            'DatasetSourceUniqueID'],
                                        where_clause) as org_cursor:
                for org_row in EBARUtils.searchCursor(org_cursor):
                    # check if in original
                    if org_row['DatasetSourceUniqueID'] in original_ids:
                        EBARUtils.displayMessage(None, 'Flagging duplicate with InputPointID ' + \
                                                    str(org_row['InputPointID']) + \
                                                    ' and DatasetSourceUniqueID ' + \
                                                    org_row['DatasetSourceUniqueID'])
                        # create BadData record, create InputFeedback record, delete Input record using ID
                        param_gdb = arcpy.Parameter()
                        param_gdb.value = param_geodatabase
                        param_input_point_id = arcpy.Parameter()
                        param_input_point_id.value = org_row['InputPointID']
                        param_input_line_id = arcpy.Parameter()
                        param_input_line_id.value = None
                        param_input_polygon_id = arcpy.Parameter()
                        param_input_polygon_id.value = None
                        param_justification = arcpy.Parameter()
                        param_justification.value = 'Duplicate with iNaturalist.ca (original coordinates for obscured records)'
                        param_undo = arcpy.Parameter()
                        param_undo.value = 'false'
                        parameters = [param_gdb, param_input_point_id, param_input_line_id, 
                                      param_input_polygon_id, param_justification, param_undo]
                        fbdui.runFlagBadDataUsingIDTool(parameters, None, quiet=True)
                        # # store ID for external flagging
                        # insert_cursor.insertRow([org_row['InputPointID'],
                        #                          org_row['DatasetSourceUniqueID']])
            if org_row:
                del org_row
            del org_cursor

    if row:
        del row
    del cursor

    # del insert_cursor

    end_time = datetime.datetime.now()
    EBARUtils.displayMessage(None, 'End time: ' + str(datetime.datetime.now()))
    EBARUtils.displayMessage(None, 'Elapsed time: ' + str(end_time - start_time))

finally:
    logfile.close()
    sys.stdout = sys.__stdout__
