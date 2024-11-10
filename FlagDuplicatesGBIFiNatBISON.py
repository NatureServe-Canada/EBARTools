# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Samantha Stefanoff
# © NatureServe Canada 2024 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: FlagDuplicatesGBIFiNat.py
# ArcGIS Python tool for flagging InputPoint/Line/Polygon records with the same provider unique identifier
# across BISON, GBIF, iNaturalist.ca and iNaturalist.org DatasetSources

# Notes:
# - command-line execution only, not yet converted to an interactive tool
# - each step, including deletion, must be completed before the next step


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

# # create instance of Flag tool for doing flagging
# fbdui = FlagBadDataUsingIDTool.FlagBadDataUsingIDTool()

try:
    EBARUtils.displayMessage(None, 'Start time: ' + str(start_time))
    # priority is iNat.ca original (1110) then iNat.ca unrestricted (1010) then iNat.org (5) then GBIF (1) then BISON (6)
    # need to process, including actual flagging, in order
    # 1. iNat.ca original vs iNat.ca unrestricted and iNat.org
    #  can use DatasetSourceUniqueID exact match
    #  always keep former? YES
    # 2. iNat.ca unrestricted vs iNat.org
    #  can use DatasetSourceUniqueID exact match
    #  always keep former? YES
    # 3. GBIF vs BISON
    #  can use DatasetSourceUniqueID exact match
    #  always keep former? YES
    # 4. iNat.ca/org vs GBIF
    #  can use URI but not exact match
    #  ensure GBIF OriginalInstitutionCode is 'iNaturalist'
    #  ensure URI begins with http; extract integer after last /
    #  always keep former

    # # 1. iNat.ca original vs iNat.ca unrestricted and iNat.org
    # EBARUtils.displayMessage(None, 'Checking iNat.ca original vs iNat.ca unrestricted and iNat.org')
    # # create table to store IDs for external flagging
    # temp_dups = 'TempDups_iNatcaOrig_iNatcaUnres_iNatorg_' + str(start_time.year) + str(start_time.month) + \
    #     str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
    # arcpy.CreateTable_management(param_geodatabase, temp_dups)
    # temp_dups = param_geodatabase + '/' + temp_dups
    # arcpy.AddField_management(temp_dups, 'InputPointID', 'LONG')
    # arcpy.AddField_management(temp_dups, 'DatasetSourceUniqueID', 'TEXT')
    # with arcpy.da.InsertCursor(temp_dups, ['InputPointID', 'DatasetSourceUniqueID']) as insert_cursor:
    #     # loop species
    #     row = None
    #     with arcpy.da.SearchCursor(param_geodatabase + '/Species', ['SpeciesID'],
    #                                 sql_clause=(None, 'ORDER BY SpeciesID')) as cursor:
    #         for row in EBARUtils.searchCursor(cursor):
    #             EBARUtils.displayMessage(None, 'Checking SpeciesID ' + str(row['SpeciesID']))

    #             # retrieve all DatasetSourceUniqueIDs for iNat.ca original
    #             original_ids = []
    #             original_row = None
    #             where_clause = 'InputDatasetID IN (SELECT InputDatasetID FROM InputDataset WHERE ' + \
    #                 'DatasetSourceID = 1110)' + ' AND SpeciesID = ' + str(row['SpeciesID'])
    #             with arcpy.da.SearchCursor(param_geodatabase + '\InputPoint', ['DatasetSourceUniqueID'],
    #                                         where_clause) as original_cursor:
    #                 for original_row in EBARUtils.searchCursor(original_cursor):
    #                     original_ids.append(original_row['DatasetSourceUniqueID'])
    #             if original_row:
    #                 del original_row
    #             del original_cursor

    #             # retrieve each DatasetSourceUniqueID for iNat.ca unrestricted
    #             unrestricted_row = None
    #             where_clause = 'InputDatasetID IN (SELECT InputDatasetID FROM InputDataset WHERE ' + \
    #                 'DatasetSourceID = 1010)' + ' AND SpeciesID = ' + str(row['SpeciesID'])
    #             with arcpy.da.SearchCursor(param_geodatabase + '\InputPoint', ['InputPointID',
    #                                                                             'DatasetSourceUniqueID'],
    #                                         where_clause) as unrestricted_cursor:
    #                 for unrestricted_row in EBARUtils.searchCursor(unrestricted_cursor):
    #                     # check if in original
    #                     if unrestricted_row['DatasetSourceUniqueID'] in original_ids:
    #                         EBARUtils.displayMessage(None, 'Flagging duplicate with InputPointID ' + \
    #                                                     str(unrestricted_row['InputPointID']) + \
    #                                                     ' and DatasetSourceUniqueID ' + \
    #                                                     unrestricted_row['DatasetSourceUniqueID'])
    #                         # store ID for external flagging
    #                         insert_cursor.insertRow([unrestricted_row['InputPointID'],
    #                                                  unrestricted_row['DatasetSourceUniqueID']])
    #                         # # create BadData record, create InputFeedback record, delete Input record using ID
    #                         # param_gdb = arcpy.Parameter()
    #                         # param_gdb.value = param_geodatabase
    #                         # param_input_point_id = arcpy.Parameter()
    #                         # param_input_point_id.value = unrestricted_row['InputPointID']
    #                         # param_input_line_id = arcpy.Parameter()
    #                         # param_input_line_id.value = None
    #                         # param_input_polygon_id = arcpy.Parameter()
    #                         # param_input_polygon_id.value = None
    #                         # param_justification = arcpy.Parameter()
    #                         # param_justification.value = 'Duplicate with iNaturalist.ca (original coordinates for obscured records)'
    #                         # param_undo = arcpy.Parameter()
    #                         # param_undo.value = 'false'
    #                         # parameters = [param_gdb, param_input_point_id, param_input_line_id, 
    #                         #             param_input_polygon_id, param_justification, param_undo]
    #                         # fbdui.runFlagBadDataUsingIDTool(parameters, None, quiet=True)
    #             if unrestricted_row:
    #                 del unrestricted_row
    #             del unrestricted_cursor

    #             # retrieve each DatasetSourceUniqueID for iNat.org
    #             org_row = None
    #             where_clause = 'InputDatasetID IN (SELECT InputDatasetID FROM InputDataset WHERE ' + \
    #                 'DatasetSourceID = 5)' + ' AND SpeciesID = ' + str(row['SpeciesID'])
    #             with arcpy.da.SearchCursor(param_geodatabase + '\InputPoint', ['InputPointID',
    #                                                                             'DatasetSourceUniqueID'],
    #                                         where_clause) as org_cursor:
    #                 for org_row in EBARUtils.searchCursor(org_cursor):
    #                     # check if in original
    #                     if org_row['DatasetSourceUniqueID'] in original_ids:
    #                         EBARUtils.displayMessage(None, 'Flagging duplicate with InputPointID ' + \
    #                                                     str(org_row['InputPointID']) + \
    #                                                     ' and DatasetSourceUniqueID ' + \
    #                                                     org_row['DatasetSourceUniqueID'])
    #                         # store ID for external flagging
    #                         insert_cursor.insertRow([org_row['InputPointID'],
    #                                                  org_row['DatasetSourceUniqueID']])
    #                         # create BadData record, create InputFeedback record, delete Input record using ID
    #                         # param_gdb = arcpy.Parameter()
    #                         # param_gdb.value = param_geodatabase
    #                         # param_input_point_id = arcpy.Parameter()
    #                         # param_input_point_id.value = org_row['InputPointID']
    #                         # param_input_line_id = arcpy.Parameter()
    #                         # param_input_line_id.value = None
    #                         # param_input_polygon_id = arcpy.Parameter()
    #                         # param_input_polygon_id.value = None
    #                         # param_justification = arcpy.Parameter()
    #                         # param_justification.value = 'Duplicate with iNaturalist.ca (original coordinates for obscured records)'
    #                         # param_undo = arcpy.Parameter()
    #                         # param_undo.value = 'false'
    #                         # parameters = [param_gdb, param_input_point_id, param_input_line_id, 
    #                         #             param_input_polygon_id, param_justification, param_undo]
    #                         # fbdui.runFlagBadDataUsingIDTool(parameters, None, quiet=True)
    #             if org_row:
    #                 del org_row
    #             del org_cursor

    #     if row:
    #         del row
    #     del cursor

    # del insert_cursor

    # # 2. iNat.ca unrestricted vs iNat.org
    # EBARUtils.displayMessage(None, 'Checking iNat.ca unrestricted vs iNat.org')
    # # create table to store IDs for external flagging
    # temp_dups = 'TempDups_iNatcaUnres_iNatorg_' + str(start_time.year) + str(start_time.month) + \
    #     str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
    # arcpy.CreateTable_management(param_geodatabase, temp_dups)
    # temp_dups = param_geodatabase + '/' + temp_dups
    # arcpy.AddField_management(temp_dups, 'InputPointID', 'LONG')
    # arcpy.AddField_management(temp_dups, 'DatasetSourceUniqueID', 'TEXT')
    # with arcpy.da.InsertCursor(temp_dups, ['InputPointID', 'DatasetSourceUniqueID']) as insert_cursor:
    #     # loop species
    #     row = None
    #     with arcpy.da.SearchCursor(param_geodatabase + '/Species', ['SpeciesID'],
    #                                 sql_clause=(None, 'ORDER BY SpeciesID')) as cursor:
    #         for row in EBARUtils.searchCursor(cursor):
    #             EBARUtils.displayMessage(None, 'Checking SpeciesID ' + str(row['SpeciesID']))

    #             # retrieve all DatasetSourceUniqueIDs for iNat.ca unrestricted
    #             unrestricted_ids = []
    #             unrestricted_row = None
    #             where_clause = 'InputDatasetID IN (SELECT InputDatasetID FROM InputDataset WHERE ' + \
    #                 'DatasetSourceID = 1010)' + ' AND SpeciesID = ' + str(row['SpeciesID'])
    #             with arcpy.da.SearchCursor(param_geodatabase + '\InputPoint', ['DatasetSourceUniqueID'],
    #                                         where_clause) as unrestricted_cursor:
    #                 for unrestricted_row in EBARUtils.searchCursor(unrestricted_cursor):
    #                     unrestricted_ids.append(unrestricted_row['DatasetSourceUniqueID'])
    #             if unrestricted_row:
    #                 del unrestricted_row
    #             del unrestricted_cursor

    #             # retrieve each DatasetSourceUniqueID for iNat.org
    #             org_row = None
    #             where_clause = 'InputDatasetID IN (SELECT InputDatasetID FROM InputDataset WHERE ' + \
    #                 'DatasetSourceID = 5)' + ' AND SpeciesID = ' + str(row['SpeciesID'])
    #             with arcpy.da.SearchCursor(param_geodatabase + '\InputPoint', ['InputPointID',
    #                                                                            'DatasetSourceUniqueID'],
    #                                         where_clause) as org_cursor:
    #                 for org_row in EBARUtils.searchCursor(org_cursor):
    #                     # check if in unrestricted
    #                     if org_row['DatasetSourceUniqueID'] in unrestricted_ids:
    #                         EBARUtils.displayMessage(None, 'Flagging duplicate with InputPointID ' + \
    #                                                     str(org_row['InputPointID']) + \
    #                                                     ' and DatasetSourceUniqueID ' + \
    #                                                     org_row['DatasetSourceUniqueID'])
    #                         # store ID for external flagging
    #                         insert_cursor.insertRow([org_row['InputPointID'],
    #                                                  org_row['DatasetSourceUniqueID']])
    #                         # create BadData record, create InputFeedback record, delete Input record using ID
    #                         # param_gdb = arcpy.Parameter()
    #                         # param_gdb.value = param_geodatabase
    #                         # param_input_point_id = arcpy.Parameter()
    #                         # param_input_point_id.value = org_row['InputPointID']
    #                         # param_input_line_id = arcpy.Parameter()
    #                         # param_input_line_id.value = None
    #                         # param_input_polygon_id = arcpy.Parameter()
    #                         # param_input_polygon_id.value = None
    #                         # param_justification = arcpy.Parameter()
    #                         # param_justification.value = 'Duplicate with iNaturalist.ca'
    #                         # param_undo = arcpy.Parameter()
    #                         # param_undo.value = 'false'
    #                         # parameters = [param_gdb, param_input_point_id, param_input_line_id, 
    #                         #             param_input_polygon_id, param_justification, param_undo]
    #                         # fbdui.runFlagBadDataUsingIDTool(parameters, None, quiet=True)
    #             if org_row:
    #                 del org_row
    #             del org_cursor

    #     if row:
    #         del row
    #     del cursor

    # del insert_cursor

    # # 3. GBIF vs BISON
    # EBARUtils.displayMessage(None, 'Checking GBIF vs BISON')
    # # create table to store IDs for external flagging
    # temp_dups = 'TempDups_GBIF_BISON_' + str(start_time.year) + str(start_time.month) + \
    #     str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
    # arcpy.CreateTable_management(param_geodatabase, temp_dups)
    # temp_dups = param_geodatabase + '/' + temp_dups
    # arcpy.AddField_management(temp_dups, 'InputPointID', 'LONG')
    # arcpy.AddField_management(temp_dups, 'DatasetSourceUniqueID', 'TEXT')
    # with arcpy.da.InsertCursor(temp_dups, ['InputPointID', 'DatasetSourceUniqueID']) as insert_cursor:
    #     # loop species
    #     row = None
    #     with arcpy.da.SearchCursor(param_geodatabase + '/Species', ['SpeciesID'],
    #                                sql_clause=(None, 'ORDER BY SpeciesID')) as cursor:
    #         for row in EBARUtils.searchCursor(cursor):
    #             EBARUtils.displayMessage(None, 'Checking SpeciesID ' + str(row['SpeciesID']))

    #             # retrieve all DatasetSourceUniqueIDs for GBIF
    #             gbif_ids = []
    #             gbif_row = None
    #             where_clause = 'InputDatasetID IN (SELECT InputDatasetID FROM InputDataset WHERE ' + \
    #                 'DatasetSourceID = 1)' + ' AND SpeciesID = ' + str(row['SpeciesID'])
    #             with arcpy.da.SearchCursor(param_geodatabase + '\InputPoint', ['DatasetSourceUniqueID'],
    #                                         where_clause) as gbif_cursor:
    #                 for gbif_row in EBARUtils.searchCursor(gbif_cursor):
    #                     gbif_ids.append(gbif_row['DatasetSourceUniqueID'])
    #             if gbif_row:
    #                 del gbif_row
    #             del gbif_cursor

    #             # retrieve each DatasetSourceUniqueID for BISON
    #             bison_row = None
    #             where_clause = 'InputDatasetID IN (SELECT InputDatasetID FROM InputDataset WHERE ' + \
    #                 'DatasetSourceID = 6)' + ' AND SpeciesID = ' + str(row['SpeciesID'])
    #             with arcpy.da.SearchCursor(param_geodatabase + '\InputPoint', ['InputPointID',
    #                                                                            'DatasetSourceUniqueID'],
    #                                         where_clause) as bison_cursor:
    #                 for bison_row in EBARUtils.searchCursor(bison_cursor):
    #                     # check if in unrestricted
    #                     if bison_row['DatasetSourceUniqueID'] in gbif_ids:
    #                         EBARUtils.displayMessage(None, 'Flagging duplicate with InputPointID ' + \
    #                                                  str(bison_row['InputPointID']) + \
    #                                                  ' and DatasetSourceUniqueID ' + \
    #                                                  bison_row['DatasetSourceUniqueID'])
    #                         # store ID for external flagging
    #                         insert_cursor.insertRow([bison_row['InputPointID'],
    #                                                  bison_row['DatasetSourceUniqueID']])
    #                         # create BadData record, create InputFeedback record, delete Input record using ID
    #                         # param_gdb = arcpy.Parameter()
    #                         # param_gdb.value = param_geodatabase
    #                         # param_input_point_id = arcpy.Parameter()
    #                         # param_input_point_id.value = bison_row['InputPointID']
    #                         # param_input_line_id = arcpy.Parameter()
    #                         # param_input_line_id.value = None
    #                         # param_input_polygon_id = arcpy.Parameter()
    #                         # param_input_polygon_id.value = None
    #                         # param_justification = arcpy.Parameter()
    #                         # param_justification.value = 'Duplicate with iNaturalist.ca'
    #                         # param_undo = arcpy.Parameter()
    #                         # param_undo.value = 'false'
    #                         # parameters = [param_gdb, param_input_point_id, param_input_line_id, 
    #                         #             param_input_polygon_id, param_justification, param_undo]
    #                         # fbdui.runFlagBadDataUsingIDTool(parameters, None, quiet=True)
    #             if bison_row:
    #                 del bison_row
    #             del bison_cursor

    #     if row:
    #         del row
    #     del cursor

    # del insert_cursor

    # 4. iNat.ca (all subtypes) vs GBIF
    EBARUtils.displayMessage(None, 'Checking iNat (all subtypes) vs GBIF')
    # create table to store IDs for external flagging
    temp_dups = 'TempDups_iNatAll_GBIF_' + str(start_time.year) + str(start_time.month) + \
        str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
    arcpy.CreateTable_management(param_geodatabase, temp_dups)
    temp_dups = param_geodatabase + '/' + temp_dups
    arcpy.AddField_management(temp_dups, 'InputPointID', 'LONG')
    arcpy.AddField_management(temp_dups, 'DatasetSourceUniqueID', 'TEXT')
    with arcpy.da.InsertCursor(temp_dups, ['InputPointID', 'DatasetSourceUniqueID']) as insert_cursor:
        # loop species
        row = None
        with arcpy.da.SearchCursor(param_geodatabase + '/Species', ['SpeciesID'],
                                   sql_clause=(None, 'ORDER BY SpeciesID')) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                EBARUtils.displayMessage(None, 'Checking SpeciesID ' + str(row['SpeciesID']))

                # retrieve all DatasetSourceUniqueIDs for iNat (all subtypes)
                inatall_ids = []
                inatall_row = None
                where_clause = 'InputDatasetID IN (SELECT InputDatasetID FROM InputDataset WHERE ' + \
                    'DatasetSourceID IN (5, 1010, 1110))' + ' AND SpeciesID = ' + str(row['SpeciesID'])
                with arcpy.da.SearchCursor(param_geodatabase + '\InputPoint', ['DatasetSourceUniqueID'],
                                            where_clause) as inatall_cursor:
                    for inatall_row in EBARUtils.searchCursor(inatall_cursor):
                        inatall_ids.append(inatall_row['DatasetSourceUniqueID'])
                if inatall_row:
                    del inatall_row
                del inatall_cursor

                # retrieve each DatasetSourceUniqueID for GBIF
                gbif_row = None
                where_clause = 'InputDatasetID IN (SELECT InputDatasetID FROM InputDataset WHERE ' + \
                    'DatasetSourceID = 1)' + ' AND SpeciesID = ' + str(row['SpeciesID'])
                with arcpy.da.SearchCursor(param_geodatabase + '\InputPoint', ['InputPointID',
                                                                               'DatasetSourceUniqueID',
                                                                               'OriginalInstitutionCode',
                                                                               'URI'],
                                           where_clause) as gbif_cursor:
                    for gbif_row in EBARUtils.searchCursor(gbif_cursor):
                        dssuid = gbif_row['DatasetSourceUniqueID']
                        # ensure OriginalInstitutionCode is 'iNaturalist'
                        if gbif_row['OriginalInstitutionCode'] == 'iNaturalist':
                            # check if URI after the last slash in list of inat.ca dss unique ids
                            pieces = gbif_row['URI'].split('/')
                            if len(pieces) > 0:
                                if pieces[len(pieces) - 1] in inatall_ids:
                                    EBARUtils.displayMessage(None, 'Flagging duplicate with InputPointID ' + \
                                                             str(gbif_row['InputPointID']) + \
                                                             ' and DatasetSourceUniqueID ' + \
                                                             gbif_row['DatasetSourceUniqueID'])
                                    # store ID for external flagging
                                    insert_cursor.insertRow([gbif_row['InputPointID'],
                                                             gbif_row['DatasetSourceUniqueID']])
                                    # create BadData record, create InputFeedback record, delete Input record using ID
                                    # param_gdb = arcpy.Parameter()
                                    # param_gdb.value = param_geodatabase
                                    # param_input_point_id = arcpy.Parameter()
                                    # param_input_point_id.value = gbif_row['InputPointID']
                                    # param_input_line_id = arcpy.Parameter()
                                    # param_input_line_id.value = None
                                    # param_input_polygon_id = arcpy.Parameter()
                                    # param_input_polygon_id.value = None
                                    # param_justification = arcpy.Parameter()
                                    # param_justification.value = 'Duplicate with iNaturalist.ca'
                                    # param_undo = arcpy.Parameter()
                                    # param_undo.value = 'false'
                                    # parameters = [param_gdb, param_input_point_id, param_input_line_id, 
                                    #             param_input_polygon_id, param_justification, param_undo]
                                    # fbdui.runFlagBadDataUsingIDTool(parameters, None, quiet=True)
                if gbif_row:
                    del gbif_row
                del gbif_cursor

        if row:
            del row
        del cursor

    del insert_cursor

    end_time = datetime.datetime.now()
    EBARUtils.displayMessage(None, 'End time: ' + str(datetime.datetime.now()))
    EBARUtils.displayMessage(None, 'Elapsed time: ' + str(end_time - start_time))

finally:
    logfile.close()
    sys.stdout = sys.__stdout__
