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

    def runImportExternalRangeReviewTool(self, parameters, messages):
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
        param_external_range_table = parameters[5].valueAsText
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
        EBARUtils.displayMessage(messages, 'Checking for existing Range Map')
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

        # check for existing imported review
        # username is currently hard-coded to rgreenens, but plan is to make this a parameter
        EBARUtils.displayMessage(messages, 'Checking for existing Review')
        review_id = None
        with arcpy.da.SearchCursor(param_geodatabase + '\Review', ['ReviewID'],
                                   "Username = 'rgreenens' AND RangeMapID = " + str(range_map_id)) as cursor:
            row = None
            for row in EBARUtils.searchCursor(cursor):
                review_id = row['ReviewID']
            if row:
                del row
        if review_id:
            EBARUtils.displayMessage(messages, 'ERROR: Review already exists for this Username')
            # terminate with error
            return
            #raise arcpy.ExecuteError

        # build list of jurisdictions
        EBARUtils.displayMessage(messages, 'Building list of Jurisdictions')
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
        jur_ids_comma = '('
        for jur_name in param_jurisdictions_list:
            if len(jur_ids_comma) > 1:
                jur_ids_comma += ','
            jur_ids_comma += str(jur_name_dict[jur_name])
        jur_ids_comma += ')'

        # build dict of RangeMapEcoshape Presence for jurisdiction(s)
        EBARUtils.displayMessage(messages, 'Building dictionary of RangeMapEcoshape Presence for Jurisdiction(s)')
        arcpy.MakeTableView_management(param_geodatabase + '/RangeMapEcoshape', 'range_layer',
                                       'RangeMapID = ' + str(range_map_id))
        arcpy.AddJoin_management('range_layer', 'EcoshapeID', param_geodatabase + '/Ecoshape',
                                 'EcoshapeID', 'KEEP_COMMON')
        range_ecoshape_dict = {}
        with arcpy.da.SearchCursor('range_layer', [table_name_prefix + 'Ecoshape.EcoshapeID',
                                                   table_name_prefix + 'RangeMapEcoshape.Presence'],
                                   table_name_prefix + 'Ecoshape.JurisdictionID IN ' + jur_ids_comma) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                range_ecoshape_dict[row[table_name_prefix + 'Ecoshape.EcoshapeID']] = \
                    row[table_name_prefix + 'RangeMapEcoshape.Presence']
            if len(range_ecoshape_dict) > 0:
                del row

        # build dict of External Ecoshape Presence
        EBARUtils.displayMessage(messages, 'Building dictionary of External Ecoshape Presence')
        external_ecoshape_dict = {}
        fields = ['EcoshapeID']
        if param_presence_field:
            fields = ['EcoshapeID', param_presence_field]
        with arcpy.da.SearchCursor(param_external_range_table, fields) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                presence = None
                if param_presence_field:
                    if row[param_presence_field]:
                        if row[param_presence_field].lower() in ('p', 'present', 'presence',
                                                                 'x', 'presence expected',
                                                                 'h', 'historical'):
                            presence = 'P'
                            if row[param_presence_field].lower() in ('x', 'presence expected'):
                                presence = 'X'
                            if row[param_presence_field].lower() in ('h', 'historical'):
                                presence = 'H'
                else:
                    presence = 'P'
                if presence:
                    external_ecoshape_dict[row['EcoshapeID']] = presence
            if len(external_ecoshape_dict) > 0:
                del row

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

        # init counts
        change_count = 0
        add_count = 0
        remove_count = 0

        # loop all external
        EBARUtils.displayMessage(messages, 'Processing External Ecoshapes')
        for external_ecoshape_id in external_ecoshape_dict:
            if external_ecoshape_id in range_ecoshape_dict:
                # check for different presence values
                if external_ecoshape_dict[external_ecoshape_id] != range_ecoshape_dict[external_ecoshape_id]:
                    # create review change record
                    with arcpy.da.InsertCursor(param_geodatabase + '/EcoshapeReview',
                                               ['EcoshapeID', 'ReviewID', 'RemovalReason', 'EcoshapeReviewNotes',
                                                'UseForMapGen', 'Markup', 'Username']) as cursor:
                        object_id = cursor.insertRow([external_ecoshape_id, review_id, None,
                                                      'In ' + param_review_label, 1,
                                                      external_ecoshape_dict[external_ecoshape_id], 'rgreenens'])
                    # EcoshapeReviewID auto-generated by PostgreSQL on EBAR server, so only set on local gdb
                    if param_geodatabase[-4:].lower() == '.gdb':
                        EBARUtils.setNewID(param_geodatabase + '/EcoshapeReview', 'EcoshapeReviewID',
                                            'OBJECTID = ' + str(object_id))
                    change_count += 1
            else:
                # create review add record
                with arcpy.da.InsertCursor(param_geodatabase + '/EcoshapeReview',
                                           ['EcoshapeID', 'ReviewID', 'RemovalReason', 'EcoshapeReviewNotes',
                                            'UseForMapGen', 'Markup', 'Username']) as cursor:
                    object_id = cursor.insertRow([external_ecoshape_id, review_id, None, 'In ' + param_review_label,
                                                  1, external_ecoshape_dict[external_ecoshape_id], 'rgreenens'])
                # EcoshapeReviewID auto-generated by PostgreSQL on EBAR server, so only set on local gdb
                if param_geodatabase[-4:].lower() == '.gdb':
                    EBARUtils.setNewID(param_geodatabase + '/EcoshapeReview', 'EcoshapeReviewID',
                                        'OBJECTID = ' + str(object_id))
                add_count += 1

        # loop all external
        EBARUtils.displayMessage(messages, 'Processing existing Range Ecoshapes')
        for range_ecoshape_id in range_ecoshape_dict:
            if range_ecoshape_id not in external_ecoshape_dict:
                # create review remove record
                with arcpy.da.InsertCursor(param_geodatabase + '/EcoshapeReview',
                                           ['EcoshapeID', 'ReviewID', 'RemovalReason', 'EcoshapeReviewNotes',
                                            'UseForMapGen', 'Markup', 'Username']) as cursor:
                    object_id = cursor.insertRow([range_ecoshape_id, review_id, 'O', 'Not in ' + param_review_label,
                                                  1, 'R', 'rgreenens'])
                # EcoshapeReviewID auto-generated by PostgreSQL on EBAR server, so only set on local gdb
                if param_geodatabase[-4:].lower() == '.gdb':
                    EBARUtils.setNewID(param_geodatabase + '/EcoshapeReview', 'EcoshapeReviewID',
                                        'OBJECTID = ' + str(object_id))
                remove_count+= 1

        # summary and end time
        EBARUtils.displayMessage(messages, str(change_count) + ' EcoshapeReview records created for changing')
        EBARUtils.displayMessage(messages, str(add_count) + ' EcoshapeReview records created for adding')
        EBARUtils.displayMessage(messages, str(remove_count) + ' EcoshapeReview records created for removing')
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
    param_external_range_table = arcpy.Parameter()
    param_external_range_table.value = 'C:/GIS/EBAR/EBARServer.gdb/EcoshapeSuckleuSpatialJoin'
    param_presence_field = arcpy.Parameter()
    param_presence_field.value = 'Occurence'
    #param_presence_field.value = None
    param_review_label = arcpy.Parameter()
    param_review_label.value = 'BC expert review'
    param_jurisdictions_covered = arcpy.Parameter()
    param_jurisdictions_covered.value = None
    parameters = [param_geodatabase, param_species, param_secondary, param_version, param_stage,
                  param_external_range_table, param_presence_field, param_review_label, param_jurisdictions_covered]
    ierr.runImportExternalRangeReviewTool(parameters, None)
