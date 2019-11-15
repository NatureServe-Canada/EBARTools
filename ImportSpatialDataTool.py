# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: ImportSpatialDataTool.py
# ArcGIS Python tool for importing spatial data into the EBAR geodatabase

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
#import sys
#import traceback
import arcpy
import datetime
#import locale
import EBARUtils
import SpatialFieldMapping


class ImportSpatialDataTool:
    """Import point data into the InputDataset and InputPoint tables of the EBAR geodatabase"""
    def __init__(self):
        pass

    def RunImportSpatialDataTool(self, parameters, messages):
        # check out any needed extension licenses
        #arcpy.CheckOutExtension('Spatial')

        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        if parameters:
            # passed from tool user interface
            param_geodatabase = parameters[0].valueAsText
            param_import_feature_class = parameters[1].valueAsText
            param_dataset_name = parameters[2].valueAsText
            param_dataset_organization = parameters[3].valueAsText
            param_dataset_contact = parameters[4].valueAsText
            param_dataset_source = parameters[5].valueAsText
            param_date_received = parameters[6].valueAsText
            param_restrictions = parameters[7].valueAsText
        else:
            # for debugging, hard code parameters
            param_geodatabase = 'C:/GIS/EBAR/EBAR_test.gdb'
            param_import_feature_class = 'C:/GIS/EBAR/CDN_CDC_Data/Yukon/SF_polygon_Yukon.shp'
            param_dataset_name = 'Yukon Polygon SFs'
            param_dataset_organization = 'Yukon CDC'
            param_dataset_contact = 'Maria Leung'
            param_dataset_source = 'YT CDC Source Feature Polygons'
            param_date_received = 'October 30, 2019'
            param_restrictions = None

        # use passed geodatabase as workspace (still seems to go to default geodatabase)
        arcpy.env.workspace = param_geodatabase

        # check parameters
        # get dataset source id
        with arcpy.da.SearchCursor(param_geodatabase + '/DatasetSource', ['DatasetSourceID'],
                                   "DatasetSourceName = '" + param_dataset_source + "'") as cursor:
            for row in EBARUtils.searchCursor(cursor):
                dataset_source_id = row['DatasetSourceID']
            del row
        # match field_dict with source
        field_dict = SpatialFieldMapping.spatial_field_mapping_dict[param_dataset_source]
        # determine type of feature class
        desc = arcpy.Describe(param_import_feature_class)
        feature_class_type = desc.shapeType

        # check/add InputDataset row
        dataset = param_dataset_name + ', ' + param_dataset_source + ', ' + str(param_date_received)
        EBARUtils.displayMessage(messages, 'Checking for dataset [' + dataset + '] and adding if new')
        input_dataset_id, dataset_exists = EBARUtils.checkAddInputDataset(param_geodatabase,
                                                                          param_dataset_name,
                                                                          param_dataset_organization,
                                                                          param_dataset_contact,
                                                                          dataset_source_id,
                                                                          param_date_received,
                                                                          param_restrictions)
        if not dataset_exists:
            EBARUtils.setNewID(param_geodatabase + '/InputDataset', 'InputDatasetID', 'OBJECTID = ' + \
                               str(input_dataset_id))

        # read existing species into dict
        EBARUtils.displayMessage(messages, 'Reading full list of Species and Synonyms')
        species_dict = EBARUtils.readSpecies(param_geodatabase)
        synonym_id_dict = EBARUtils.readSynonymIDs(param_geodatabase)
        synonym_species_id_dict = EBARUtils.readSynonymSpeciesIDs(param_geodatabase)

        # read existing unique IDs into dict
        EBARUtils.displayMessage(messages, 'Reading existing unique IDs')
        id_dict = EBARUtils.readDatasetSourceUniqueIDs(param_geodatabase, dataset_source_id, feature_class_type)

        # make temp copy of features being imported so that it is geodatabase format
        EBARUtils.displayMessage(messages, 'Copying features to temporary feature class')
        arcpy.CopyFeatures_management(param_import_feature_class, 'TempImportFeatures')

        # pre-processing
        EBARUtils.displayMessage(messages, 'Pre-processing features')
        arcpy.MakeFeatureLayer_management('TempImportFeatures', 'import_features')
        EBARUtils.checkAddField('import_features', 'SpeciesID', 'LONG')
        EBARUtils.checkAddField('import_features', 'SynonymID', 'LONG')
        EBARUtils.checkAddField('import_features', 'ignore', 'SHORT')
        if feature_class_type in ('Polygon', 'MultiPatch'):
            # EOs can only be polygons
            EBARUtils.checkAddField('import_features', 'eo_rank', 'TEXT')

        # loop to check/add species and flag duplicates
        overall_count = 0
        duplicates = 0
        no_species_match = 0
        no_match_list = []
        with arcpy.da.UpdateCursor('import_features',
                                   [field_dict['unique_id'], field_dict['scientific_name'],
                                    'SpeciesID', 'SynonymID', 'ignore']) as cursor:
            for row in EBARUtils.updateCursor(cursor):
                overall_count += 1
                if overall_count % 1000 == 0:
                    EBARUtils.displayMessage(messages, 'Species and duplicates pre-processed ' + str(overall_count))
                ignore = 0
                # check for species
                species_id = None
                synonym_id = None
                if (row[field_dict['scientific_name']] not in species_dict and
                    row[field_dict['scientific_name']] not in synonym_id_dict):
                    no_species_match += 1
                    ignore = 1
                    if row[field_dict['scientific_name']] not in no_match_list:
                        no_match_list.append(row[field_dict['scientific_name']])
                        EBARUtils.displayMessage(messages,
                                                 'WARNING: No match for species ' + row[field_dict['scientific_name']])
                else:
                    if row[field_dict['scientific_name']] in species_dict:
                        species_id = species_dict[row[field_dict['scientific_name']]]
                    else:
                        species_id = synonym_species_id_dict[row[field_dict['scientific_name']]]
                        synonym_id = synonym_id_dict[row[field_dict['scientific_name']]]
                    # check for duplicates
                    # handle case where integer gets read as float with decimals
                    uid_raw = row[field_dict['unique_id']]
                    if isinstance(uid_raw, float):
                        uid_raw = int(uid_raw)
                    if str(uid_raw) in id_dict:
                        duplicates += 1
                        ignore = 1
                # save
                cursor.updateRow([row[field_dict['unique_id']], row[field_dict['scientific_name']], species_id,
                                  synonym_id, ignore])
            if overall_count > 0:
                del row
        EBARUtils.displayMessage(messages, 'Species and duplicates pre-processed ' + str(overall_count))

        if overall_count - duplicates - no_species_match > 0:
            # select non-ignore
            arcpy.SelectLayerByAttribute_management('import_features', where_clause='ignore = 0')

            # loop to set eo rank
            if field_dict['eo_rank'] and feature_class_type in ('Polygon', 'MultiPatch'):
                count = 0
                with arcpy.da.UpdateCursor('import_features', [field_dict['eo_rank'], 'eo_rank']) as cursor:
                    for row in EBARUtils.updateCursor(cursor):
                        count += 1
                        if count % 1000 == 0:
                            EBARUtils.displayMessage(messages, 'EO Rank pre-processed ' + str(count))
                        # encode eo rank if full description provided
                        eo_rank = row[field_dict['eo_rank']]
                        if eo_rank:
                            if len(eo_rank) > 2:
                                eo_rank = EBARUtils.eo_rank_dict[eo_rank]
                            # save
                            cursor.updateRow([row[field_dict['eo_rank']], eo_rank])
                    if count > 0:
                        del row
                EBARUtils.displayMessage(messages, 'EO Rank pre-processed ' + str(count))

            # pre-process dates
            if field_dict['min_date']:
                EBARUtils.checkAddField('import_features', 'MinDate', 'DATE')
                count = 0
                with arcpy.da.UpdateCursor('import_features', [field_dict['min_date'], 'MinDate']) as cursor:
                    for row in EBARUtils.updateCursor(cursor):
                        count += 1
                        if count % 1000 == 0:
                            EBARUtils.displayMessage(messages, 'Min Date pre-processed ' + str(count))
                        min_date = None
                        if field_dict['min_date']:
                            if row[field_dict['min_date']]:
                                min_date = EBARUtils.extractDate(row[field_dict['min_date']].strip())
                        cursor.updateRow([row[field_dict['min_date']], min_date])
                    del row
                EBARUtils.displayMessage(messages, 'Min Date pre-processed ' + str(count))
            if field_dict['max_date']:
                EBARUtils.checkAddField('import_features', 'MaxDate', 'DATE')
                count = 0
                with arcpy.da.UpdateCursor('import_features', [field_dict['max_date'], 'MaxDate']) as cursor:
                    for row in EBARUtils.updateCursor(cursor):
                        count += 1
                        if count % 1000 == 0:
                            EBARUtils.displayMessage(messages, 'Max Date pre-processed ' + str(count))
                        max_date = None
                        if field_dict['max_date']:
                            if row[field_dict['max_date']]:
                                max_date = EBARUtils.extractDate(row[field_dict['max_date']].strip())
                        cursor.updateRow([row[field_dict['max_date']], max_date])
                    del row
                EBARUtils.displayMessage(messages, 'Max Date pre-processed ' + str(count))

            # add and set column for input dataset
            EBARUtils.checkAddField('import_features', 'InDSID', 'LONG')
            arcpy.CalculateField_management('import_features', 'InDSID', input_dataset_id)

            # append to InputPolygon/Point/Line
            EBARUtils.displayMessage(messages, 'Appending features')
            # map fields
            field_mappings = arcpy.FieldMappings()
            field_mappings.addFieldMap(EBARUtils.createFieldMap('import_features', 'InDSID',
                                                                'InputDatasetID', 'LONG'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('import_features', 'SpeciesID',
                                                                'SpeciesID', 'LONG'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('import_features', 'SynonymID',
                                                                'SynonymID', 'LONG'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('import_features', field_dict['unique_id'],
                                                                'DatasetSourceUniqueID', 'TEXT'))
            if field_dict['uri']:
                field_mappings.addFieldMap(EBARUtils.createFieldMap('import_features', field_dict['uri'],
                                                                    'URI', 'TEXT'))
            if field_dict['min_date']:
                field_mappings.addFieldMap(EBARUtils.createFieldMap('import_features', 'MinDate',
                                                                    'MinDate', 'DATE'))
            if field_dict['max_date']:
                field_mappings.addFieldMap(EBARUtils.createFieldMap('import_features', 'MaxDate',
                                                                    'MaxDate', 'DATE'))
            if field_dict['rep_accuracy']:
                field_mappings.addFieldMap(EBARUtils.createFieldMap('import_features', field_dict['rep_accuracy'],
                                                                    'RepresentationAccuracy', 'TEXT'))
            if field_dict['eo_rank'] and feature_class_type in ('Polygon', 'MultiPatch'):
                field_mappings.addFieldMap(EBARUtils.createFieldMap('import_features', 'eo_rank',
                                                                    'EORank', 'DATE'))
            # append
            if feature_class_type in ('Polygon', 'MultiPatch'):
                destination = param_geodatabase + '/InputPolygon'
                id_field = 'InputPolygonID'
            elif feature_class_type in ('Point', 'Multipoint'):
                destination = param_geodatabase + '/InputPoint'
                id_field = 'InputPointID'
            else: # Polyline
                destination = param_geodatabase + '/InputLine'
                id_field = 'InputLineID'
            arcpy.Append_management('import_features', destination, 'NO_TEST', field_mappings)
            # set new id (will reset any previous IDs from same input dataset)
            EBARUtils.setNewID(destination, id_field, 'InputDatasetID = ' + str(input_dataset_id))

        # summary and end time
        EBARUtils.displayMessage(messages, 'Summary:')
        EBARUtils.displayMessage(messages, 'Processed - ' + str(overall_count))
        EBARUtils.displayMessage(messages, 'Species not matched - ' + str(no_species_match))
        EBARUtils.displayMessage(messages, 'Duplicates - ' + str(duplicates))
        end_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'End time: ' + str(end_time))
        elapsed_time = end_time - start_time
        EBARUtils.displayMessage(messages, 'Elapsed time: ' + str(elapsed_time))

        return


# controlling process
if __name__ == '__main__':
    isd = ImportSpatialDataTool()
    # hard code parameters for debugging
    isd.RunImportSpatialDataTool(None, None)
