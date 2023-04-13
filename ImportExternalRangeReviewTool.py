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
        param_usagetype_field = parameters[7].valueAsText
        param_review_label = parameters[8].valueAsText
        param_overall_review_notes = parameters[9].valueAsText
        param_jurisdictions_covered = parameters[10].valueAsText
        # convert to Python list
        param_jurisdictions_list = []
        if param_jurisdictions_covered:
            param_jurisdictions_list = param_jurisdictions_covered.replace("'", '')
            param_jurisdictions_list = param_jurisdictions_list.split(';')
        param_username = parameters[11].valueAsText
        param_additions_only = parameters[12].valueAsText
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

        # check for username
        EBARUtils.displayMessage(messages, 'Checking for Username')
        with arcpy.da.SearchCursor(param_geodatabase + '\Expert', ['Username'],
                                   "Username = '" + param_username + "'") as cursor:
            row = None
            for row in EBARUtils.searchCursor(cursor):
                pass
            if not row:
                EBARUtils.displayMessage(messages, 'ERROR: Username must exist in Expert table')
                # terminate with error
                return
                #raise arcpy.ExecuteError
            else:
                del row

        # check for existing review
        EBARUtils.displayMessage(messages, 'Checking for existing Review')
        review_id = None
        with arcpy.da.SearchCursor(param_geodatabase + '\Review', ['ReviewID'],
                                   "Username = '" + param_username + "' AND RangeMapID = " + \
                                       str(range_map_id)) as cursor:
            row = None
            for row in EBARUtils.searchCursor(cursor):
                review_id = row['ReviewID']
            if row:
                del row
        if review_id:
            EBARUtils.displayMessage(messages, 'ERROR: Review already exists for this Username and RangeMap')
            # terminate with error
            return
            #raise arcpy.ExecuteError

        # build list of jurisdiction ids
        EBARUtils.displayMessage(messages, 'Building list of Jurisdictions')
        jur_ids_comma = EBARUtils.buildJurisdictionList(param_geodatabase, param_jurisdictions_list)

        # build dicst of RangeMapEcoshape Presence and UsageType for jurisdiction(s)
        EBARUtils.displayMessage(messages, 'Building dictionary of RangeMapEcoshape Presence for Jurisdiction(s)')
        arcpy.MakeTableView_management(param_geodatabase + '/RangeMapEcoshape', 'range_layer',
                                       'RangeMapID = ' + str(range_map_id))
        arcpy.AddJoin_management('range_layer', 'EcoshapeID', param_geodatabase + '/Ecoshape',
                                 'EcoshapeID', 'KEEP_COMMON')
        range_presence_dict = {}
        range_usagetype_dict = {}
        with arcpy.da.SearchCursor('range_layer', [table_name_prefix + 'Ecoshape.EcoshapeID',
                                                   table_name_prefix + 'RangeMapEcoshape.Presence',
                                                   table_name_prefix + 'RangeMapEcoshape.UsageType'],
                                   table_name_prefix + 'Ecoshape.JurisdictionID IN ' + jur_ids_comma) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                range_presence_dict[row[table_name_prefix + 'Ecoshape.EcoshapeID']] = \
                    row[table_name_prefix + 'RangeMapEcoshape.Presence']
                range_usagetype_dict[row[table_name_prefix + 'Ecoshape.EcoshapeID']] = \
                    row[table_name_prefix + 'RangeMapEcoshape.UsageType']
            if len(range_presence_dict) > 0:
                del row

        # build dicts of external ecoshape Presence and UsageType
        EBARUtils.displayMessage(messages, 'Building dictionaries of External Ecoshape Presence and UsageType')
        fields = ['EcoshapeID']
        if param_presence_field:
            fields.append(param_presence_field)
        if param_usagetype_field:
            fields.append(param_usagetype_field)
        external_presence_dict = {}
        external_usagetype_dict = {}
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
                #if presence:
                external_presence_dict[row['EcoshapeID']] = presence
                usagetype = None
                if param_usagetype_field:
                    if row[param_usagetype_field]:
                        if row[param_usagetype_field].lower() in ('b', 'breeding',
                                                                  'p', 'possible breeding',
                                                                  'n', 'non-breeding', 'nonbreeding'):
                            usagetype = 'B'
                            if row[param_usagetype_field].lower() in ('p', 'possible breeding'):
                                usagetype = 'P'
                            # if row[param_usagetype_field].lower() in ('m', 'migration'):
                            #     usagetype = 'M'
                            if row[param_usagetype_field].lower() in ('n', 'non-breeding', 'nonbreeding'):
                                usagetype = 'N' 
                #if usagetype:
                external_usagetype_dict[row['EcoshapeID']] = usagetype

            if len(external_presence_dict) > 0:
                del row

        # create Review record
        EBARUtils.displayMessage(messages, 'Creating Review record')
        with arcpy.da.InsertCursor(param_geodatabase + '/Review',
                                   ['RangeMapID', 'Username', 'DateCompleted', 'ReviewNotes',
                                    'UseForMapGen']) as cursor:
            review_notes = param_review_label + ' imported'
            if param_overall_review_notes:
                review_notes += ': ' + param_overall_review_notes
            object_id = cursor.insertRow([range_map_id, param_username, datetime.datetime.now(),
                                          review_notes, 1])
        review_id = EBARUtils.getUniqueID(param_geodatabase + '/Review', 'ReviewID', object_id)

        # init counts
        change_count = 0
        add_count = 0
        remove_count = 0

        # loop all external
        EBARUtils.displayMessage(messages, 'Processing External Ecoshapes')
        for external_ecoshape_id in external_presence_dict:
            change = False
            new_presence = None
            new_usagetype = None
            if external_ecoshape_id in range_presence_dict:
                # check for different presence values
                if external_presence_dict[external_ecoshape_id] != range_presence_dict[external_ecoshape_id]:
                    # additions also include the case of "upgrading" ecoshape to Present
                    if param_additions_only == 'false' or external_presence_dict[external_ecoshape_id] == 'P':
                        change = True
                        new_presence = external_presence_dict[external_ecoshape_id]
            if external_ecoshape_id in range_usagetype_dict:
                # check for different usagetype values
                if external_usagetype_dict[external_ecoshape_id] != range_usagetype_dict[external_ecoshape_id]:
                    change = True
                    new_usagetype = external_usagetype_dict[external_ecoshape_id]
            if change:
                # create review change record
                with arcpy.da.InsertCursor(param_geodatabase + '/EcoshapeReview',
                                            ['EcoshapeID', 'ReviewID', 'RemovalReason', 'EcoshapeReviewNotes',
                                             'UseForMapGen', 'Markup', 'UsageTypeMarkup', 'Username']) as cursor:
                    object_id = cursor.insertRow([external_ecoshape_id, review_id, None,
                                                  'In ' + param_review_label, 1, new_presence, new_usagetype,
                                                  param_username])
                change_count += 1
            else:
                check_row = None
                if external_ecoshape_id:
                    # check for matching ecoshape ID
                    with arcpy.da.SearchCursor(param_geodatabase + '/Ecoshape', ['EcoshapeID'],
                                               'EcoshapeID = ' + str(external_ecoshape_id)) as check_cursor:
                        for check_row in check_cursor:
                            pass
                    del check_cursor
                if check_row:
                    # create review add record
                    with arcpy.da.InsertCursor(param_geodatabase + '/EcoshapeReview',
                                            ['EcoshapeID', 'ReviewID', 'RemovalReason', 'EcoshapeReviewNotes',
                                                'UseForMapGen', 'Markup', 'UsageTypeMarkup', 'Username']) as cursor:
                        object_id = cursor.insertRow([external_ecoshape_id, review_id, None, 'In ' + param_review_label,
                                                    1, external_presence_dict[external_ecoshape_id],
                                                    external_usagetype_dict[external_ecoshape_id], param_username])
                    add_count += 1
                    del check_row
                else:
                    EBARUtils.displayMessage(messages, 'WARNING - invalid external EcoshapeID ' + str(external_ecoshape_id))
        # handle case of ecoshape with usagetype markup but no presence markup
        for external_ecoshape_id in external_usagetype_dict:
            if external_ecoshape_id not in external_presence_dict:
                change = False
                new_presence = None
                new_usagetype = None
                if external_ecoshape_id in range_usagetype_dict:
                    # check for different usagetype values
                    if external_usagetype_dict[external_ecoshape_id] != range_usagetype_dict[external_ecoshape_id]:
                        change = True
                        new_usagetype = external_usagetype_dict[external_ecoshape_id]
                if change:
                    # create review change record
                    with arcpy.da.InsertCursor(param_geodatabase + '/EcoshapeReview',
                                                ['EcoshapeID', 'ReviewID', 'RemovalReason', 'EcoshapeReviewNotes',
                                                'UseForMapGen', 'Markup', 'UsageTypeMarkup', 'Username']) as cursor:
                        object_id = cursor.insertRow([external_ecoshape_id, review_id, None,
                                                    'In ' + param_review_label, 1, new_presence, new_usagetype,
                                                    param_username])
                    change_count += 1
                else:
                    # create review add record
                    with arcpy.da.InsertCursor(param_geodatabase + '/EcoshapeReview',
                                            ['EcoshapeID', 'ReviewID', 'RemovalReason', 'EcoshapeReviewNotes',
                                                'UseForMapGen', 'Markup', 'UsageTypeMarkup', 'Username']) as cursor:
                        object_id = cursor.insertRow([external_ecoshape_id, review_id, None, 'In ' + param_review_label,
                                                    1, external_presence_dict[external_ecoshape_id],
                                                    external_usagetype_dict[external_ecoshape_id], param_username])
                    add_count += 1

        # loop all existing
        if param_additions_only == 'false':
            EBARUtils.displayMessage(messages, 'Processing existing Range Ecoshapes')
            for range_ecoshape_id in range_presence_dict:
                if (range_ecoshape_id not in external_presence_dict and
                    range_ecoshape_id not in external_usagetype_dict):
                    # create review remove record
                    with arcpy.da.InsertCursor(param_geodatabase + '/EcoshapeReview',
                                            ['EcoshapeID', 'ReviewID', 'RemovalReason', 'EcoshapeReviewNotes',
                                             'UseForMapGen', 'Markup', 'Username']) as cursor:
                        object_id = cursor.insertRow([range_ecoshape_id, review_id, 'O',
                                                      'Not in ' + param_review_label, 1, 'R', param_username])
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
    param_species.value = 'Aechmophorus occidentalis'
    param_secondary = arcpy.Parameter()
    param_secondary.value = None
    #param_secondary.value = "'Dodia verticalis'"
    #param_secondary.value = "'Dodia tarandus';'Dodia verticalis'"
    param_version = arcpy.Parameter()
    param_version.value = '1.0'
    param_stage = arcpy.Parameter()
    param_stage.value = 'Expert reviewed test00'
    param_external_range_table = arcpy.Parameter()
    param_external_range_table.value = 'C:/GIS/EBAR/EBARServer.gdb/TestImport'
    param_presence_field = arcpy.Parameter()
    param_presence_field.value = 'PresenceMarkup'
    #param_presence_field.value = None
    param_usagetype_field = arcpy.Parameter()
    param_usagetype_field.value = 'UsageTypeMarkup'
    #param_usagetype_field.value = None
    param_review_label = arcpy.Parameter()
    param_review_label.value = 'Test expert review'
    param_overall_review_notes = arcpy.Parameter()
    param_overall_review_notes.value = 'Additional notes, such as definitions and exceptions!'
    param_jurisdictions_covered = arcpy.Parameter()
    #param_jurisdictions_covered.value = None
    param_jurisdictions_covered.value = "'Yukon Territory'"
    param_username = arcpy.Parameter()
    param_username.value = 'rgreenens'
    param_additions_only = arcpy.Parameter()
    param_additions_only.value = 'false'
    parameters = [param_geodatabase, param_species, param_secondary, param_version, param_stage,
                  param_external_range_table, param_presence_field, param_usagetype_field, param_review_label,
                  param_overall_review_notes, param_jurisdictions_covered, param_username, param_additions_only]
    ierr.runImportExternalRangeReviewTool(parameters, None)
