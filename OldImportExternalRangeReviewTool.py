# encoding: utf-8
# encoding: utf-8
# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: ImportExternalRangeReviewTool.py
# ArcGIS Python tool for creating review records for an exising range map based on third-party polygons

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
#import sys
#import locale
import EBARUtils
import arcpy
import datetime


class ImportExternalRangeReviewTool:
    """Create review records for an exising range map based on third-party polygons"""
    def __init__(self):
        pass

    def RunImportExternalRangeReviewTool(self, parameters, messages):
        # debugging/testing
        #print(locale.getpreferredencoding())
        #return

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
        param_species = parameters[1].valueAsText.lower()
        param_secondary = parameters[2].valueAsText
        if param_secondary:
            param_secondary = param_secondary.lower()
            param_secondary = param_secondary.replace("'", '')
            param_secondary = param_secondary.split(';')
        param_version = parameters[3].valueAsText
        param_stage = parameters[4].valueAsText
        param_external_range_polygons = parameters[5].valueAsText
        param_presence_field = parameters[6].valueAsText
        if param_presence_field:
            fields = ['EcoshapeID', param_presence_field]
            where_clause = param_presence_field + ' IS NOT NULL'
        else:
            fields = ['EcoshapeID']
            where_clause = '1 = 1'
        param_review_label = parameters[7].valueAsText
        param_jurisdictions_covered = parameters[8].valueAsText
        # convert to Python list
        param_jurisdictions_list = []
        if param_jurisdictions_covered:
            param_jurisdictions_list = param_jurisdictions_covered.replace("'", '')
            param_jurisdictions_list = param_jurisdictions_list.split(';')
        # use passed geodatabase as workspace (still seems to go to default geodatabase)
        arcpy.env.workspace = param_geodatabase

        # get table name prefix (needed for joined tables and feature classes in enterprise geodatabases)
        table_name_prefix = EBARUtils.getTableNamePrefix(param_geodatabase)

        # get feature class name only from external polygons
        desc = arcpy.Describe(param_external_range_polygons)
        external_fc_name = desc.name

        # check for species
        species_id, short_citation = EBARUtils.checkSpecies(param_species, param_geodatabase)
        if not species_id:
            EBARUtils.displayMessage(messages, 'ERROR: Species not found')
            # terminate with error
            return
            #raise arcpy.ExecuteError

        # check for secondary species
        secondary_ids = []
        if param_secondary:
            for secondary in param_secondary:
                secondary_id, short_citation = EBARUtils.checkSpecies(secondary, param_geodatabase)
                if not secondary_id:
                    EBARUtils.displayMessage(messages, 'ERROR: Secondary species not found')
                    # terminate with error
                    return
                    #raise arcpy.ExecuteError
                if secondary_id in secondary_ids:
                    EBARUtils.displayMessage(messages, 'ERROR: Same secondary species specified more than once')
                    # terminate with error
                    return
                    #raise arcpy.ExecuteError
                secondary_ids.append(secondary_id)

        # check for range map record
        EBARUtils.displayMessage(messages, 'Checking for existing range map')
        range_map_id = None
        arcpy.MakeTableView_management(param_geodatabase + '/RangeMap', 'range_map_view',
                                       'SpeciesID = ' + str(species_id) +
                                       " AND RangeVersion = '" + param_version +
                                       "' AND RangeStage = '" + param_stage + "'")
        # start with list of range map candidates due to complexity of checking secondary
        match_candidate = []
        candidate_secondary_count = {}
        candidate_secondary_match_count = {}
        arcpy.AddJoin_management('range_map_view', 'RangeMapID',
                                 param_geodatabase + '/SecondarySpecies', 'RangeMapID', 'KEEP_ALL')
        with arcpy.da.SearchCursor('range_map_view', [table_name_prefix + 'RangeMap.RangeMapID',
                                                      table_name_prefix + 'SecondarySpecies.SpeciesID']) as cursor:
            row = None
            for row in EBARUtils.searchCursor(cursor):
                if row[table_name_prefix + 'RangeMap.RangeMapID'] not in match_candidate:
                    match_candidate.append(row[table_name_prefix + 'RangeMap.RangeMapID'])
                    candidate_secondary_match_count[row[table_name_prefix + 'RangeMap.RangeMapID']] = 0
                    candidate_secondary_count[row[table_name_prefix + 'RangeMap.RangeMapID']] = 0
                if row[table_name_prefix + 'SecondarySpecies.SpeciesID'] in secondary_ids:
                    # secondary matches
                    candidate_secondary_match_count[row[table_name_prefix + 'RangeMap.RangeMapID']] += 1
                if row[table_name_prefix + 'SecondarySpecies.SpeciesID']:
                    # secondary count
                    candidate_secondary_count[row[table_name_prefix + 'RangeMap.RangeMapID']] += 1
            if row:
                del row
        arcpy.RemoveJoin_management('range_map_view', table_name_prefix + 'SecondarySpecies')
        # check candidates for secondary match
        for candidate in match_candidate:
            if (candidate_secondary_match_count[candidate] == len(secondary_ids) and
                candidate_secondary_count[candidate] == len(secondary_ids)):
                range_map_id = candidate
        if not range_map_id:
            EBARUtils.displayMessage(messages, 'ERROR: Range Map not found')
            # terminate with error
            return
            #raise arcpy.ExecuteError

        # build list of jurisdictions
        EBARUtils.displayMessage(messages, 'Building list of jurisdictions')
        jur_name_dict = {}
        with arcpy.da.SearchCursor(param_geodatabase + '/Jurisdiction',
                                   ['JurisdictionID', 'JurisdictionName']) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                jur_name_dict[row['JurisdictionName']] = row['JurisdictionID']
                if not param_jurisdictions_covered:
                    # if not passed in, set to all jurisdictions
                    param_jurisdictions_list.append(row['JurisdictionName'])
            if len(jur_name_dict) > 0:
                del row
        # convert names to comma-separated list of ids
        jur_ids_comma = ''
        for jur_name in param_jurisdictions_list:
            if len(jur_ids_comma) > 0:
                jur_ids_comma += ','
            jur_ids_comma += str(jur_name_dict[jur_name])

        # subset external polygons (by species name if given)
        EBARUtils.displayMessage(messages, 'Selecting external polygons for species')
        arcpy.MakeFeatureLayer_management(param_external_range_polygons, 'external_polygons_layer')

        # subset RangeMapEcoshapes (by range map)
        EBARUtils.displayMessage(messages, 'Selecting RangeMapEcoshapes')
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/Ecoshape', 'ecoshapes_layer')
        arcpy.AddJoin_management('ecoshapes_layer', 'EcoshapeID', param_geodatabase + '/RangeMapEcoshape',
                                 'EcoshapeID', 'KEEP_COMMON')
        arcpy.SelectLayerByAttribute_management('ecoshapes_layer', 'NEW_SELECTION',
                                                table_name_prefix + 'RangeMapEcoshape.RangeMapID = ' + \
                                                    str(range_map_id) + ' AND ' + table_name_prefix + \
                                                    'Ecoshape.JurisdictionID IN ( ' + jur_ids_comma + ')')

        # create Review record
        # how to dynamically get username (only applicable when connected to enterprise gdb/service???)
        EBARUtils.displayMessage(messages, 'Creating Review record')
        with arcpy.da.InsertCursor(param_geodatabase + '/Review',
                                   ['RangeMapID', 'Username', 'DateCompleted', 'ReviewNotes']) as cursor:
            object_id = cursor.insertRow([range_map_id, 'rgreenens', datetime.datetime.now(),
                                          param_review_label + ' auto-applied'])
        # ReviewID auto-generated by PostgreSQL on EBAR server, so only set on local gdb
        if param_geodatabase[-4:].lower() == '.gdb':
            review_id = EBARUtils.setNewID(param_geodatabase + '/Review', 'ReviewID', 'OBJECTID = ' + str(object_id))
        else:
            with arcpy.da.SearchCursor(param_geodatabase + '/Review', ['ReviewID'],
                                       'OBJECTID = ' + str(object_id)) as search_cursor:
                row = None
                for row in EBARUtils.searchCursor(search_cursor):
                    review_id = row['ReviewID']
                if row:
                    del row

        # check each RangeMapEcoshape and create EcoshapeReview Remove record for any in covered jurisdictions but not
        # in external polygons
        EBARUtils.displayMessage(messages, 'Creating EcoshapeReview remove records')
        remove_count = 0
        # read external ids
        external_ecoshape_ids = []
        with arcpy.da.SearchCursor('external_polygons_layer', ['EcoshapeID'], where_clause) as search_cursor:
            for row in EBARUtils.searchCursor(search_cursor):
                external_ecoshape_ids.append(row['EcoshapeID'])
            if len(external_ecoshape_ids) > 0:
                del row
        # check against EBAR ecoshapes
        with arcpy.da.SearchCursor('ecoshapes_layer',
                                    [table_name_prefix + 'RangeMapEcoshape.RangeMapID',
                                     table_name_prefix + 'Ecoshape.EcoshapeID']) as search_cursor:
            row = None
            for row in EBARUtils.searchCursor(search_cursor):
                if (row[table_name_prefix + 'RangeMapEcoshape.RangeMapID'] == range_map_id and
                    row[table_name_prefix + 'Ecoshape.EcoshapeID'] not in external_ecoshape_ids):
                    with arcpy.da.InsertCursor(param_geodatabase + '/EcoshapeReview',
                                               ['EcoshapeID', 'ReviewID', 'RemovalReason', 'EcoshapeReviewNotes',
                                                'UseForMapGen', 'Markup', 'Username']) as cursor:
                        object_id = cursor.insertRow([row[table_name_prefix + 'Ecoshape.EcoshapeID'], review_id,
                                                      'O', 'Not in ' + param_review_label, 1, 'R', 'rgreenens'])
                    # EcoshapeReviewID auto-generated by PostgreSQL on EBAR server, so only set on local gdb
                    if param_geodatabase[-4:].lower() == '.gdb':
                        EBARUtils.setNewID(param_geodatabase + '/EcoshapeReview', 'EcoshapeReviewID',
                                            'OBJECTID = ' + str(object_id))
                    remove_count += 1
            if row:
                del row

        # check each external polygon and create EcoshapeReview Add record for any in covered jurisdictions but not
        # in RangeMapEcoshape
        EBARUtils.displayMessage(messages, 'Creating EcoshapeReview add records')
        add_count = 0
        # read ecoshapes in current range
        range_ecoshape_ids = {}
        with arcpy.da.SearchCursor('ecoshapes_layer', [table_name_prefix + 'Ecoshape.EcoshapeID',
                                                       table_name_prefix + 'RangeMapEcoshape.Presence',
                                                       table_name_prefix + 'RangeMapEcoshape.RangeMapID']
                                   ) as search_cursor:
            for row in EBARUtils.searchCursor(search_cursor):
                range_ecoshape_ids[row[table_name_prefix + 'Ecoshape.EcoshapeID']] = \
                    row[table_name_prefix + 'RangeMapEcoshape.Presence']
            if len(range_ecoshape_ids) > 0:
                del row
        # check against external ecoshapes
        with arcpy.da.SearchCursor('external_polygons_layer', fields, where_clause) as search_cursor:
            row = None
            for row in EBARUtils.searchCursor(search_cursor):
                presence = None
                if row['EcoshapeID'] not in range_ecoshape_ids:
                    if param_presence_field:
                        if row[param_presence_field]:
                            if row[param_presence_field].lower() in ('p', 'present', 'presence'):
                                presence = 'P'
                            if row[param_presence_field].lower() in ('x', 'presence expected'):
                                presence = 'X'
                            if row[param_presence_field].lower() in ('h', 'historical'):
                                presence = 'H'
                    else:
                        presence = 'P'
                if presence:
                    with arcpy.da.InsertCursor(param_geodatabase + '/EcoshapeReview',
                                                ['EcoshapeID', 'ReviewID', 'RemovalReason', 'EcoshapeReviewNotes',
                                                'UseForMapGen', 'Markup', 'Username']) as cursor:
                        object_id = cursor.insertRow([row['EcoshapeID'], review_id, None, 'In ' + param_review_label,
                                                      1, presence, 'rgreenens'])
                    # EcoshapeReviewID auto-generated by PostgreSQL on EBAR server, so only set on local gdb
                    if param_geodatabase[-4:].lower() == '.gdb':
                        EBARUtils.setNewID(param_geodatabase + '/EcoshapeReview', 'EcoshapeReviewID',
                                            'OBJECTID = ' + str(object_id))
                    add_count += 1
            if row:
                del row

        # check if any records in both external and RangeMapEcoshape need to be upgraded
        EBARUtils.displayMessage(messages, 'Creating EcoshapeReview change records')
        change_count = 0
        # loop external ecoshapes
        with arcpy.da.SearchCursor('external_polygons_layer', fields, where_clause) as search_cursor:
            row = None
            for row in EBARUtils.searchCursor(search_cursor):
                if row['EcoshapeID'] in external_ecoshape_ids:
                    # get external presence (default to Present)
                    presence = 'P'
                    if param_presence_field:
                        if row[param_presence_field]:
                            if row[param_presence_field].lower() in ('p', 'present', 'presence'):
                                presence = 'P'
                            if row[param_presence_field].lower() in ('x', 'presence expected'):
                                presence = 'X'
                            if row[param_presence_field].lower() in ('h', 'historical'):
                                presence = 'H'
                    # compare to range ecoshape presence
                    if row['EcoshapeID'] in range_ecoshape_ids:
                        if presence != range_ecoshape_ids[row['EcoshapeID']]:
                            with arcpy.da.InsertCursor(param_geodatabase + '/EcoshapeReview',
                                                        ['EcoshapeID', 'ReviewID', 'RemovalReason', 'EcoshapeReviewNotes',
                                                         'UseForMapGen', 'Markup', 'Username']) as cursor:
                                object_id = cursor.insertRow([row['EcoshapeID'], review_id, None,
                                                              'In ' + param_review_label, 1, presence, 'rgreenens'])
                            # EcoshapeReviewID auto-generated by PostgreSQL on EBAR server, so only set on local gdb
                            if param_geodatabase[-4:].lower() == '.gdb':
                                EBARUtils.setNewID(param_geodatabase + '/EcoshapeReview', 'EcoshapeReviewID',
                                                    'OBJECTID = ' + str(object_id))
                            change_count += 1
            if row:
                del row

        # summary and end time
        EBARUtils.displayMessage(messages, str(remove_count) + ' EcoshapeReview records created for removing')
        EBARUtils.displayMessage(messages, str(add_count) + ' EcoshapeReview records created for adding')
        EBARUtils.displayMessage(messages, str(change_count) + ' EcoshapeReview records created for changing')
        end_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'End time: ' + str(end_time))
        elapsed_time = end_time - start_time
        EBARUtils.displayMessage(messages, 'Elapsed time: ' + str(elapsed_time))
        return
            

# controlling process
if __name__ == '__main__':
    ierr = ImportExternalRangeReviewTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:/GIS/EBAR/EBAR-KBA-Dev.gdb'
    param_species = arcpy.Parameter()
    param_species.value = 'Bombus suckleyi'
    param_secondary = arcpy.Parameter()
    param_secondary.value = None
    #param_secondary.value = "'Dodia verticalis'"
    #param_secondary.value = "'Dodia tarandus';'Dodia verticalis'"
    param_version = arcpy.Parameter()
    param_version.value = '0.99'
    param_stage = arcpy.Parameter()
    param_stage.value = 'Auto-generated'
    param_external_range_polygons = arcpy.Parameter()
    param_external_range_polygons.value = 'C:/GIS/EBAR/EBARServer.gdb/EcoshapeSuckleuSpatialJoin'
    param_presence_field = arcpy.Parameter()
    param_presence_field.value = 'Occurence'
    param_review_label = arcpy.Parameter()
    param_review_label.value = 'BC expert review'
    param_jurisdictions_covered = arcpy.Parameter()
    param_jurisdictions_covered.value = None
    parameters = [param_geodatabase, param_species, param_secondary, param_version, param_stage,
                  param_external_range_polygons, param_presence_field, param_review_label, param_jurisdictions_covered]
    ierr.RunImportExternalRangeReviewTool(parameters, None)
