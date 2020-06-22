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


class PublishRangeMapTool:
    """Create JPG, PDF and Spatial Data (Zip) for a Range Map"""
    def __init__(self):
        pass

    def RunPublishRangeMapTool(self, parameters, messages):
        # debugging/testing
        #print(locale.getpreferredencoding())
        #return

        # check out any needed extension licenses
        #arcpy.CheckOutExtension('Spatial')

        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True
        arcgis_pro_project = 'C:/GIS/EBAR/EBAR.aprx'
        resources_folder = 'C:/GIS/EBAR/pub/resources'
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

        # get range map data
        species_id = None
        with arcpy.da.SearchCursor(ebar_feature_service + '/11', ['SpeciesID'],
                                   'RangeMapID = ' + str(param_range_map_id)) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                species_id = row['SpeciesID']
            if species_id:
                del row
            else:
                EBARUtils.displayMessage(messages, 'ERROR: Range Map Not Found')
                # terminate with error
                return

        # generate jpg
        if param_pdf == 'true' or param_jpg == 'true':
            EBARUtils.displayMessage(messages, 'Generating JPG')
            aprx = arcpy.mp.ArcGISProject(arcgis_pro_project)
            map = aprx.listMaps('Range Map Landscape Topographic')[0]
            polygon_layer = map.listLayers('EcoshapeRangeMap')[0]
            polygon_layer.definitionQuery = 'rangemapid = ' + str(param_range_map_id)
            table_layer = map.listTables('RangeMap')[0]
            table_layer.definitionQuery = 'rangemapid = ' + str(param_range_map_id)
            layout = aprx.listLayouts('Range Map Landscape Topographic')[0]
            map_frame = layout.listElements('MAPFRAME_ELEMENT')[0]
            extent = map_frame.getLayerExtent(polygon_layer, False, True)
            x_buffer = (extent.XMax - extent.XMin) / 20.0
            y_buffer = (extent.YMax - extent.YMin) / 20.0
            buffered_extent = arcpy.Extent(extent.XMin - x_buffer,
                                           extent.YMin - y_buffer,
                                           extent.XMax + x_buffer,
                                           extent.YMax + y_buffer)
            map_frame.camera.setExtent(buffered_extent)
            layout.exportToJPEG(download_folder + '/EBAR' + str(param_range_map_id) + '.jpg', 300,
                                clip_to_elements=True)

        # generate pdf
        if param_pdf == 'true':
            pass

        # generate zip
        if param_spatial == 'true':
            pass

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
