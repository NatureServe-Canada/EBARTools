# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2020 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: ExportInputDataTool.py
# ArcGIS Python tool for exporting InputPoint/Line/Polygon records

# Notes:
# - Relies on views in server geodatabase, so not possible to use/debug with local file gdb

# import Python packages
import EBARUtils
import arcpy
import datetime
import shutil


class ExportInputDataTool:
    """Export InputPoint/Line/Polygon records"""
    def __init__(self):
        pass

    def runExportInputDataTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        param_geodatabase = parameters[0].valueAsText
        param_jurisdictions_covered = parameters[1].valueAsText
        # convert to Python list
        param_jurisdictions_list = []
        param_jurisdictions_list = param_jurisdictions_covered.replace("'", '')
        param_jurisdictions_list = param_jurisdictions_list.split(';')
        jur_ids_comma = EBARUtils.buildJurisdictionList(param_geodatabase, param_jurisdictions_list)
        param_include_cdc = parameters[2].valueAsText
        param_include_restricted = parameters[3].valueAsText
        param_output_zip = parameters[4].valueAsText
        if param_output_zip[-4:] != '.zip':
            param_output_zip += '.zip'

        # check for existing output
        if arcpy.Exists(EBARUtils.download_folder + '/' + param_output_zip):
            EBARUtils.displayMessage(messages,
                                     'ERROR: output file already exists')
            # terminate with error
            return
            #raise arcpy.ExecuteError

        # create output_gdb
        output_gdb = 'EBARExport' + str(start_time.year) + str(start_time.month) + str(start_time.day) + \
            str(start_time.hour) + str(start_time.minute) + str(start_time.second) + '.gdb'
        arcpy.CreateFileGDB_management(EBARUtils.temp_folder, output_gdb)
        output_gdb = EBARUtils.temp_folder + '/' + output_gdb

        # select jurisdiction(s)
        EBARUtils.displayMessage(messages, 'Selecting jurisdiction(s)')
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/JurisdictionBufferFull', 'jurs')
        arcpy.SelectLayerByAttribute_management('jurs', 'NEW_SELECTION', 'JurisdictionID IN ' + jur_ids_comma)

        # generate metadata
        EBARUtils.displayMessage(messages, 'Generating metadata')
        md = arcpy.metadata.Metadata()
        md.tags = 'Species Data, NatureServe Canada'
        md.description = 'Export of Species data from EBAR-KBA database. ' + \
            'Please see EBARExportReadme.txt for field descriptions.'
        md.credits = 'Please credit original providers as per DatasetSourceCitation field.'
        if param_include_restricted  == 'true' or param_include_cdc == 'true':
            md.accessConstraints = 'Some data has restrictions. ' + \
                'Please check with EBAR-KBA@natureserve.ca before sharing.'
        else:
            md.accessConstraints = 'Please credit original providers as per DatasetSourceCitation field.'

        # process points, lines and polygons separately
        EBARUtils.displayMessage(messages, 'Processing points')
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/x_InputPoint', 'points')
        self.processFeatureClass('points', 'jurs', param_include_cdc, param_include_restricted,
                                 output_gdb + '/EBARPoints', md)
        EBARUtils.displayMessage(messages, 'Processing lines')
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/x_InputLine', 'lines')
        self.processFeatureClass('lines', 'jurs', param_include_cdc, param_include_restricted,
                                 output_gdb + '/EBARLines', md)
        EBARUtils.displayMessage(messages, 'Processing polygons')
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/x_InputPolygon', 'polygons')
        self.processFeatureClass('polygons', 'jurs', param_include_cdc, param_include_restricted,
                                 output_gdb + '/EBARPolygons', md)

        # zip gdb into single file for download
        EBARUtils.displayMessage(messages, 'Zipping output')
        EBARUtils.createZip(output_gdb, EBARUtils.download_folder + '/' + param_output_zip, None)
        EBARUtils.addToZip(EBARUtils.download_folder + '/' + param_output_zip,
                           EBARUtils.resources_folder + '/EBARExportReadme.txt')

        # download message
        EBARUtils.displayMessage(messages,
                                 'Please download output from https://gis.natureserve.ca/download/' + param_output_zip)

    def processFeatureClass(self, fclyr, jurs, include_cdc, include_restricted, output_fc, md):
        # select features using non-spatial criteria
        where_clause = None
        if include_cdc == 'false':
            where_clause = 'CDCJurisdictionID IS NULL'
        if include_restricted == 'false':
            if not where_clause:
               where_clause = ''
               where_clause += " Restrictions != 'R'"
        arcpy.SelectLayerByAttribute_management(fclyr, 'NEW_SELECTION', where_clause)
        # sub-select features using spatial criteria
        arcpy.SelectLayerByLocation_management(fclyr, 'INTERSECT', jurs, selection_type='SUBSET_SELECTION')
        # export features
        arcpy.CopyFeatures_management(fclyr, output_fc)
        # embed metadata
        fc_md = arcpy.metadata.Metadata(output_fc)
        fc_md.copy(md)
        fc_md.save()
