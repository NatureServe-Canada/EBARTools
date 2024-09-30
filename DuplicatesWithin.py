import arcpy
import datetime
import EBARUtils
import FlagBadDataUsingIDTool

# parameters
param_geodatabase = 'C:/GIS/EBAR/nsc-gis-ebarkba.sde'
start_time = datetime.datetime.now()
EBARUtils.displayMessage(None, 'Start time: ' + str(start_time))

# get table name prefix (needed for joined tables and feature classes in enterprise geodatabases)
table_name_prefix = EBARUtils.getTableNamePrefix(param_geodatabase)

# get relevant DatasetSourceIDs
dss_ids = {}
# row = None
# with arcpy.da.SearchCursor(param_geodatabase + '/DatasetSource', ['DatasetSourceID', 'DatasetSourceType'],
#                            'CDCJurisdictionID IS NULL') as cursor:
#                            #'DuplicatePriority IS NOT NULL AND CDCJurisdictionID IS NULL') as cursor:
#     for row in EBARUtils.searchCursor(cursor):
#         dss_ids[row['DatasetSourceID']] = row['DatasetSourceType']
#         #dss_ids.append()
# if row:
#     del row
# del cursor
dss_ids[1010] = 'T'

# create instance of Flag tool for doing cleanup
fbdui = FlagBadDataUsingIDTool.FlagBadDataUsingIDTool()

# loop dss_ids
for dss_id in dss_ids.keys():
    EBARUtils.displayMessage(None, 'Checking DatasetSourceID ' + str(dss_id))

    # separate input feature classes for points, lines, polygons
    input_fcname = "InputPoint"
    if dss_ids[dss_id] == 'L':
        input_fcname = 'InputLine'
    elif dss_ids[dss_id] == 'P':
        input_fcname = 'InputPolygon'
    arcpy.MakeFeatureLayer_management(param_geodatabase + '/' + input_fcname, 'input_layer',
                                      'InputDatasetID IN (SELECT InputDatasetID FROM InputDataset WHERE DatasetSourceID = ' +
                                      str(dss_id) + ')' + ' AND MaxDate IS NOT NULL')

    # get list of species for just the current DatasetSource
    # with arcpy.da.SearchCursor('input_layer', ['SpeciesID'], sql_clause=('DISTINCT SpeciesID', 'ORDER BY SpeciesID')) as cursor:
    #     #species_ids = sorted({row[table_name_prefix + 'InputPoint.SpeciesID'] for row in cursor})
    #     for row in EBARUtils.searchCursor(cursor):
    #         species_ids.append(row['SpeciesID'])
    # if row:
    #     del row
    # del cursor
    species_ids = [15968]
        
    # loop species_ids
    for species_id in species_ids:
        EBARUtils.displayMessage(None, 'Checking SpeciesID ' + str(species_id))

        # select one species
        arcpy.SelectLayerByAttribute_management('input_layer', 'NEW_SELECTION', 'SpeciesID = ' + str(species_id))

        # find duplicates
        temp_dups = param_geodatabase + '/TempDups' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.FindIdentical_management('input_layer', temp_dups, ['MaxDate', 'Shape'],
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
                            EBARUtils.displayMessage(None, 'Cleaning up duplicate ' + input_fcname +
                                                     ' with OBJECTID: ' + str(row['IN_FID']))
                            # # create BadData record, create InputFeedback record, delete Input record using ID
                            # input_point_id = None
                            # input_line_id = None
                            # input_polygon_id = None
                            # fid_row = None
                            # with arcpy.da.SearchCursor('input_layer', [input_fcname + 'ID'],
                            #                            'OBJECTID = ' + row['IN_FID']) as fid_cursor:
                            #     for rid_row in EBARUtils.searchCursor(fid_cursor):
                            #         if input_fcname == 'InputPoint':
                            #             input_point_id = fid_row[input_fcname + 'ID']
                            #         if input_fcname == 'InputLine':
                            #             input_line_id = fid_row[input_fcname + 'ID']
                            #         if input_fcname == 'InputPolygon':
                            #             input_polygon_id = fid_row[input_fcname + 'ID']
                            # if fid_row:
                            #     del fid_row
                            # del fid_cursor
                            # parameters = [param_geodatabase, input_point_id, input_line_id, input_polygon_id,
                            #               'Duplicate within DatasetSource', 'false']
                            # fbdui.runFlagBadDataUsingIDTool(parameters, None)
                        else:
                            first_in_seq = True
                    if first_in_seq:
                        # keep first within each seq
                        cur_seq = row['FEAT_SEQ']
                        first_in_seq = False
            if row:
                del row
            del cursor

        # delete temp_dups table
        arcpy.Delete_management(temp_dups)

    arcpy.Delete_management('input_layer')

end_time = datetime.datetime.now()
EBARUtils.displayMessage(None, 'End time: ' + str(datetime.datetime.now()))
EBARUtils.displayMessage(None, 'Elapsed time: ' + str(end_time - start_time))
