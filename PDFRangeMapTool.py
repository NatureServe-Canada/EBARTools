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
#import locale
import EBARUtils
import arcpy
import datetime
import pdfkit


# controlling process
if __name__ == '__main__':
    #range_map_id = 10
    #aprx = arcpy.mp.ArcGISProject('C:/GIS/EBAR/EBAR.aprx')
    #map = aprx.listMaps('Range Map Landscape Topographic')[0]
    #polygon_layer = map.listLayers('EcoshapeRangeMap')[0]
    #polygon_layer.definitionQuery = 'rangemapid = ' + str(range_map_id)
    #table_layer = map.listTables('RangeMap')[0]
    #table_layer.definitionQuery = 'rangemapid = ' + str(range_map_id)
    #layout = aprx.listLayouts('Range Map Landscape Topographic')[0]
    #map_frame = layout.listElements('MAPFRAME_ELEMENT')[0]
    #extent = map_frame.getLayerExtent(polygon_layer, False, True)
    #x_buffer = (extent.XMax - extent.XMin) / 20.0
    #y_buffer = (extent.YMax - extent.YMin) / 20.0
    #buffered_extent = arcpy.Extent(extent.XMin - x_buffer,
    #                               extent.YMin - y_buffer,
    #                               extent.XMax + x_buffer,
    #                               extent.YMax + y_buffer)
    #map_frame.camera.setExtent(buffered_extent)
    #layout.exportToPDF('C:/GIS/EBAR/Test' + str(range_map_id) + '.pdf')

    pdf_options = {
        'quiet': '',
        'page-size': 'Letter',
        'margin-top': '1.5in',
        'margin-right': '1.5in',
        'margin-bottom': '1.5in',
        'margin-left': '1.5in',
        'encoding': "UTF-8",
        'custom-header' : [
            ('Accept-Encoding', 'gzip')
        ],
        'cookie': [
            ('cookie-name1', 'cookie-value1'),
            ('cookie-name2', 'cookie-value2'),
        ],
        'no-outline': None
    }
    pdfkit.from_string('Hello world!', 'C:/GIS/EBAR/TestMetadata.pdf') #, pdf_options)
