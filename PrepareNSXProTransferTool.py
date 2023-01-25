# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Samantha Stefanoff
# © NatureServe Canada 2023 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: PrepareNSXProTransferTool.py
# ArcGIS Python tool for setting InputPoint/Polygon fields used by the NSXProTransfer service
# Restricted records

# Notes:
# - Relies on views in server geodatabase, so not possible to use/debug with local file gdb

# import Python packages
import EBARUtils
import arcpy
import datetime


class PrepareNSXProTransferTool:
    """Set InputPoint/Polygon fields used by the NSXProTransfer service"""
    def __init__(self):
        pass

    def runPrepareNSXProTransferTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        param_geodatabase = parameters[0].valueAsText

        # process points and polygons
        EBARUtils.displayMessage(messages, 'Processing points')
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/x_InputPoint', 'points')

        EBARUtils.displayMessage(messages, 'Processing polygons')
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/x_InputPolygon', 'polygons')


# controlling process
if __name__ == '__main__':
    pnpt = PrepareNSXProTransferTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:/GIS/EBAR/EBAR-KBA-Dev.gdb'
    parameters = [param_geodatabase]
    pnpt.runPrepareNSXProTransferTool(parameters, None)
