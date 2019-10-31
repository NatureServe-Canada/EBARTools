# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: ImportPolygonsTool.py
# ArcGIS Python tool for importing polygon data into the
# InputDataset and InputPolygon tables of the EBAR geodatabase

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
import PolygonsFieldMapping


class ImportPolygonsTool:
    """Import point data into the InputDataset and InputPoint tables of the EBAR geodatabase"""
    def __init__(self):
        pass

    def RunImportPolygonsTool(self, parameters, messages):
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

            param_import_feature_class = 'C:/GIS/EBAR/CDN_CDC_Data/Yukon/EO_data_Yukon.shp'
            param_dataset_name = 'Yukon EOs'
            param_dataset_organization = 'Yukon CDC'
            param_dataset_contact = 'Maria Leung'
            param_dataset_source = 'YT CDC Element Occurrences'
            param_dataset_type = 'Element Occurrences'
            param_date_received = 'October 31, 2019'
            param_restrictions = None

        # use passed geodatabase as workspace
        arcpy.env.workspace = param_geodatabase

        # check parameters
        if param_dataset_source == 'YT CDC Element Occurrences':
            field_dict = PolygonsFieldMapping.cdc_eos_fields
        elif param_dataset_source == 'ECCC Critical Habitat':
            field_dict = PolygonsFieldMapping.eccc_critical_habitat_fields
        elif param_dataset_source == 'NCC Endemics Polygons':
            field_dict = PolygonsFieldMapping.ncc_endemics_polygons_fields

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
        id_dict = EBARUtils.readDatasetSourceUniquePolygonIDs(param_geodatabase, param_dataset_source)

        # pre-processing
        EBARUtils.displayMessage(messages, 'Pre-processing polygons')
        arcpy.MakeFeatureLayer_management(param_import_feature_class, 'import_polygons')
        EBARUtils.checkAddField('import_polygons', 'SpeciesID', 'LONG')
        EBARUtils.checkAddField('import_polygons', 'dup', 'SHORT')

        # loop to check/add species and flag duplicates
        count = 0
        duplicates = 0
        with arcpy.da.UpdateCursor('import_polygons', [field_dict['unique_id'], field_dict['scientific_name'],
                                                       'SpeciesID', 'dup']) as cursor:
            for row in EBARUtils.updateCursor(cursor):
                count += 1
                if count % 1000 == 0:
                    EBARUtils.displayMessage(messages, 'Pre-processed ' + str(count))
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

        # select non-dups
        arcpy.SelectLayerByAttribute_management('import_polygons', where_clause='dup = 0')

        # pre-process date
        if field_dict['date']:
            EBARUtils.checkAddField('import_polygons', 'MaxDate', 'DATE')
            with arcpy.da.UpdateCursor('import_polygons', [field_dict['date'], 'MaxDate']) as cursor:
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
        EBARUtils.checkAddField('import_polygons', 'InDSID', 'LONG')
        arcpy.CalculateField_management('import_polygons', 'InDSID', input_dataset_id)

        # append to InputPolygons
        EBARUtils.displayMessage(messages, 'Appending polygons')
        field_mappings = arcpy.FieldMappings()
        # InputDatasetID mapping
        field_mappings.addFieldMap(EBARUtils.createFieldMap('import_polygons', 'InDSID',
                                                            'InputDatasetID', 'LONG'))
        #field_map = arcpy.FieldMap()
        #field_map.addInputField('import_polygons', 'InputDatasetID')
        #input_dataset_id_field = field_map.outputField
        #input_dataset_id_field.name = 'InputDatasetID'
        #input_dataset_id_field.aliasName = 'InputDatasetID'
        #input_dataset_id_field.type = 'LONG'
        #field_map.outputField = input_dataset_id_field
        #field_mappings.addFieldMap(field_map)
        # SpeciesID mapping
        field_mappings.addFieldMap(EBARUtils.createFieldMap('import_polygons', 'SpeciesID',
                                                            'SpeciesID', 'LONG'))
        # DatasetSourceUniqueID mapping
        field_mappings.addFieldMap(EBARUtils.createFieldMap('import_polygons', field_dict['unique_id'],
                                                            'DatasetSourceUniqueID', 'TEXT'))
        # URI mapping
        if field_dict['uri']:
            field_mappings.addFieldMap(EBARUtils.createFieldMap('import_polygons', field_dict['uri'],
                                                                'URI', 'TEXT'))
        # Date
        if field_dict['date']:
            field_mappings.addFieldMap(EBARUtils.createFieldMap('import_polygons', 'MaxDate',
                                                                'MaxDate', 'DATE'))
        # append
        if count - duplicates > 0:
            arcpy.Append_management('import_polygons', param_geodatabase + '/InputPolygon', 'NO_TEST', field_mappings)
            # set new id (will reset any previous IDs from same input dataset)
            EBARUtils.setNewID(param_geodatabase + '/InputPolygon', 'InputPolygonID',
                               'InputDatasetID = ' + str(input_dataset_id))

        # summary and end time
        EBARUtils.displayMessage(messages, 'Summary:')
        EBARUtils.displayMessage(messages, 'Processed ' + str(count))
        EBARUtils.displayMessage(messages, 'Duplicates ' + str(duplicates))
        end_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'End time: ' + str(end_time))
        elapsed_time = end_time - start_time
        EBARUtils.displayMessage(messages, 'Elapsed time: ' + str(elapsed_time))

        return


# controlling process
if __name__ == '__main__':
    ipt = ImportPolygonsTool()
    # hard code parameters for debugging
    ipt.RunImportPolygonsTool(None, None)
