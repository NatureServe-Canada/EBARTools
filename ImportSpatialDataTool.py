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
            param_dataset_type = parameters[6].valueAsText
            param_date_received = parameters[7].valueAsText
            param_restrictions = parameters[8].valueAsText
        else:
            # for debugging, hard code parameters
            param_geodatabase = 'C:/GIS/EBAR/EBAR_outputs.gdb'

            #param_import_feature_class = 'C:/GIS/EBAR/CriticalHabitat/' + \
            #    'Critical Habitat for Species at Risk - National View.gdb/CriticalHabitatNationalView'
            #param_dataset_name = 'ECCC Critical Habitat National View'
            #param_dataset_organization = 'Environment and Climate Change Canada'
            #param_dataset_contact = \
            #    'http://data.ec.gc.ca/data/species/protectrestore/critical-habitat-species-at-risk-canada/'
            #param_dataset_source = 'ECCC Critical Habitat'
            #param_dataset_type = 'Critical Habitat'
            #param_date_received = 'October 18, 2019'
            #param_restrictions = None

            #param_import_feature_class = 'C:/GIS/EBAR/NCC/Endemics_Data_EBAR.gdb/Literature_20190813'
            #param_dataset_name = 'NCC Endemics Literature'
            #param_dataset_organization = 'Nature Conservancy of Canada'
            #param_dataset_contact = 'Andrea Hebb'
            #param_dataset_source = 'NCC Endemics Polygons'
            #param_dataset_type = 'Species Observation Polygons'
            #param_date_received = 'October 15, 2019'
            #param_restrictions = None

            #param_import_feature_class = 'C:/GIS/EBAR/CDN_CDC_Data/Yukon/EO_data_Yukon.shp'
            #param_dataset_name = 'Yukon EOs'
            #param_dataset_organization = 'Yukon CDC'
            #param_dataset_contact = 'Maria Leung'
            #param_dataset_source = 'YT CDC Element Occurrences'
            #param_dataset_type = 'Element Occurrences'
            #param_date_received = 'October 31, 2019'
            #param_restrictions = None

            param_import_feature_class = 'C:/GIS/EBAR/CDN_CDC_Data/Yukon/SF_polygon_Yukon.shp'
            param_dataset_name = 'Yukon SFs'
            param_dataset_organization = 'Yukon CDC'
            param_dataset_contact = 'Maria Leung'
            param_dataset_source = 'CDC Source Feature Polygons'
            param_dataset_type = 'Source Feature Polygons'
            param_date_received = 'October 30, 2019'
            param_restrictions = None

        # use passed geodatabase as workspace (still seems to go to default geodatabase)
        arcpy.env.workspace = param_geodatabase

        # check parameters
        # match field_dict with source
        if param_dataset_source in ['NU CDC Element Occurrences',
                                    'YT CDC Element Occurrences']:
            field_dict = SpatialFieldMapping.cdc_eo_fields
        elif param_dataset_source == 'CDC Source Feature Polygons':
            field_dict = SpatialFieldMapping.cdc_sf_fields
        elif param_dataset_source == 'CDC Source Feature Points':
            field_dict = SpatialFieldMapping.cdc_sf_fields
        elif param_dataset_source == 'CDC Source Feature Lines':
            field_dict = SpatialFieldMapping.cdc_sf_fields
        elif param_dataset_source == 'ECCC Critical Habitat':
            field_dict = SpatialFieldMapping.eccc_critical_habitat_fields
        elif param_dataset_source == 'NCC Endemics Polygons':
            field_dict = SpatialFieldMapping.ncc_endemics_polygons_fields
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
                                                                          param_dataset_source,
                                                                          param_dataset_type,
                                                                          param_date_received,
                                                                          param_restrictions)
        if not dataset_exists:
            EBARUtils.setNewID(param_geodatabase + '/InputDataset', 'InputDatasetID', 'OBJECTID = ' + \
                               str(input_dataset_id))

        # read existing species into dict
        EBARUtils.displayMessage(messages, 'Reading existing species')
        species_dict = EBARUtils.readSpecies(param_geodatabase)

        # read existing unique IDs into dict
        EBARUtils.displayMessage(messages, 'Reading existing unique IDs')
        id_dict = EBARUtils.readDatasetSourceUniqueIDs(param_geodatabase, param_dataset_source, feature_class_type)

        # pre-processing
        EBARUtils.displayMessage(messages, 'Pre-processing features')
        arcpy.MakeFeatureLayer_management(param_import_feature_class, 'import_features')
        EBARUtils.checkAddField('import_features', 'SpeciesID', 'LONG')
        EBARUtils.checkAddField('import_features', 'dup', 'SHORT')
        if feature_class_type in ('Polygon', 'MultiPatch'):
            # EOs can only be polygons
            EBARUtils.checkAddField('import_features', 'eo_rank', 'TEXT')

        # loop to check/add species and flag duplicates
        count = 0
        duplicates = 0
        with arcpy.da.UpdateCursor('import_features',
                                   [field_dict['unique_id'], field_dict['scientific_name'],
                                    'SpeciesID', 'dup']) as cursor:
            for row in EBARUtils.updateCursor(cursor):
                count += 1
                if count % 1000 == 0:
                    EBARUtils.displayMessage(messages, 'Step 1 pre-processed ' + str(count))
                # check/add species
                species_id, exists = EBARUtils.checkAddSpecies(species_dict, param_geodatabase,
                                                               row[field_dict['scientific_name']])
                # check for duplicates
                dup = 0
                # handle case where integer gets read as float with decimals
                uid_raw = row[field_dict['unique_id']]
                if isinstance(uid_raw, float):
                    uid_raw = int(uid_raw)
                if str(uid_raw) in id_dict:
                    duplicates += 1
                    dup = 1
                # save
                cursor.updateRow([row[field_dict['unique_id']], row[field_dict['scientific_name']], species_id, dup])
            if count > 0:
                del row

        # loop to set eo rank
        if field_dict['eo_rank'] and feature_class_type in ('Polygon', 'MultiPatch'):
            count = 0
            with arcpy.da.UpdateCursor('import_features', [field_dict['eo_rank'], 'eo_rank']) as cursor:
                for row in EBARUtils.updateCursor(cursor):
                    count += 1
                    if count % 1000 == 0:
                        EBARUtils.displayMessage(messages, 'Step 2 pre-processed ' + str(count))
                    # encode eo rank if full description provided
                    eo_rank = row[field_dict['eo_rank']]
                    if len(eo_rank) > 2:
                        eo_rank = EBARUtils.eo_rank_dict[eo_rank]
                    # save
                    cursor.updateRow([row[field_dict['eo_rank']], eo_rank])
                if count > 0:
                    del row

        # select non-dups
        arcpy.SelectLayerByAttribute_management('import_features', where_clause='dup = 0')

        # pre-process date
        if field_dict['date']:
            EBARUtils.checkAddField('import_features', 'MaxDate', 'DATE')
            with arcpy.da.UpdateCursor('import_features', [field_dict['date'], 'MaxDate']) as cursor:
                for row in EBARUtils.updateCursor(cursor):
                    max_date = None
                    if field_dict['date']:
                        # could be yyyy-mm-dd, yyyy-mm or yyyy
                        date_str = row[field_dict['date']].strip()
                        if date_str not in ('NA', '', None):
                            year = int(date_str[0:4])
                            month = 1
                            if len(date_str) >= 7:
                                month = int(date_str[5:7])
                            day = 1
                            if len(date_str) == 10:
                                day = int(date_str[8:10])
                            max_date = datetime.datetime(year, month, day)
                    cursor.updateRow([row[field_dict['date']], max_date])
                if count - duplicates > 0:
                    del row

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
        field_mappings.addFieldMap(EBARUtils.createFieldMap('import_features', field_dict['unique_id'],
                                                            'DatasetSourceUniqueID', 'TEXT'))
        if field_dict['uri']:
            field_mappings.addFieldMap(EBARUtils.createFieldMap('import_features', field_dict['uri'],
                                                                'URI', 'TEXT'))
        if field_dict['date']:
            field_mappings.addFieldMap(EBARUtils.createFieldMap('import_features', 'MaxDate',
                                                                'MaxDate', 'DATE'))
        if field_dict['eo_rank'] and feature_class_type in ('Polygon', 'MultiPatch'):
            field_mappings.addFieldMap(EBARUtils.createFieldMap('import_features', 'eo_rank',
                                                                'EORank', 'DATE'))
        # append
        if count - duplicates > 0:
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
        EBARUtils.displayMessage(messages, 'Processed - ' + str(count))
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
