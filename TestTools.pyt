# import python packages
#import AddSynonymsTool
import arcpy
#import BuildBulkDownloadTableTool
import BuildEBARDownloadTableTool
#import collections
#import csv
import datetime
#import DeleteRangeMapTool
import EBARUtils
#import ExportInputDataTool
#import FlagBadDataUsingRangeTool
#import GenerateRangeMapTool
#import ImportExternalRangeReviewTool
#import ImportSpatialDataTool
#import ImportTabularDataTool
#import ImportVisitsTool
#import io
#import json
#import ListElementNationalIDsTool
#import locale
#import math
#import os
#import pathlib
#import pdfkit
import PublishRangeMapSetsTool
import PublishRangeMapTool
#import requests
#import shutil
#import SummarizeDownloadsTool
#import SyncSpeciesListBioticsTool
#import SyncSpeciesListKBATool
#import sys
#import TabularFieldMapping
#import time
#import traceback
#import urllib
#import zipfile


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = 'Test Tools'
        self.alias = ''

        # List of tool classes associated with this toolbox
        self.tools = [TestTool]


class TestTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Test Tool'
        self.description = 'Test'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        return None

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is 
        called whenever a parameter has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called "
        "after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        arcpy.AddMessage('TEST0')
        ## start time
        #start_time = datetime.datetime.now()
        #EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        ## settings
        #output_file = EBARUtils.download_folder + '/EBARDownloadTables.html'

        ## html header
        #html = '<!doctype html>'
        ## loop all RangeMap records where IncludeInDownloadTable is populated
        #arcpy.MakeTableView_management(EBARUtils.ebar_feature_service + '/11', 'range_map_view',
        #                               'IncludeInDownloadTable IN (1, 2, 3, 4) AND Publish = 1')
        ## join BIOTICS_ELEMENT_NATIONAL to RangeMap
        #arcpy.AddJoin_management('range_map_view', 'SpeciesID', EBARUtils.ebar_feature_service + '/4', 'SpeciesID',
        #                         'KEEP_COMMON')
        #category_taxa = ''
        ## use Python sorted (sql_clause ORDER BY doesn't work), which precludes use of EBARUtils.SearchCursor
        #for row in sorted(arcpy.da.SearchCursor('range_map_view',
        #                  ['L4BIOTICS_ELEMENT_NATIONAL.CATEGORY',
        #                   'L4BIOTICS_ELEMENT_NATIONAL.TAX_GROUP',
        #                   'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_SCIENTIFIC_NAME',
        #                   'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_ENGL_NAME',
        #                   'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_FR_NAME',
        #                   'L4BIOTICS_ELEMENT_NATIONAL.ELEMENT_GLOBAL_ID',
        #                   'L11RangeMap.RangeMapScope',
        #                   'L11RangeMap.IncludeInDownloadTable'])):
        #    if row[0] + ' - ' + row[1] != category_taxa:
        #        if category_taxa != '':
        #            # table footer for previous table
        #            html += '</tbody></table>'
        #        # table header
        #        category_taxa = row[0] + ' - ' + row[1]
        #        EBARUtils.displayMessage(messages, category_taxa + ' table')
        #        html += '<h2>' + category_taxa + '</h2><table><tbody><tr><th>Scientific Name</th><th>English Name</th><th>Nom Francais</th><th>Scope</th><th>Status</th><th>PDF Link</th><th>GIS Data Link</th></tr>'
        #    # table row
        #    french_name = ''
        #    if row[4]:
        #        french_name = row[4]
        #    scope = 'Global'
        #    if row[6] == 'N':
        #        scope = 'Canadian'
        #    if row[6] == 'A':
        #        scope = 'North American'
        #    element_global_id = str(row[5])
        #    if scope == 'Canadian':
        #        element_global_id += 'N'
        #    status = 'Expert Reviewed'
        #    if row[7] == 2:
        #        status = 'Insufficient Data'
        #    if row[7] == 3:
        #        status = 'Partially Reviewed'
        #    if row[7] == 4:
        #        status = 'Low Star Rating'
        #    html += '<tr><td>' + row[2] + '</td><td>' + row[3] + '</td><td>' + french_name + '</td><td>' + scope + '</td><td>' + status + '</td><td><a href="https://gis.natureserve.ca/download/EBAR' + element_global_id + '.pdf" target="_blank">View PDF</a></td>'
        #    if row[7] == 1:
        #        html += '<td><a href="https://gis.natureserve.ca/download/EBAR' + element_global_id + '.zip" target="_blank">Download GIS Data</a></td>'
        #    else:
        #        html += '<td></td>'
        #    html += '</tr>'
        #    EBARUtils.displayMessage(messages, element_global_id)
        ## table footer for final table
        #html += '</tbody></table></body>'
                
        ## save
        #EBARUtils.displayMessage(messages, 'Saving file')
        #file = open(output_file, 'w')
        #file.write(html)
        #file.close()
