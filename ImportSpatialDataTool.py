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
        #arcpy.env.overwriteOutput = True

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        param_geodatabase = parameters[0].valueAsText
        param_import_feature_class = parameters[1].valueAsText
        param_dataset_name = parameters[2].valueAsText
        param_dataset_source = parameters[3].valueAsText
        param_date_received = parameters[4].valueAsText
        param_restrictions = parameters[5].valueAsText

        # check dataset source
        if param_dataset_source not in EBARUtils.readDatasetSources(param_geodatabase, "('S', 'L', 'P')"):
            EBARUtils.displayMessage(messages, 'ERROR: Dataset Source is not valid')
            return

        # use passed geodatabase as workspace (still seems to go to default geodatabase)
        arcpy.env.workspace = param_geodatabase

        # get table name prefix (needed for joined tables and feature classes in enterprise geodatabases)
        table_name_prefix = EBARUtils.getTableNamePrefix(param_geodatabase)

        # determine type of feature class
        desc = arcpy.Describe(param_import_feature_class)
        feature_class_type = desc.shapeType

        # get dataset source id, type and field mappings
        field_dict = {}
        with arcpy.da.SearchCursor(param_geodatabase + '/DatasetSource', ['DatasetSourceID', 'UniqueIDField',
                                                                          'DatasetSourceType', 'URIField',
                                                                          'ScientificNameField', 'MinDateField',
                                                                          'MaxDateField', 'RepAccuracyField',
                                                                          'EORankField', 'AccuracyField'],
                                   "DatasetSourceName = '" + param_dataset_source + "'") as cursor:
            row = None
            for row in EBARUtils.searchCursor(cursor):
                dataset_source_id = row['DatasetSourceID']
                # check match between feature class type and dataset source type
                match = True
                if feature_class_type in ('Polygon', 'MultiPatch'):
                    if row['DatasetSourceType'] != 'P':
                        match = False
                elif feature_class_type in ('Point', 'Multipoint'):
                    if row['DatasetSourceType'] != 'S':
                        match = False
                else: # Polyline
                    if row['DatasetSourceType'] != 'L':
                        match = False
                # populate field mappings
                field_dict['unique_id'] = row['UniqueIDField']
                field_dict['uri'] = row['URIField']
                field_dict['scientific_name'] = row['ScientificNameField']
                field_dict['min_date'] = row['MinDateField']
                field_dict['max_date'] = row['MaxDateField']
                field_dict['rep_accuracy'] = row['RepAccuracyField']
                field_dict['eo_rank'] = row['EORankField']
                field_dict['accuracy'] = row['AccuracyField']
            if row:
                del row
        if not match:
            EBARUtils.displayMessage(messages,
                                     'ERROR: Feature Class Type and Dataset Source Type do not match')
            return

        # encode restriction using domain
        param_restrictions = EBARUtils.encodeRestriction(param_geodatabase, param_restrictions)

        # check/add InputDataset row
        dataset = param_dataset_name + ', ' + param_dataset_source + ', ' + str(param_date_received)
        EBARUtils.displayMessage(messages, 'Checking for dataset [' + dataset + '] and adding if new')
        input_dataset_id, dataset_exists = EBARUtils.checkAddInputDataset(param_geodatabase,
                                                                          param_dataset_name,
                                                                          dataset_source_id,
                                                                          param_date_received,
                                                                          param_restrictions)
        if not dataset_exists:
            EBARUtils.setNewID(param_geodatabase + '/InputDataset', 'InputDatasetID', 'OBJECTID = ' + \
                               str(input_dataset_id))

        # read existing species into dict
        EBARUtils.displayMessage(messages, 'Reading full list of Species and Synonyms')
        species_dict = EBARUtils.readSpecies(param_geodatabase)
        synonym_id_dict = EBARUtils.readSynonyms(param_geodatabase)
        synonym_species_id_dict = EBARUtils.readSynonymSpecies(param_geodatabase)

        # read existing unique IDs into dict
        EBARUtils.displayMessage(messages, 'Reading existing unique IDs')
        id_dict = EBARUtils.readDatasetSourceUniqueIDs(param_geodatabase, table_name_prefix, dataset_source_id, feature_class_type)

        # make temp copy of features being imported so that it is geodatabase format
        EBARUtils.displayMessage(messages, 'Copying features to temporary feature class')
        temp_import_features = 'TempImportFeatures' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.CopyFeatures_management(param_import_feature_class, temp_import_features)

        # pre-processing
        EBARUtils.displayMessage(messages, 'Pre-processing features')
        arcpy.MakeFeatureLayer_management(temp_import_features, 'import_features')
        EBARUtils.checkAddField('import_features', 'SpeciesID', 'LONG')
        EBARUtils.checkAddField('import_features', 'SynonymID', 'LONG')
        EBARUtils.checkAddField('import_features', 'ignore_imp', 'SHORT')
        if feature_class_type in ('Polygon', 'MultiPatch'):
            # EOs can only be polygons
            EBARUtils.checkAddField('import_features', 'eo_rank', 'TEXT')

        # loop to check/add species and flag duplicates
        overall_count = 0
        inaccurate = 0
        duplicates = 0
        no_coords = 0
        no_species_match = 0
        bad_date = 0
        no_match_list = []
        with arcpy.da.UpdateCursor('import_features',
                                   [field_dict['unique_id'], field_dict['scientific_name'], 'SpeciesID', 'SynonymID',
                                    'ignore_imp', 'SHAPE@']) as cursor:
            for row in EBARUtils.updateCursor(cursor):
                overall_count += 1
                if overall_count % 1000 == 0:
                    EBARUtils.displayMessage(messages, 'Species, coordinates and duplicates pre-processed ' + str(overall_count))
                ignore_imp = 0
                # check for species
                species_id = None
                synonym_id = None
                if (row[field_dict['scientific_name']].lower() not in species_dict and
                    row[field_dict['scientific_name']].lower() not in synonym_id_dict):
                    no_species_match += 1
                    ignore_imp = 1
                    if row[field_dict['scientific_name']] not in no_match_list:
                        no_match_list.append(row[field_dict['scientific_name']])
                        EBARUtils.displayMessage(messages,
                                                 'WARNING: No match for species ' + row[field_dict['scientific_name']])
                else:
                    if row[field_dict['scientific_name']].lower() in species_dict:
                        species_id = species_dict[row[field_dict['scientific_name']].lower()]
                    else:
                        species_id = synonym_species_id_dict[row[field_dict['scientific_name']].lower()]
                        synonym_id = synonym_id_dict[row[field_dict['scientific_name']].lower()]
                    # check coordinates
                    if not row['SHAPE@']:
                        no_coords += 1
                        ignore_ime = 1
                    else:
                        # check for duplicates
                        # handle case where integer gets read as float with decimals
                        uid_raw = row[field_dict['unique_id']]
                        if isinstance(uid_raw, float):
                            uid_raw = int(uid_raw)
                        if str(uid_raw) in id_dict:
                            duplicates += 1
                            ignore_imp = 1
                # save
                cursor.updateRow([row[field_dict['unique_id']], row[field_dict['scientific_name']], species_id,
                                  synonym_id, ignore_imp, row['SHAPE@']])
            if overall_count > 0:
                del row
                # index ignore_imp to improve performance
                arcpy.AddIndex_management('import_features', ['ignore_imp'], 'temp_ignore_imp_idx')
        EBARUtils.displayMessage(messages, 'Species and duplicates pre-processed ' + str(overall_count))

        # check accuracy if provided
        if field_dict['accuracy']:
            overall_count = 0
            with arcpy.da.UpdateCursor('import_features',
                                       [field_dict['accuracy'], 'ignore_imp'], 'ignore_imp = 0') as cursor:
                for row in EBARUtils.updateCursor(cursor):
                    overall_count += 1
                    if overall_count % 1000 == 0:
                        EBARUtils.displayMessage(messages, 'Accuracy pre-processed ' + str(overall_count))
                    # handle case where integer gets read as float with decimals
                    accuracy_raw = row[field_dict['accuracy']]
                    if isinstance(accuracy_raw, float):
                        accuracy_raw = int(accuracy_raw)
                    if accuracy_raw:
                        if accuracy_raw > EBARUtils.worst_accuracy:
                            inaccurate += 1
                            cursor.updateRow([row[field_dict['accuracy']], 1])
                if overall_count > 0:
                    del row
            EBARUtils.displayMessage(messages, 'Accuracy pre-processed ' + str(overall_count))

        # other pre-processing (that doesn't result in ignoring input rows)
        if overall_count - duplicates - no_species_match - no_coords - inaccurate > 0:
            # loop to set eo rank
            if field_dict['eo_rank'] and feature_class_type in ('Polygon', 'MultiPatch'):
                count = 0
                with arcpy.da.UpdateCursor('import_features', [field_dict['eo_rank'], 'eo_rank'],
                                           'ignore_imp = 0') as cursor:
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
                with arcpy.da.UpdateCursor('import_features', [field_dict['min_date'], 'MinDate'],
                                           'ignore_imp = 0') as cursor:
                    row = None
                    for row in EBARUtils.updateCursor(cursor):
                        count += 1
                        if count % 1000 == 0:
                            EBARUtils.displayMessage(messages, 'Min Date pre-processed ' + str(count))
                        min_date = None
                        if row[field_dict['min_date']]:
                            if type(row[field_dict['min_date']]).__name__ == 'datetime':
                                min_date = row[field_dict['min_date']]
                            else:
                                # extract date from text
                                min_date = EBARUtils.extractDate(row[field_dict['min_date']].strip())
                        cursor.updateRow([row[field_dict['min_date']], min_date])
                    if row:
                        del row
                EBARUtils.displayMessage(messages, 'Min Date pre-processed ' + str(count))
            if field_dict['max_date']:
                EBARUtils.checkAddField('import_features', 'MaxDate', 'DATE')
                count = 0
                with arcpy.da.UpdateCursor('import_features', [field_dict['max_date'], 'MaxDate'],
                                           'ignore_imp = 0') as cursor:
                    row = None
                    for row in EBARUtils.updateCursor(cursor):
                        count += 1
                        if count % 1000 == 0:
                            EBARUtils.displayMessage(messages, 'Max Date pre-processed ' + str(count))
                        max_date = None
                        if row[field_dict['max_date']]:
                            if type(row[field_dict['max_date']]).__name__ == 'datetime':
                                max_date = row[field_dict['max_date']]
                            else:
                                # extract date from text
                                max_date = EBARUtils.extractDate(row[field_dict['max_date']].strip())
                        cursor.updateRow([row[field_dict['max_date']], max_date])
                        if not max_date:
                            bad_date += 1
                    if row:
                        del row
                EBARUtils.displayMessage(messages, 'Max Date pre-processed ' + str(count))

            # select non-ignore_imp
            arcpy.SelectLayerByAttribute_management('import_features', where_clause='ignore_imp = 0')

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
                                                                    'EORank', 'TEXT'))
            if field_dict['accuracy']:
                field_mappings.addFieldMap(EBARUtils.createFieldMap('import_features', field_dict['accuracy'],
                                                                    'Accuracy', 'LONG'))
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

        # temp clean-up
        # trouble deleting on server only due to locks; could be layer?
        if param_geodatabase[-4:].lower() == '.gdb':
            if arcpy.Exists(temp_import_features):
                arcpy.Delete_management(temp_import_features)

        # summary and end time
        EBARUtils.displayMessage(messages, 'Summary:')
        EBARUtils.displayMessage(messages, 'Processed - ' + str(overall_count))
        EBARUtils.displayMessage(messages, 'Species not matched - ' + str(no_species_match))
        EBARUtils.displayMessage(messages, 'No coordinates - ' + str(no_coords))
        EBARUtils.displayMessage(messages,
                                 'Accuracy worse than ' + str(EBARUtils.worst_accuracy) + ' m - ' + str(inaccurate))
        EBARUtils.displayMessage(messages, 'Duplicates - ' + str(duplicates))
        if field_dict['max_date']:
            EBARUtils.displayMessage(messages, 'Imported without date - ' + str(bad_date))
        else:
            EBARUtils.displayMessage(messages, 'Imported without date - ' + str(overall_count - no_species_match - 
                                                                                no_coords - inaccurate - duplicates))
        end_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'End time: ' + str(end_time))
        elapsed_time = end_time - start_time
        EBARUtils.displayMessage(messages, 'Elapsed time: ' + str(elapsed_time))

        return


# controlling process
if __name__ == '__main__':
    isd = ImportSpatialDataTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value='C:/GIS/EBAR/EBAR-KBA-Dev.gdb'
    param_import_feature_class = arcpy.Parameter()
    param_import_feature_class.value = 'C:/GIS/EBAR/US_CDC_Data/Nature_Serve/EBAR_EOs_NJ_OH_supplement_20200305.shp'
    param_dataset_name = arcpy.Parameter()
    param_dataset_name.value = 'NJ OH Supplement'
    param_dataset_source = arcpy.Parameter()
    param_dataset_source.value = 'US Element Occurrences'
    param_date_received = arcpy.Parameter()
    param_date_received.value = 'March 6, 2020'
    param_restrictions = arcpy.Parameter()
    param_restrictions.value = 'Restricted EBAR'
    parameters = [param_geodatabase, param_import_feature_class, param_dataset_name, param_dataset_source,
                  param_date_received, param_restrictions]
    isd.RunImportSpatialDataTool(parameters, None)
