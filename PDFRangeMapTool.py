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
import requests
import json


# controlling process
if __name__ == '__main__':
    # export map to jpg
    range_map_id = 199
    output_root_name = 'C:/GIS/EBAR/EBARMap'
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
    #layout.exportToJPEG(output_root_name + str(range_map_id) + '.jpg', 300, clip_to_elements=True)
    ##layout.exportToPDF(output_root_name + str(range_map_id) + '.pdf')

    # get attributes from database
    param_geodatabase = 'https://gis.natureserve.ca/arcgis/rest/services/EBAR-KBA/EBAR/FeatureServer'
    species_id = None
    with arcpy.da.SearchCursor(param_geodatabase + '/11', ['SpeciesID'],
                               'RangeMapID = ' + str(range_map_id)) as cursor:
        for row in EBARUtils.searchCursor(cursor):
            species_id = row['SpeciesID']
        del row
    national_engl_name = None
    element_code = None
    with arcpy.da.SearchCursor(param_geodatabase + '/4', ['NATIONAL_ENGL_NAME', 'ELEMENT_CODE'],
                               'SpeciesID = ' + str(species_id)) as cursor:
        for row in EBARUtils.searchCursor(cursor):
            national_engl_name = row['NATIONAL_ENGL_NAME']
            element_code = row['ELEMENT_CODE']
        del row
    kba_trigger = None
    with arcpy.da.SearchCursor(param_geodatabase + '/19', ['KBATrigger'],
                               'SpeciesID = ' + str(species_id)) as cursor:
        for row in EBARUtils.searchCursor(cursor):
            kba_trigger = row['KBATrigger']
        del row

    # get attributes from NSE
    rounded_nrank = None
    url = 'https://explorer.natureserve.org/api/data/search'
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json; charset=UTF-8'}
    params = {'criteriaType': 'combined',
              'textCriteria': [{'paramType': 'textSearch',
                                'searchToken': element_code,
                                'matchAgainst': 'code',
                                'operator': 'equals'}]}
    payload = json.dumps(params)
    r = requests.post(url, data=payload, headers=headers)
    content = json.loads(r.content)
    results = content['results']
    for k in results[0]:
        if k == 'nations':
            for knation in results[0][k]:
                if knation['nationCode'] == 'CA':
                    rounded_nrank = knation['roundedNRank']

    # build html
    body = '''
    <html>
      <head>
        <meta name="pdfkit-orientation" content="Landscape"/>
      </head>
      <img src="''' + output_root_name + str(range_map_id) + '.jpg' + '''" width="1500">
      <br>
      <header>
        <h1>From Biotics Table</h1>
        <h2>National English Name: ''' + national_engl_name + '''</h2>
      </header>
      <header>
        <h1>From Species Table</h1>
        <h2>KBA Trigger: ''' + kba_trigger + '''</h2>
      </header>
      <header>
        <h1>From NSE Taxon API</h1>
        <h2>Rounded NRank: ''' + rounded_nrank + '''</h2>
      </header>
      <header>
        <h1>Hard-coded Text</h1>
        <h2>Boilerplate text, such as methods info...</h2>
      </header>
    </html>
    '''

    # send to pdf
    pdf_options = {
        'quiet': '',
        'page-size': 'Letter',
        'margin-top': '0.5in',
        'margin-right': '0.65in',
        'margin-bottom': '0.5in',
        'margin-left': '0.65in',
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
    pdfkit.from_string(body, output_root_name + str(range_map_id) + '.pdf', pdf_options)
