# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: GenerateRangeMapTool.py
# ArcGIS Python tool for generating EBAR range maps from spatial data

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
#import sys
import EBARUtils
import arcpy
import datetime


class GenerateRangeMapTool:
    """Generate Range Map for a species from available spatial data in the EBAR geodatabase"""
    def __init__(self):
        pass

    def RunGenerateRangeMapTool(self, parameters, messages):
        # debugging/testing
        #print(locale.getpreferredencoding())
        #return

        # check out any needed extension licenses
        #arcpy.CheckOutExtension('Spatial')

        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        arcpy.gp.overwriteOutput = True
        # buffer size in metres, used if Accuracy not provided
        default_buffer_size = 10
        # proportion of buffer polygon that must be within ecoshape to get Present; other gets Presence Expected
        buffer_percent_overlap = 0.25

        if not messages:
            # for debugging, set workspace location
            arcpy.env.workspace = 'C:/GIS/EBAR/EBAR_outputs.gdb'

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        if parameters:
            # passed from tool user interface
            param_geodatabase = parameters[0].valueAsText
            param_species = parameters[1].valueAsText
            param_version = parameters[2].valueAsText
            param_stage = parameters[3].valueAsText
        else:
            # for debugging, hard code parameters
            param_geodatabase = 'C:/GIS/EBAR/EBAR_outputs.gdb'
            param_species = 'Marmota vancouverensis'
            param_version = '1.0'
            param_stage = 'Auto-generated'

        # check for species
        species_id = None
        with arcpy.da.SearchCursor(param_geodatabase + '/Species', ['SpeciesID'], "ScientificName = '" +
                                   param_species + "'", None) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                species_id = row['SpeciesID']
            if species_id:
                del row
            else:
                EBARUtils.displayMessage(messages, 'ERROR: Species not found')
                return

        # check for range map and add if necessary
        range_map_id = None
        with arcpy.da.SearchCursor(param_geodatabase + '/RangeMap', ['RangeMapID'], "RangeVersion = '" +
                                   param_version + "' AND RangeStage = '" + param_stage + "'") as cursor:
            for row in EBARUtils.searchCursor(cursor):
                range_map_id = row['RangeMapID']
            if range_map_id:
                del row
                EBARUtils.displayMessage(messages, 'WARNING: Range Map already exists; its ecoshapes will be replaced')
        if not range_map_id:
            # add
            fields = ['RangeVersion', 'RangeStage', 'RangeDate']
            with arcpy.da.InsertCursor(param_geodatabase + '/RangeMap', fields) as cursor:
                range_map_id = cursor.insertRow([param_version, param_stage, datetime.datetime.now()])
            EBARUtils.setNewID(param_geodatabase + '/RangeMap', 'RangeMapID', range_map_id)
            EBARUtils.displayMessage(messages, 'Range Map added')

        # select all points for species and buffer
        arcpy.MakeFeatureLayer_management(param_geodatabase + '\InputPoint', 'input_point_layer')
        arcpy.SelectLayerByAttribute_management('input_point_layer', 'NEW_SELECTION', 'SpeciesID = ' + str(species_id))
        EBARUtils.displayMessage(messages, 'Input Points selected')
        EBARUtils.checkAddField('input_point_layer', 'buffer', 'LONG')
        code_block = '''
def GetBuffer(accuracy):
    ret = accuracy
    if not ret:
        ret = ''' + str(default_buffer_size) + '''
    return ret'''
        arcpy.CalculateField_management('input_point_layer', 'buffer', 'GetBuffer(!Accuracy!)', 'PYTHON3', code_block)
        if arcpy.Exists('TempPointBuffer'):
            arcpy.Delete_management('TempPointBuffer')
        arcpy.Buffer_analysis('input_point_layer', 'TempPointBuffer', 'buffer')
        EBARUtils.displayMessage(messages, 'Input Points buffered')

        return
            

# controlling process
if __name__ == '__main__':
    grm = GenerateRangeMapTool()
    # hard code parameters for debugging
    grm.RunGenerateRangeMapTool(None, None)
