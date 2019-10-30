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

            param_import_feature_class = 'C:/Users/rgree/OneDrive/Data_Mining/Import_Routine_Data/gbif_test.csv'
            param_dataset_name = 'ECCC Critical Habitat'
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
        id_dict = EBARUtils.readDatasetSourceUniquePolygonsIDs(param_geodatabase, param_dataset_source)

        # add column for species id
        arcpy.MakeFeatureLayer_management(param_import_feature_class, 'import_polygons')
        EBARUtils.checkAddField('import_polygons', 'SpeciesID', 'LONG')

        # select all rows then loop to remove duplicates and set Species ID
        count = 0
        duplicates = 0
        arcpy.SelectLayerByAttribute_management('import_polygons')
        with arcpy.da.UpdateCursor('import_polygons', ['identifier', 'SciName']) as cursor:
            for row in EBARUtils.updateCursor(cursor):
                count += 1
                if row['identifier'] in id_dict:
                    duplicates += 1
                    arcpy.SelectLayerByAttribute_management('import_polygons', 'REMOVE_FROM_SELECTION', )
                else:
                    species_id, exists = EBARUtils.checkAddSpecies(species_dict, param_geodatabase, row['SciName'])
                    cursor.updateRow([row['identifier'], species_id])
            if count > 0:
                del row

        # add and set column for input dataset
        EBARUtils.checkAddField('import_polygons', 'InputDatasetID', 'LONG')
        arcpy.CalculateField_management('import_polygons', 'InputDatasetID', input_dataset_id)

        return


# controlling process
if __name__ == '__main__':
    ipt = ImportPolygonsTool()
    # hard code parameters for debugging
    ipt.RunImportPolygonsTool(None, None)
