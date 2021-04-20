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
import arcpy
import datetime
import EBARUtils


class ImportSpatialDataTool:
    """Import point data into the InputDataset and InputPoint tables of the EBAR geodatabase"""
    def __init__(self):
        pass

    def runImportSpatialDataTool(self, parameters, messages):
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

        # populate fixed field mappings
        field_dict = {}
        field_dict['InputDatasetID'] = 'InDSID'
        field_dict['SpeciesID'] = 'SpeciesID'
        field_dict['SynonymID'] = 'SynonymID'
        field_dict['MinDate'] = 'MinDate'
        field_dict['MaxDate'] = 'MaxDate'
        field_dict['SHAPE@'] = 'SHAPE@'

        # get dataset source id, type and dynamic field mappings
        with arcpy.da.SearchCursor(param_geodatabase + '/DatasetSource', ['DatasetSourceID',
                                                                          'UniqueIDField',
                                                                          'DatasetSourceType',
                                                                          'URIField',
                                                                          'ScientificNameField',
                                                                          'SRankField',
                                                                          'RoundedSRankField',
                                                                          'MinDateField',
                                                                          'MaxDateField',
                                                                          'RepAccuracyField',
                                                                          'EORankField',
                                                                          'AccuracyField',
                                                                          'OriginField',
                                                                          'SeasonalityField',
                                                                          'SubnationField',
                                                                          'EODataField',
                                                                          'GenDescField',
                                                                          'EORankDescField',
                                                                          'SurveyDateField',
                                                                          'RepAccuracyCommentField',
                                                                          'ConfidenceExtentField',
                                                                          'ConfidenceExtentDescField',
                                                                          'DataSensitivityField',
                                                                          'DataSensitivityCatField',
                                                                          'ESTDataSensitivityField',
                                                                          'ESTDataSensitivityCatField',
                                                                          'IDConfirmedField',
                                                                          'EORankDateField',
                                                                          'EORankCommentsField',
                                                                          'AdditionalInvNeededField',
                                                                          'OwnershipField',
                                                                          'OwnerCommentsField',
                                                                          'DataQCStatusField',
                                                                          'MapQCStatusField',
                                                                          'QCCommentsField',
                                                                          'EOIDField',
                                                                          'SFIDField',
                                                                          'DescriptorField',
                                                                          'LocatorField',
                                                                          'MappingCommentsField',
                                                                          'DigitizingCommentsField',
                                                                          'LocUncertaintyTypeField',
                                                                          'LocUncertaintyDistClsField',
                                                                          'LocUncertaintyDistUnitField',
                                                                          'LocUseClassField',
                                                                          'IndependentSFField',
                                                                          'UnsuitableHabExcludedField'],
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
                # populate dynamic field mappings
                field_dict['DatasetSourceUniqueID'] = row['UniqueIDField']
                field_dict['URI'] = row['URIField']
                field_dict['scientific_name'] = row['ScientificNameField']
                field_dict['S_RANK'] = row['SRankField']
                field_dict['ROUNDED_S_RANK'] = row['RoundedSRankField']
                field_dict['EST_DATA_SENS'] = row['ESTDataSensitivityField']
                field_dict['EST_DATASEN_CAT'] = row['ESTDataSensitivityCatField']
                field_dict['min_date'] = row['MinDateField']
                field_dict['max_date'] = row['MaxDateField']
                field_dict['RepresentationAccuracy'] = row['RepAccuracyField']
                field_dict['Accuracy'] = row['AccuracyField']
                field_dict['Origin'] = row['OriginField']
                field_dict['Seasonality'] = row['SeasonalityField']
                field_dict['Subnation'] = row['SubnationField']
                field_dict['DataSensitivity'] = row['DataSensitivityField']
                field_dict['DataSensitivityCat'] = row['DataSensitivityCatField']
                field_dict['DataQCStatus'] = row['DataQCStatusField']
                field_dict['MapQCStatus'] = row['MapQCStatusField']
                field_dict['QCComments'] = row['QCCommentsField']
                field_dict['EOID'] = row['EOIDField']
                field_dict['SFID'] = row['SFIDField']
                field_dict['Descriptor'] = row['DescriptorField']
                field_dict['Locator'] = row['LocatorField']
                field_dict['MappingComments'] = row['MappingCommentsField']
                field_dict['DigitizingComments'] = row['DigitizingCommentsField']
                field_dict['LocUncertaintyType'] = row['LocUncertaintyTypeField']
                field_dict['LocUncertaintyDistCls'] = row['LocUncertaintyDistClsField']
                field_dict['LocUncertaintyDistUnit'] = row['LocUncertaintyDistUnitField']
                field_dict['LocUseClass'] = row['LocUseClassField']
                field_dict['IndependentSF'] = row['IndependentSFField']
                field_dict['UnsuitableHabExcluded'] = row['UnsuitableHabExcludedField']
                if feature_class_type in ('Polygon', 'MultiPatch'):
                    field_dict['EORank'] = row['EORankField']
                    field_dict['EOData'] = row['EODataField']
                    field_dict['GenDesc'] = row['GenDescField']
                    field_dict['EORankDesc'] = row['EORankDescField']
                    field_dict['SurveyDate'] = row['SurveyDateField']
                    field_dict['RepAccuracyComment'] = row['RepAccuracyCommentField']
                    field_dict['ConfidenceExtent'] = row['ConfidenceExtentField']
                    field_dict['ConfidenceExtentDesc'] = row['ConfidenceExtentDescField']
                    field_dict['IDConfirmed'] = row['IDConfirmedField']
                    field_dict['EORankDate'] = row['EORankDateField']
                    field_dict['EORankComments'] = row['EORankCommentsField']
                    field_dict['AdditionalInvNeeded'] = row['AdditionalInvNeededField']
                    field_dict['Ownership'] = row['OwnershipField']
                    field_dict['OwnerComments'] = row['OwnerCommentsField']
            if row:
                del row
        if not match:
            EBARUtils.displayMessage(messages,
                                     'ERROR: Feature Class Type and Dataset Source Type do not match')
            return

        # populate types
        type_dict = {}
        type_dict['InputDatasetID'] = 'LONG'
        type_dict['SpeciesID'] = 'LONG'
        type_dict['SynonymID'] = 'LONG'
        type_dict['MinDate'] = 'DATE'
        type_dict['MaxDate'] = 'DATE'
        type_dict['DatasetSourceUniqueID'] = 'TEXT'
        type_dict['URI'] = 'TEXT'
        type_dict['RepresentationAccuracy'] = 'TEXT'
        type_dict['EORank'] = 'TEXT'
        type_dict['Accuracy'] = 'LONG'
        type_dict['Origin'] = 'TEXT'
        type_dict['Seasonality'] = 'TEXT'
        type_dict['Subnation'] = 'TEXT'
        type_dict['EOData'] = 'TEXT'
        type_dict['GenDesc'] = 'TEXT'
        type_dict['EORankDesc'] = 'TEXT'
        type_dict['SurveyDate'] = 'TEXT'
        type_dict['RepAccuracyComment'] = 'TEXT'
        type_dict['ConfidenceExtent'] = 'TEXT'
        type_dict['ConfidenceExtentDesc'] = 'TEXT'
        type_dict['DataSensitivity'] = 'TEXT'
        type_dict['DataSensitivityCat'] = 'TEXT'
        type_dict['IDConfirmed'] = 'TEXT'
        type_dict['EORankDate'] = 'TEXT'
        type_dict['EORankComments'] = 'TEXT'
        type_dict['AdditionalInvNeeded'] = 'TEXT'
        type_dict['Ownership'] = 'TEXT'
        type_dict['OwnerComments'] = 'TEXT'
        type_dict['DataQCStatus'] = 'TEXT'
        type_dict['MapQCStatus'] = 'TEXT'
        type_dict['QCComments'] = 'TEXT'
        type_dict['EOID'] = 'LONG'
        type_dict['SFID'] = 'LONG'
        type_dict['Descriptor'] = 'TEXT'
        type_dict['Locator'] = 'TEXT'
        type_dict['MappingComments'] = 'TEXT'
        type_dict['DigitizingComments'] = 'TEXT'
        type_dict['LocUncertaintyType'] = 'TEXT'
        type_dict['LocUncertaintyDistCls'] = 'TEXT'
        type_dict['LocUncertaintyDistUnit'] = 'TEXT'
        type_dict['LocUseClass'] = 'TEXT'
        type_dict['IndependentSF'] = 'TEXT'
        type_dict['UnsuitableHabExcluded'] = 'TEXT'

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

        # read existing species into dict
        EBARUtils.displayMessage(messages, 'Reading full list of Species and Synonyms')
        species_dict = EBARUtils.readSpecies(param_geodatabase)
        synonym_id_dict = EBARUtils.readSynonyms(param_geodatabase)
        synonym_species_id_dict = EBARUtils.readSynonymSpecies(param_geodatabase)

        # read existing unique IDs into dict
        EBARUtils.displayMessage(messages, 'Reading existing unique IDs')
        id_dict = EBARUtils.readDatasetSourceUniqueIDs(param_geodatabase, table_name_prefix, dataset_source_id,
                                                       feature_class_type)

        # make temp copy of features being imported so that it is geodatabase format
        EBARUtils.displayMessage(messages, 'Copying features to temporary feature class')
        temp_import_features = 'TempImportFeatures' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.CopyFeatures_management(param_import_feature_class, temp_import_features)

        # pre-processing
        EBARUtils.displayMessage(messages, 'Pre-processing features')
        arcpy.MakeFeatureLayer_management(temp_import_features, 'import_features')
        # add/set columns
        EBARUtils.checkAddField('import_features', 'InDSID', 'LONG')
        arcpy.CalculateField_management('import_features', 'InDSID', input_dataset_id)
        EBARUtils.checkAddField('import_features', 'SpeciesID', 'LONG')
        EBARUtils.checkAddField('import_features', 'SynonymID', 'LONG')
        EBARUtils.checkAddField('import_features', 'MinDate', 'DATE')
        EBARUtils.checkAddField('import_features', 'MaxDate', 'DATE')
        EBARUtils.checkAddField('import_features', 'ignore_imp', 'SHORT')
        if feature_class_type in ('Polygon', 'MultiPatch'):
            # EOs can only be polygons
            EBARUtils.checkAddField('import_features', 'eo_rank', 'TEXT')

        # loop to check/add species and flag duplicates
        overall_count = 0
        added = 0
        duplicates = 0
        inaccurate = 0
        no_coords = 0
        no_species_match = 0
        bad_date = 0
        no_match_list = []
        with arcpy.da.UpdateCursor('import_features',
                                   [field_dict['DatasetSourceUniqueID'], field_dict['scientific_name'],
                                    field_dict['Subnation'], 'SpeciesID', 'SynonymID', 'ignore_imp',
                                    'SHAPE@']) as cursor:
            for row in EBARUtils.updateCursor(cursor):
                overall_count += 1
                if overall_count % 1000 == 0:
                    EBARUtils.displayMessage(messages, 'Subnation, species, coordinates and duplicates pre-processed ' + str(overall_count))
                # ignore_imp: 0=Add, 1=Ignore(species, coords), 2=Duplicate/Update
                ignore_imp = 0
                # check for species
                species_id = None
                synonym_id = None
                subnation = None
                if (row[field_dict['scientific_name']].lower() not in species_dict and
                    row[field_dict['scientific_name']].lower() not in synonym_id_dict):
                    no_species_match += 1
                    ignore_imp = 1
                    if row[field_dict['scientific_name']] not in no_match_list:
                        no_match_list.append(row[field_dict['scientific_name']])
                        EBARUtils.displayMessage(messages,
                                                 'WARNING: No match for species ' + row[field_dict['scientific_name']])
                else:
                    if field_dict['Subnation']:
                        subnation = row[field_dict['Subnation']]
                        if subnation in EBARUtils.subnation_dict:
                            # convert to abbreviation
                            subnation = EBARUtils.subnation_dict[subnation]
                    if row[field_dict['scientific_name']].lower() in species_dict:
                        species_id = species_dict[row[field_dict['scientific_name']].lower()]
                    else:
                        species_id = synonym_species_id_dict[row[field_dict['scientific_name']].lower()]
                        synonym_id = synonym_id_dict[row[field_dict['scientific_name']].lower()]
                    # check coordinates
                    if not row['SHAPE@']:
                        no_coords += 1
                        ignore_imp = 1
                    else:
                        # check for duplicates
                        # handle case where integer gets read as float with decimals
                        uid_raw = row[field_dict['DatasetSourceUniqueID']]
                        if isinstance(uid_raw, float):
                            uid_raw = int(uid_raw)
                        #if str(uid_raw) + ' - ' + str(species_id) in id_dict:
                        if str(uid_raw) in id_dict:
                            duplicates += 1
                            ignore_imp = 2
                # save
                cursor.updateRow([row[field_dict['DatasetSourceUniqueID']], row[field_dict['scientific_name']],
                                  subnation, species_id, synonym_id, ignore_imp, row['SHAPE@']])
            if overall_count > 0:
                del row
                # index ignore_imp to improve performance
                arcpy.AddIndex_management('import_features', ['ignore_imp'], 'temp_ignore_imp_idx')
        EBARUtils.displayMessage(messages, 'Subnation, species, coordinates and duplicates pre-processed ' + str(overall_count))

        # check accuracy if provided
        if field_dict['Accuracy']:
            loop_count = 0
            with arcpy.da.UpdateCursor('import_features',
                                       [field_dict['Accuracy'], 'ignore_imp'], 'ignore_imp <> 1') as cursor:
                for row in EBARUtils.updateCursor(cursor):
                    loop_count += 1
                    if loop_count % 1000 == 0:
                        EBARUtils.displayMessage(messages, 'Accuracy pre-processed ' + str(loop_count))
                    # handle case where integer gets read as float with decimals
                    accuracy_raw = row[field_dict['Accuracy']]
                    if isinstance(accuracy_raw, float):
                        accuracy_raw = int(accuracy_raw)
                    if accuracy_raw:
                        if accuracy_raw > EBARUtils.worst_accuracy:
                            inaccurate += 1
                            cursor.updateRow([row[field_dict['Accuracy']], 1])
                if loop_count > 0:
                    del row
            EBARUtils.displayMessage(messages, 'Accuracy pre-processed ' + str(loop_count))

        # other pre-processing (that doesn't result in ignoring input rows)
        #if overall_count - duplicates - no_species_match - no_coords - inaccurate > 0:
        if overall_count - no_species_match - no_coords - inaccurate > 0:
            # loop to set eo rank
            if feature_class_type in ('Polygon', 'MultiPatch'):
                if field_dict['EORank']:
                    loop_count = 0
                    with arcpy.da.UpdateCursor('import_features', [field_dict['EORank'], 'eo_rank'],
                                               'ignore_imp <> 1') as cursor:
                        for row in EBARUtils.updateCursor(cursor):
                            loop_count += 1
                            if loop_count % 1000 == 0:
                                EBARUtils.displayMessage(messages, 'EO Rank pre-processed ' + str(loop_count))
                            # encode eo rank if full description provided
                            eo_rank = row[field_dict['EORank']]
                            if eo_rank:
                                if len(eo_rank) > 2:
                                    eo_rank = EBARUtils.eo_rank_dict[eo_rank]
                                # save
                                cursor.updateRow([row[field_dict['EORank']], eo_rank])
                        if loop_count > 0:
                            del row
                    EBARUtils.displayMessage(messages, 'EO Rank pre-processed ' + str(loop_count))

            # pre-process dates
            if field_dict['min_date']:
                loop_count = 0
                with arcpy.da.UpdateCursor('import_features', [field_dict['min_date'], 'MinDate'],
                                           'ignore_imp <> 1') as cursor:
                    row = None
                    for row in EBARUtils.updateCursor(cursor):
                        loop_count += 1
                        if loop_count % 1000 == 0:
                            EBARUtils.displayMessage(messages, 'Min Date pre-processed ' + str(loop_count))
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
                EBARUtils.displayMessage(messages, 'Min Date pre-processed ' + str(loop_count))
            if field_dict['max_date']:
                loop_count = 0
                with arcpy.da.UpdateCursor('import_features', [field_dict['max_date'], 'MaxDate'],
                                           'ignore_imp <> 1') as cursor:
                    row = None
                    for row in EBARUtils.updateCursor(cursor):
                        loop_count += 1
                        if loop_count % 1000 == 0:
                            EBARUtils.displayMessage(messages, 'Max Date pre-processed ' + str(loop_count))
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
                EBARUtils.displayMessage(messages, 'Max Date pre-processed ' + str(loop_count))

            # pre-process species subnational fields
            if field_dict['S_RANK']:
                loop_count = 0
                with arcpy.da.SearchCursor('import_features', [field_dict['S_RANK'], 'SpeciesID',
                                                               field_dict['Subnation']], 'ignore_imp <> 1') as cursor:
                    row = None
                    for row in EBARUtils.updateCursor(cursor):
                        loop_count += 1
                        if loop_count % 1000 == 0:
                            EBARUtils.displayMessage(messages, 'S_RANK pre-processed ' + str(loop_count))
                        # update ranks in BIOTICS_ELEMENT_NATIONAL table, if provided
                        if row[field_dict['S_RANK']] and row[field_dict['Subnation']]:
                            EBARUtils.updateBioticsSubnational(param_geodatabase, row[field_dict['S_RANK']], None,
                                                               None, None, row[field_dict['Subnation']],
                                                               row['SpeciesID'])
                    if row:
                        del row
                EBARUtils.displayMessage(messages, 'S_RANK pre-processed ' + str(loop_count))
            if field_dict['ROUNDED_S_RANK']:
                loop_count = 0
                with arcpy.da.SearchCursor('import_features', [field_dict['ROUNDED_S_RANK'], 'SpeciesID',
                                                               field_dict['Subnation']], 'ignore_imp <> 1') as cursor:
                    row = None
                    for row in EBARUtils.updateCursor(cursor):
                        loop_count += 1
                        if loop_count % 1000 == 0:
                            EBARUtils.displayMessage(messages, 'ROUNDED_S_RANK pre-processed ' + str(loop_count))
                        # update ranks in BIOTICS_ELEMENT_NATIONAL table, if provided
                        if row[field_dict['ROUNDED_S_RANK']] and row[field_dict['Subnation']]:
                            EBARUtils.updateBioticsSubnational(param_geodatabase, None,
                                                               row[field_dict['ROUNDED_S_RANK']],
                                                               None, None, row[field_dict['Subnation']],
                                                               row['SpeciesID'])
                    if row:
                        del row
                EBARUtils.displayMessage(messages, 'ROUNDED_S_RANK pre-processed ' + str(loop_count))
            if field_dict['EST_DATA_SENS']:
                loop_count = 0
                with arcpy.da.SearchCursor('import_features', [field_dict['EST_DATA_SENS'], 'SpeciesID',
                                                               field_dict['Subnation']], 'ignore_imp <> 1') as cursor:
                    row = None
                    for row in EBARUtils.updateCursor(cursor):
                        loop_count += 1
                        if loop_count % 1000 == 0:
                            EBARUtils.displayMessage(messages, 'EST_DATA_SENS pre-processed ' + str(loop_count))
                        # update ranks in BIOTICS_ELEMENT_NATIONAL table, if provided
                        if row[field_dict['EST_DATA_SENS']] and row[field_dict['Subnation']]:
                            EBARUtils.updateBioticsSubnational(param_geodatabase, None, None,
                                                               row[field_dict['EST_DATA_SENS']],
                                                               None, row[field_dict['Subnation']],
                                                               row['SpeciesID'])
                    if row:
                        del row
                EBARUtils.displayMessage(messages, 'EST_DATA_SENS pre-processed ' + str(loop_count))
            if field_dict['EST_DATASEN_CAT']:
                loop_count = 0
                with arcpy.da.SearchCursor('import_features', [field_dict['EST_DATASEN_CAT'], 'SpeciesID',
                                                               field_dict['Subnation']], 'ignore_imp <> 1') as cursor:
                    row = None
                    for row in EBARUtils.updateCursor(cursor):
                        loop_count += 1
                        if loop_count % 1000 == 0:
                            EBARUtils.displayMessage(messages, 'EST_DATASEN_CAT pre-processed ' + str(loop_count))
                        # update ranks in BIOTICS_ELEMENT_NATIONAL table, if provided
                        if row[field_dict['EST_DATASEN_CAT']] and row[field_dict['Subnation']]:
                            EBARUtils.updateBioticsSubnational(param_geodatabase, None, None,
                                                               row[field_dict['EST_DATASEN_CAT']],
                                                               None, row[field_dict['Subnation']],
                                                               row['SpeciesID'])
                    if row:
                        del row
                EBARUtils.displayMessage(messages, 'EST_DATASEN_CAT pre-processed ' + str(loop_count))

            # select for appending
            arcpy.SelectLayerByAttribute_management('import_features', where_clause='ignore_imp = 0')
            result = arcpy.GetCount_management('import_features')
            added = result[0]

            # append to InputPolygon/Point/Line
            EBARUtils.displayMessage(messages, 'Appending features')
            # map fields
            field_mappings = arcpy.FieldMappings()
            for key in field_dict:
                # exclude fields that were used for preprocessing
                if key not in ['scientific_name', 'S_RANK', 'ROUNDED_S_RANK', 'EST_DATA_SENS', 'EST_DATASEN_CAT',
                               'min_date', 'max_date', 'SHAPE@']:
                    if field_dict[key]:
                        field_mappings.addFieldMap(EBARUtils.createFieldMap('import_features', field_dict[key], key,
                                                                            type_dict[key]))
            # append
            if feature_class_type in ('Polygon', 'MultiPatch'):
                destination = param_geodatabase + '/InputPolygon'
            elif feature_class_type in ('Point', 'Multipoint'):
                destination = param_geodatabase + '/InputPoint'
            else: # Polyline
                destination = param_geodatabase + '/InputLine'
            arcpy.Append_management('import_features', destination, 'NO_TEST', field_mappings)

            # update duplicates
            if duplicates > 0:
                EBARUtils.displayMessage(messages, 'Updating features')
                # existing records could be in any InputDataset linked to the DatasetSource
                input_dataset_ids = ''
                with arcpy.da.SearchCursor(param_geodatabase + '/InputDataset', ['InputDatasetID'],
                                           'DatasetSourceID = ' + str(dataset_source_id)) as cursor:
                    row = None
                    for row in EBARUtils.searchCursor(cursor):
                        if len(input_dataset_ids) == 0:
                            input_dataset_ids += '('
                        else:
                            input_dataset_ids += ', '
                        input_dataset_ids += str(row['InputDatasetID'])
                    if row:
                        del row
                input_dataset_ids += ')'
                # use most fields from dict to automate
                src_fields = []
                for key in field_dict:
                    # exclude fields that were used for preprocessing
                    if key not in ['scientific_name', 'S_RANK', 'ROUNDED_S_RANK', 'EST_DATA_SENS', 'EST_DATASEN_CAT',
                                   'min_date', 'max_date']:
                        if field_dict[key]:
                            src_fields.append(field_dict[key])
                arcpy.SelectLayerByAttribute_management('import_features', 'CLEAR_SELECTION')
                with arcpy.da.SearchCursor('import_features', src_fields, 'ignore_imp = 2') as cursor:
                    row = None
                    for row in EBARUtils.searchCursor(cursor):
                        # build list of values from source
                        values = []
                        for key in field_dict:
                            # exclude fields that were used for preprocessing
                            if key not in ['scientific_name', 'S_RANK', 'ROUNDED_S_RANK', 'EST_DATA_SENS',
                                           'EST_DATASEN_CAT', 'min_date', 'max_date']:
                                if field_dict[key]:
                                    values.append(row[field_dict[key]])
                        # use most keys from dict to automate
                        dst_fields = []
                        for key in field_dict:
                            # exclude fields that were used for preprocessing
                            if key not in ['scientific_name', 'S_RANK', 'ROUNDED_S_RANK', 'EST_DATA_SENS',
                                           'EST_DATASEN_CAT', 'min_date', 'max_date']:
                                if field_dict[key]:
                                    dst_fields.append(key)
                        # retrieve and update duplicate destination row
                        with arcpy.da.UpdateCursor(destination, dst_fields, "DatasetSourceUniqueID = '" +
                                                   str(int(row[field_dict['DatasetSourceUniqueID']])) +
                                                   "' AND InputDatasetID IN " +
                                                   input_dataset_ids) as update_cursor:
                            update_row = None
                            for update_row in EBARUtils.updateCursor(update_cursor):
                                update_cursor.updateRow(values)
                            if update_row:
                                del update_row
                    if row:
                        del row

        # temp clean-up
        # trouble deleting on server only due to locks; could be layer?
        if param_geodatabase[-4:].lower() == '.gdb':
            if arcpy.Exists(temp_import_features):
                arcpy.Delete_management(temp_import_features)

        # summary and end time
        EBARUtils.displayMessage(messages, 'Summary:')
        EBARUtils.displayMessage(messages, 'Processed - ' + str(overall_count))
        EBARUtils.displayMessage(messages, 'Added - ' + str(added))
        EBARUtils.displayMessage(messages, 'Duplicates updated - ' + str(duplicates))
        EBARUtils.displayMessage(messages, 'Species not matched - ' + str(no_species_match))
        EBARUtils.displayMessage(messages, 'No coordinates - ' + str(no_coords))
        EBARUtils.displayMessage(messages,
                                 'Accuracy worse than ' + str(EBARUtils.worst_accuracy) + ' m - ' + str(inaccurate))
        if field_dict['max_date']:
            EBARUtils.displayMessage(messages, 'Imported without date - ' + str(bad_date))
        else:
            EBARUtils.displayMessage(messages, 'Imported without date - ' + str(overall_count - no_species_match - 
                                                                                no_coords - inaccurate))
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
    param_import_feature_class.value = 'C:/GIS/EBAR/CDN_CDC_Data/Yukon/Yukon_nonsensitive_data.gdb/YT_nonsensitive_SF_line'
    param_dataset_name = arcpy.Parameter()
    param_dataset_name.value = 'Yukon Non-sensitive SF Lines'
    param_dataset_source = arcpy.Parameter()
    param_dataset_source.value = 'YT Source Feature Lines'
    param_date_received = arcpy.Parameter()
    param_date_received.value = 'April 2, 2021'
    param_restrictions = arcpy.Parameter()
    param_restrictions.value = 'Non-restricted'
    parameters = [param_geodatabase, param_import_feature_class, param_dataset_name, param_dataset_source,
                  param_date_received, param_restrictions]
    isd.runImportSpatialDataTool(parameters, None)
