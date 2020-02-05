# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: ApplyExternalRangeReviewTool.py
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


class ApplyExternalRangeReviewTool:
    """Create review records for an exising range map based on third-party polygons"""
    def __init__(self):
        pass

    def RunApplyExternalRangeReviewTool(self, parameters, messages):
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
        param_species = parameters[1].valueAsText
        param_version = parameters[2].valueAsText
        param_stage = parameters[3].valueAsText
        param_external_range_polygons = parameters[4].valueAsText
        param_scientific_name_field = parameters[5].valueAsText
        param_ecoshape_name_field = parameters[6].valueAsText
        param_review_label = parameters[7].valueAsText
        param_jurisdictions_covered = parameters[8].valueAsText
        # convert to Python list
        param_jurisdictions_covered = param_jurisdictions_covered.replace("'", '')
        param_jurisdictions_covered = param_jurisdictions_covered.split(';')
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

        # check for range map record and add if necessary
        EBARUtils.displayMessage(messages, 'Checking for existing range map')
        range_map_id = None
        arcpy.MakeTableView_management(param_geodatabase + '/RangeMap', 'range_map_view',
                                       'SpeciesID = ' + str(species_id) +
                                       " AND RangeVersion = '" + param_version +
                                       "' AND RangeStage = '" + param_stage + "'")
        with arcpy.da.SearchCursor('range_map_view', ['RangeMapID']) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                range_map_id = row['RangeMapID']
            if range_map_id:
                # found
                del row
            else:
                EBARUtils.displayMessage(messages, 'ERROR: Range Map not found')
                # terminate with error
                return
                #raise arcpy.ExecuteError

        # build list of jurisdictions
        EBARUtils.displayMessage(messages, 'Building list of jurisdictions')
        jur_dict = {}
        with arcpy.da.SearchCursor(param_geodatabase + '/Jurisdiction',
                                   ['JurisdictionID', 'JurisdictionName']) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                jur_dict[row['JurisdictionID']] = row['JurisdictionName']
            if len(jur_dict) > 0:
                del row

        # subset external polygons (by species name if given)
        arcpy.MakeFeatureLayer_management(param_external_range_polygons, 'external_polygons_layer')
        if param_scientific_name_field:
            arcpy.SelectLayerByAttribute_management('external_polygons_layer', 'NEW_SELECTION',
                                                    param_scientific_name_field + "= '" + param_species + "'")

        # subset RangeMapEcoshapes (by range map)
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/Ecoshape', 'ecoshapes_layer')
        arcpy.AddJoin_management('ecoshapes_layer', 'EcoshapeID', param_geodatabase + '/RangeMapEcoshape',
                                 'EcoshapeID', 'KEEP_COMMON')
        arcpy.SelectLayerByAttribute_management('ecoshapes_layer', 'NEW_SELECTION',
                                                table_name_prefix + 'RangeMapEcoshape.RangeMapID = ' + \
                                                    str(range_map_id))

        # create Review record
        # how to dynamically get username (only applicable when connected to enterprise gdb/service???
        EBARUtils.displayMessage(messages, 'Creating Review record')
        with arcpy.da.InsertCursor(param_geodatabase + '/Review',
                                   ['RangeMapID', 'Username', 'DateCompleted', 'ReviewNotes']) as cursor:
            object_id = cursor.insertRow([range_map_id, 'rgreenens', datetime.datetime.now(),
                                          param_review_label + ' auto-applied'])
        # review_id is an auto-generated value on the server!
        #EBARUtils.setNewID(param_geodatabase + '/Review', 'ReviewID', 'OBJECTID = ' + str(review_id))
        with arcpy.da.SearchCursor(param_geodatabase + '/Review', ['ReviewID'],
                                   'OBJECTID = ' + str(object_id)) as search_cursor:
            for row in EBARUtils.searchCursor(search_cursor):
                review_id = row['ReviewID']
            del row

        # check each RangeMapEcoshape and create EcoshapeReview Remove record for any in covered jurisdictions but not
        # in external polygons
        EBARUtils.displayMessage(messages, 'Creating EcoshapeReview remove records')
        remove_count = 0
        if param_ecoshape_name_field:
            # read external names
            external_ecoshapes = []
            with arcpy.da.SearchCursor('external_polygons_layer', [param_ecoshape_name_field]) as search_cursor:
                for row in EBARUtils.searchCursor(search_cursor):
                    external_ecoshapes.append(row[param_ecoshape_name_field])
                if len(external_ecoshapes) > 0:
                    del row
            # check against EBAR ecoshapes
            with arcpy.da.SearchCursor('ecoshapes_layer',
                                       [table_name_prefix + 'RangeMapEcoshape.RangeMapID',
                                        table_name_prefix + 'Ecoshape.JurisdictionID',
                                        table_name_prefix + 'Ecoshape.EcoshapeID',
                                        table_name_prefix + 'Ecoshape.EcoshapeName']) as search_cursor:
                for row in EBARUtils.searchCursor(search_cursor):
                    if (row[table_name_prefix + 'RangeMapEcoshape.RangeMapID'] == range_map_id and
                        jur_dict[row[table_name_prefix + 'Ecoshape.JurisdictionID']] in param_jurisdictions_covered and
                        row[table_name_prefix + 'Ecoshape.EcoshapeName'] not in external_ecoshapes):
                        with arcpy.da.InsertCursor(param_geodatabase + '/EcoshapeReview',
                                                   ['EcoshapeID', 'ReviewID', 'RemovalReason', 'EcoshapeReviewNotes',
                                                    'UseForMapGen', 'AddRemove', 'Username']) as cursor:
                            cursor.insertRow([row[table_name_prefix + 'Ecoshape.EcoshapeID'], review_id, 'O',
                                              'Not in ' + param_review_label, 1, 2, 'rgreenens'])
                            remove_count += 1
        else:
            # use intersect if no external ecoshape names that match EBAR ecoshape names???
            #arcpy.SelectLayerByLocation_management('ecoshapes_layer', 'INTERSECT', 'external_polygons_layer')
            pass
           
        # summary and end time
        EBARUtils.displayMessage(messages, str(remove_count) + ' EcshopeReview remove records created')
        end_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'End time: ' + str(end_time))
        elapsed_time = end_time - start_time
        EBARUtils.displayMessage(messages, 'Elapsed time: ' + str(elapsed_time))
        return
            

# controlling process
if __name__ == '__main__':
    aerr = ApplyExternalRangeReviewTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:/GIS/EBAR/EBAR-KBA-Dev.gdb'
    param_species = arcpy.Parameter()
    param_species.value = 'Crataegus atrovirens'
    param_version = arcpy.Parameter()
    param_version.value = '0.9'
    param_stage = arcpy.Parameter()
    param_stage.value = 'Auto-generated'
    param_external_range_polygons = arcpy.Parameter()
    param_external_range_polygons.value = 'C:/GIS/EBAR/CDN_CDC_Data/British_Columbia/BC_vasc_plant_ranges_for_EBAR' + \
        '/Vasc_Plants_Reviewed.gdb/vasc_plants_ryan'
    param_scientific_name_field = arcpy.Parameter()
    param_scientific_name_field .value = 'SCI_NAME'
    param_ecoshape_name_field = arcpy.Parameter()
    param_ecoshape_name_field .value = 'ECOSECTION_NAME'
    param_review_label = arcpy.Parameter()
    param_review_label.value = 'BC expert review'
    parameters = [param_geodatabase, param_species, param_version, param_stage, param_external_range_polygons,
                  param_scientific_name_field, param_ecoshape_name_field, param_review_label]
    aerr.RunApplyExternalRangeReviewTool(parameters, None)
