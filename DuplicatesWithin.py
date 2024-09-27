import arcpy
import datetime
import EBARUtils

# parameters
param_geodatabase = 'C:/GIS/EBAR/nsc-gis-ebarkba.sde'
#species_id = 925
start_time = datetime.datetime.now()

# get table name prefix (needed for joined tables and feature classes in enterprise geodatabases)
table_name_prefix = EBARUtils.getTableNamePrefix(param_geodatabase)
# arcpy.MakeFeatureLayer_management(param_geodatabase + '/InputPoint', 'input_point_layer')
# arcpy.AddJoin_management('input_point_layer', 'InputDatasetID', param_geodatabase + '/InputDataset', 'InputDatasetID',
#                          'KEEP_COMMON')
#arcpy.AddJoin_management('input_point_layer', 'DatasetSourceID', 'DatasetSource', 'DatasetSourceID', 'KEEP_COMMON')
#arcpy.AddJoin_management('input_point_layer', 'SpeciesID', 'Species', 'SpeciesID', 'KEEP_COMMON')

# get relevant DatasetSourceIDs
# dss_ids = []
# row = None
# with arcpy.da.SearchCursor(param_geodatabase + '/DatasetSource', ['DatasetSourceID'],
#                            'DuplicatePriority IS NOT NULL AND CDCJurisdictionID IS NULL') as cursor:
#     for row in EBARUtils.searchCursor(cursor):
#         dss_ids.append(row['DatasetSourceID'])
# if row:
#     del row
# del cursor
dss_ids = [1010]

# loop dss_ids
for dss_id in dss_ids:
    EBARUtils.displayMessage(None, 'Checking DatasetSourceID ' + str(dss_id))

    # get distinct SpeciesIDs within DatasetSource
    species_ids = []
    row = None
    # with arcpy.da.SearchCursor('input_point_layer', [table_name_prefix + 'InputPoint.SpeciesID'],
    #                            'DatasetSourceID = ' + str(dss_id)) as cursor:
    #                            #sql_clause=('DISTINCT SpeciesID', None)) as cursor:
    arcpy.MakeFeatureLayer_management(param_geodatabase + '/InputPoint', 'input_point_layer',
                                      'InputDatasetID IN (SELECT InputDatasetID FROM InputDataset WHERE DatasetSourceID = ' + str(dss_id) + ')')
    with arcpy.da.SearchCursor('input_point_layer', ['SpeciesID'], sql_clause=('DISTINCT SpeciesID', None)) as cursor:
        #species_ids = sorted({row[table_name_prefix + 'InputPoint.SpeciesID'] for row in cursor})
        for row in EBARUtils.searchCursor(cursor):
            species_ids.append(row['SpeciesID'])
    if row:
        del row
    del cursor    
        
    # loop species_ids
    for species_id in species_ids:
        EBARUtils.displayMessage(None, 'Checking SpeciesID ' + str(species_id))

        # select one species
        arcpy.SelectLayerByAttribute_management('input_point_layer', 'NEW_SELECTION', 'SpeciesID = ' + str(species_id))

        # find duplicates
        temp_dups = param_geodatabase + '/TempDups' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.FindIdentical_management('input_point_layer', temp_dups, ['MaxDate', 'Shape'],
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
                            EBARUtils.displayMessage(None, 'Duplicate InputPoint OBJECTID: ' + str(row['IN_FID']))
                            # create BadData records
                            # create InputFeedback records
                            # delete InputPoint records
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

    arcpy.Delete_management('input_point_layer')

        # row = None
        # with arcpy.da.SearchCursor('input_point_layer', [table_name_prefix + 'InputPoint.InputPointID',
        #                                                 table_name_prefix + 'InputDataset.DatasetSourceID',
        #                                                 table_name_prefix + 'InputPoint.SpeciesID',
        #                                                 table_name_prefix + 'InputPoint.MaxDate',
        #                                                 'SHAPE@X', 'SHAPE@Y'],
        #                         'DatasetSourceID = ' + str(dss_id) + ' AND SpeciesID = ' + str(species_id),
        #                         sql_clause=(None,'ORDER BY SpeciesID ASC, MaxDate ASC, InputPointID DESC')) as cursor:
        #     first = True
        #     for row in EBARUtils.searchCursor(cursor):
        #         EBARUtils.displayMessage(None, 'Processing: ' + str(row[table_name_prefix + 'InputPoint.InputPointID']))
        #         cur_x = row['SHAPE@X']
        #         cur_y = row['SHAPE@Y']
        #         EBARUtils.displayMessage(None, 'SpeciesID: ' + str(row[table_name_prefix + 'InputPoint.SpeciesID']))
        #         EBARUtils.displayMessage(None, 'MaxDate: ' + str(row[table_name_prefix + 'InputPoint.MaxDate']))
        #         EBARUtils.displayMessage(None, 'X: ' + str(cur_x))
        #         EBARUtils.displayMessage(None, 'Y: ' + str(cur_y))
        #         EBARUtils.displayMessage(None, 'MaxDate: ' + str(row[table_name_prefix + 'InputPoint.MaxDate']))
        #         if not first:
        #             if (row[table_name_prefix + 'InputDataset.DatasetSourceID'] == prev_id and
        #                 row[table_name_prefix + 'InputPoint.SpeciesID'] == prev_species and
        #                 row[table_name_prefix + 'InputPoint.MaxDate'] == prev_date and
        #                 cur_x == prev_x and cur_y == prev_y):
        #                 EBARUtils.displayMessage(None,
        #                                         'Duplicate: ' + str(row[table_name_prefix + 'InputPoint.InputPointID']))
        #                 # create BadData records
        #                 # create InputFeedback records
        #                 # delete InputPoint records
        #                 pass
        #             else:
        #                 first = True
        #         if first:
        #             prev_id = row[table_name_prefix + 'InputDataset.DatasetSourceID']
        #             prev_species = row[table_name_prefix + 'InputPoint.SpeciesID']
        #             prev_date = row[table_name_prefix + 'InputPoint.MaxDate']
        #             prev_x = row['SHAPE@X']
        #             prev_y = row['SHAPE@Y']
        #             first = False
        # if row:
        #     del row
        # del cursor
