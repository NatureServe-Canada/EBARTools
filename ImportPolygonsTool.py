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
import sys
import traceback
import arcpy
import io
import csv
import datetime
#import locale
import EBARUtils
import PointsFieldMapping


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

            param_import_feature_class = 'C:/GIS/EBAR/CriticalHabitat/Critical Habitat for Species at Risk - National View.gdb/' + \
                'CriticalHabitatNationalView'
            param_dataset_name = 'ECCC Critical Habitat National View'
            param_dataset_organization = 'Environment and Climate Change Canada'
            param_dataset_contact = 'http://data.ec.gc.ca/data/species/protectrestore/critical-habitat-species-at-risk-canada/'
            param_dataset_source = 'ECCC Critical Habitat'
            param_dataset_type = 'Critical Habitat'
            param_date_received = 'October 18, 2019'
            param_restrictions = None

        # use passed geodatabase as workspace
        arcpy.env.workspace = param_geodatabase

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
        EBARUtils.setNewID(param_geodatabase + '/InputDataset', 'InputDatasetID', 'OBJECTID = ' + \
                           str(input_dataset_id))

        # read existing species into dict
        EBARUtils.displayMessage(messages, 'Reading existing species')
        species_dict = EBARUtils.readSpecies(param_geodatabase)

        # read existing unique IDs into dict
        EBARUtils.displayMessage(messages, 'Reading existing unique IDs')
        id_dict = EBARUtils.readDatasetSourceUniquePolygonIDs(param_geodatabase, param_dataset_source)

        # add columns for species id and dup flag
        arcpy.MakeFeatureLayer_management(param_import_feature_class, 'import_polygons')
        EBARUtils.checkAddField('import_polygons', 'SpeciesID', 'LONG')
        EBARUtils.checkAddField('import_polygons', 'dup', 'SHORT')

        # loop to flag duplicates and set Species ID
        EBARUtils.displayMessage(messages, 'Pre-processing polygons')
        count = 0
        duplicates = 0
        with arcpy.da.UpdateCursor('import_polygons', ['Identifier', 'SciName', 'SpeciesID', 'dup']) as cursor:
            for row in EBARUtils.updateCursor(cursor):
                count += 1
                if count % 1000 == 0:
                    EBARUtils.displayMessage(messages, 'Pre-processed ' + str(count))
                dup = 0
                if row['Identifier'] in id_dict:
                    duplicates += 1
                    dup = 1
                    cursor.updateRow([row['Identifier'], row['SciName'], None, dup])
                else:
                    species_id, exists = EBARUtils.checkAddSpecies(species_dict, param_geodatabase, row['SciName'])
                    cursor.updateRow([row['Identifier'], row['SciName'], species_id, dup])
            if count > 0:
                del row

        # select non-dups
        arcpy.SelectLayerByAttribute_management('import_polygons', where_clause='dup = 0')

        # add and set column for input dataset
        EBARUtils.checkAddField('import_polygons', 'InputDatasetID', 'LONG')
        arcpy.CalculateField_management('import_polygons', 'InputDatasetID', input_dataset_id)

        # append to InputPolygons
        EBARUtils.displayMessage(messages, 'Appending polygons')
        field_mappings = arcpy.FieldMappings()
        # InputDatasetID mapping
        field_map = arcpy.FieldMap()
        field_map.addInputField('import_polygons', 'InputDatasetID')
        input_dataset_id_field = field_map.outputField
        input_dataset_id_field.name = 'InputDatasetID'
        input_dataset_id_field.aliasName = 'InputDatasetID'
        input_dataset_id_field.type = 'LONG'
        field_map.outputField = input_dataset_id_field
        field_mappings.addFieldMap(field_map)
        # SpeciesID mapping
        field_map = arcpy.FieldMap()
        field_map.addInputField('import_polygons', 'SpeciesID')
        species_id_field = field_map.outputField
        species_id_field.name = 'SpeciesID'
        species_id_field.aliasName = 'SpeciesID'
        species_id_field.type = 'LONG'
        field_map.outputField = species_id_field
        field_mappings.addFieldMap(field_map)
        # DatasetSourceUniqueID mapping
        field_map = arcpy.FieldMap()
        field_map.addInputField('import_polygons', 'Identifier')
        dsuid_field = field_map.outputField
        dsuid_field.name = 'DatasetSourceUniqueID'
        dsuid_field.aliasName = 'DatasetSourceUniqueID'
        dsuid_field.type = 'TEXT'
        field_map.outputField = dsuid_field
        field_mappings.addFieldMap(field_map)
        arcpy.Append_management('import_polygons', param_geodatabase + '/InputPolygon', 'NO_TEST', field_mappings)
        # set new id (will reset any previous IDs from same input dataset)
        EBARUtils.setNewID(param_geodatabase + '/InputPolygon', 'InputPolygonID', 'InputDatasetID = ' + str(input_dataset_id))

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
