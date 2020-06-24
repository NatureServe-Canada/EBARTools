# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2020 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: PublishRangeMapTool.py
# ArcGIS Python tool for creating JPG, PDF and Spatial Data (Zip) for a Range Map

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


class PublishRangeMapTool:
    """Create JPG, PDF and Spatial Data (Zip) for a Range Map"""
    def __init__(self):
        pass

    def RunPublishRangeMapTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True
        arcgis_pro_project = 'C:/GIS/EBAR/EBAR.aprx'
        resources_folder = 'C:/GIS/EBAR/EBARTools/resources'
        temp_folder = 'C:/GIS/EBAR/pub/temp'
        download_folder = 'C:/GIS/EBAR/pub/download'
        ebar_feature_service = 'https://gis.natureserve.ca/arcgis/rest/services/EBAR-KBA/EBAR/FeatureServer'
        nse_taxon_search_url = 'https://explorer.natureserve.org/api/data/search'

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        param_range_map_id = parameters[0].valueAsText
        EBARUtils.displayMessage(messages, 'Range Map ID: ' + param_range_map_id)
        param_pdf = parameters[1].valueAsText
        EBARUtils.displayMessage(messages, 'Include PDF: ' + param_pdf)
        param_jpg = parameters[2].valueAsText
        EBARUtils.displayMessage(messages, 'Include JPG: ' + param_jpg)
        param_spatial = parameters[3].valueAsText
        EBARUtils.displayMessage(messages, 'Include Spatial: ' + param_spatial)

        if param_pdf == 'true' or param_spatial == 'true':
            # replace metadata html tags with real data
            EBARUtils.displayMessage(messages, 'Filling metadata template')
            metadata_body = EBARUtils.metadata_body
            metadata_body = metadata_body.replace('[logo_image]', resources_folder + '/nscanada_inline_copy.png')
            metadata_body = metadata_body.replace('[species_header_image]', resources_folder + '/species_header.png')
            metadata_body = metadata_body.replace('[rank_status_header_image]', resources_folder +
                                                  '/rank_status_header.png')
            metadata_body = metadata_body.replace('[range_map_header_image]', resources_folder +
                                                  '/range_map_header.png')
            metadata_body = metadata_body.replace('[reviews_header_image]', resources_folder + '/reviews_header.png')
            metadata_body = metadata_body.replace('[credits_header_image]', resources_folder + '/credits_header.png')

            # get range map data from database
            species_id = None
            with arcpy.da.SearchCursor(ebar_feature_service + '/11',
                                       ['SpeciesID', 'RangeVersion', 'RangeStage', 'RangeDate', 'RangeMapScope',
                                        'RangeMapNotes', 'RangeMetadata'],
                                       'RangeMapID = ' + str(param_range_map_id)) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    species_id = row['SpeciesID']
                    version = row['RangeVersion'] + ', ' + row['RangeStage'] + ', ' + \
                        EBARUtils.scope_dict[row['RangeMapScope']] + ' scope, ' + \
                        row['RangeDate'].strftime('%B %d, %Y')
                    metadata_body = metadata_body.replace('[RangeMap.RangeVersion]', version)
                    metadata_body = metadata_body.replace('[RangeMap.RangeMapNotes]', row['RangeMapNotes'])
                    metadata_body = metadata_body.replace('[RangeMap.RangeMetadata]', row['RangeMetadata'])
                if species_id:
                    del row
                else:
                    EBARUtils.displayMessage(messages, 'ERROR: Range Map Not Found')
                    # terminate with error
                    return

            # get biotics data from database
            national_engl_name = None
            element_code = None
            with arcpy.da.SearchCursor(ebar_feature_service + '/4', ['NATIONAL_ENGL_NAME', 'ELEMENT_CODE'],
                                       'SpeciesID = ' + str(species_id)) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    national_engl_name = row['NATIONAL_ENGL_NAME']
                    element_code = row['ELEMENT_CODE']
                del row

            # get species data from database
            kba_trigger = None
            with arcpy.da.SearchCursor(ebar_feature_service + '/19', ['KBATrigger'],
                                       'SpeciesID = ' + str(species_id)) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    kba_trigger = row['KBATrigger']
                del row

            # get attributes from NSE
            EBARUtils.displayMessage(messages, 'Getting attributes from NatureServe Explorer')
            rounded_nrank = None
            headers = {'Accept': 'application/json', 'Content-Type': 'application/json; charset=UTF-8'}
            params = {'criteriaType': 'combined',
                      'textCriteria': [{'paramType': 'textSearch',
                                        'searchToken': element_code,
                                        'matchAgainst': 'code',
                                        'operator': 'equals'}]}
            payload = json.dumps(params)
            r = requests.post(nse_taxon_search_url, data=payload, headers=headers)
            content = json.loads(r.content)
            results = content['results']
            for k in results[0]:
                if k == 'nations':
                    for knation in results[0][k]:
                        if knation['nationCode'] == 'CA':
                            rounded_nrank = knation['roundedNRank']

        ## generate jpg
        #if param_pdf == 'true' or param_jpg == 'true':
        #    EBARUtils.displayMessage(messages, 'Generating JPG')
        #    aprx = arcpy.mp.ArcGISProject(arcgis_pro_project)
        #    map = aprx.listMaps('Range Map Landscape Topographic')[0]
        #    polygon_layer = map.listLayers('EcoshapeRangeMap')[0]
        #    polygon_layer.definitionQuery = 'rangemapid = ' + str(param_range_map_id)
        #    table_layer = map.listTables('RangeMap')[0]
        #    table_layer.definitionQuery = 'rangemapid = ' + str(param_range_map_id)
        #    layout = aprx.listLayouts('Range Map Landscape Topographic')[0]
        #    map_frame = layout.listElements('MAPFRAME_ELEMENT')[0]
        #    extent = map_frame.getLayerExtent(polygon_layer, False, True)
        #    x_buffer = (extent.XMax - extent.XMin) / 20.0
        #    y_buffer = (extent.YMax - extent.YMin) / 20.0
        #    buffered_extent = arcpy.Extent(extent.XMin - x_buffer,
        #                                   extent.YMin - y_buffer,
        #                                   extent.XMax + x_buffer,
        #                                   extent.YMax + y_buffer)
        #    map_frame.camera.setExtent(buffered_extent)
        #    layout.exportToJPEG(download_folder + '/EBAR' + str(param_range_map_id) + '.jpg', 300,
        #                        clip_to_elements=True)

        # generate pdf
        if param_pdf == 'true':
            EBARUtils.displayMessage(messages, 'Generating PDF')
            # combine map and metadata html
            body = '''
            <html>
              <head>
                <meta name="pdfkit-orientation" content="Landscape"/>
              </head>
              <style>
                body {
                  font-family:"Trebuchet MS","Lucida Grande","Lucida Sans Unicode","Lucida Sans",Tahoma,sans-serif;
                }
              </style>
              <img src="''' + download_folder + '/EBAR' + str(param_range_map_id) + '.jpg' + '''" width="1500">
              <br>
              ''' + metadata_body + '''
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
            pdfkit.from_string(body, download_folder + '/EBAR' + str(param_range_map_id) + '.pdf', pdf_options)

        # generate zip
        if param_spatial == 'true':
            EBARUtils.displayMessage(messages, 'Generating Spatial Data (ZIP)')

        # cleanup
        if param_jpg != 'true':
            pass

        return


# controlling process
if __name__ == '__main__':
    prm = PublishRangeMapTool()
    # hard code parameters for debugging
    param_range_map_id = arcpy.Parameter()
    param_range_map_id.value = '199'
    param_pdf = arcpy.Parameter()
    param_pdf.value = 'true'
    param_jpg = arcpy.Parameter()
    param_jpg.value = 'true'
    param_spatial = arcpy.Parameter()
    param_spatial.value = 'true'
    parameters = [param_range_map_id, param_pdf, param_jpg, param_spatial]
    prm.RunPublishRangeMapTool(parameters, None)
