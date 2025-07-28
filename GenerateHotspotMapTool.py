# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Samantha Stefanoff
# © NatureServe Canada 2025 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: GenerateHotspotMapTool.py
# ArcGIS Python tool for creating JPG hotspot maps from EBAR ranges

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import arcpy.management
import EBARUtils
import arcpy
import datetime


class GenerateHotspotMapTool:
    """Create JPG hotspot maps from EBAR ranges"""
    def __init__(self):
        pass

    def runGenerateHotspotMapTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True
        arcgis_pro_project = EBARUtils.resources_folder + '/EBARMapLayoutsBackup.aprx'

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        param_geodatabase = parameters[0].valueAsText
        param_hotspot_type = parameters[1].valueAsText
        EBARUtils.displayMessage(messages, 'Hotspot type: ' + param_hotspot_type)

        # get table name prefix (needed for joined tables and feature classes in enterprise geodatabases)
        table_name_prefix = EBARUtils.getTableNamePrefix(param_geodatabase)

        # get map, layout and related objects
        EBARUtils.displayMessage(messages, 'Generating JPG map')
        aprx = arcpy.mp.ArcGISProject(arcgis_pro_project)
        mp = aprx.listMaps('Hotspots')[0]
        layer = mp.listLayers('EcoshapeOverview')[0]
        layout = aprx.listLayouts('Hotspots')[0]
        legend = layout.listElements('LEGEND_ELEMENT', 'Legend')[0]

        # change source of joined table and update symbology
        if param_hotspot_type != 'Published SAR':
            arcpy.management.RemoveJoin(layer) #'L22EcoshapeOverview') #EBARUtils.ebar_summary_service + '/22') #'EcoshapeOverview')
        if param_hotspot_type == 'Published All':
            # arcpy.management.AddJoin(layer, 'EcoshapeID', 'PublishedRangeCountByEcoshape', 'EcoshapeID',
            arcpy.management.AddJoin(layer, 'EcoshapeID', EBARUtils.ebar_summary_service + '/16', 'ecoshapeid',
                                     'KEEP_COMMON')
            symbology = layer.symbology
            renderer = symbology.renderer
            # renderer.classificationField = "$feature['L16PublishedRangeCountByEcoshape.count']"
            renderer.classificationField = 'L16PublishedRangeCountByEcoshape.count'
            for brk in renderer.classBreaks:
                brk.symbol.outlineWidth = 0 #outlineColor = {'RGB' : [255, 255, 255, 0]}
            layer.symbology = symbology
        elif param_hotspot_type == 'Published High Quality':
            # arcpy.management.AddJoin(layer, 'EcoshapeID', 'HighQualityRangeCountByEcoshape', 'EcoshapeID',
            arcpy.management.AddJoin(layer, 'EcoshapeID', EBARUtils.ebar_summary_service + '/9', 'ecoshapeid',
                                     'KEEP_COMMON')
            symbology = layer.symbology
            renderer = symbology.renderer
            # renderer.classificationField = "$feature['L9HighQualityRangeCountByEcoshape.count']"
            renderer.classificationField = 'L9HighQualityRangeCountByEcoshape.count'
            for brk in renderer.classBreaks:
                brk.symbol.outlineWidth = 0 #outlineColor = {'RGB' : [255, 255, 255, 0]}
            layer.symbology = symbology

        # modify dynamic title and legend text
        title_text = layout.listElements('TEXT_ELEMENT', 'TitleText')[0]
        if param_hotspot_type != 'Published SAR':
            title_text.text = 'Canadian Biodiversity Hotspots'
        if param_hotspot_type == 'Published All':
            legend.title = 'Count of EBAR Ranges\n(all published ranges)'
        elif param_hotspot_type == 'Published High Quality':
            legend.title = 'Count of EBAR Ranges\n(high quality published ranges)'

        # modify dynamic n= text (directly access views, so only works on server)
        n_text = layout.listElements('TEXT_ELEMENT', 'NText')[0]
        n_view = param_geodatabase + '/s_PublishedSARRangeCount'
        if param_hotspot_type == 'Published All':
            n_view = param_geodatabase + '/s_PublishedRangeCount'
        elif param_hotspot_type == 'Published High Quality':
            n_view = param_geodatabase + '/s_HighQualityRangeCount'
        row = None
        with arcpy.da.SearchCursor(n_view, ['RangeCount']) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                n_text.text = 'n=' + str(int(row['RangeCount']))
        if row:
            del row
        del cursor

        # generate jpg
        jpg = 'EBARHotspotsPublishedSAR'
        if param_hotspot_type == 'Published All':
            jpg = 'EBARHotspotsPublishedAll'
        elif param_hotspot_type == 'Published High Quality':
            jpg = 'EBARHotspotsPublishedHighQuality'
        layout.exportToJPEG(EBARUtils.download_folder + '/' + jpg + '.jpg', 300, clip_to_elements=False)
        #layout.exportToJPEG('D:/GIS/EBAR/' + jpg + '.jpg', 300, clip_to_elements=False)

        # results link messages
        EBARUtils.displayMessage(messages, 'Image: ' + EBARUtils.download_url + '/' + jpg + '.jpg')

        return


# controlling process
if __name__ == '__main__':
    ghm = GenerateHotspotMapTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:/GIS/EBAR/nsc-gis-ebarkba.sde' #'D:/GIS/EBAR/EBAR.gdb'
    param_hotspot_type = arcpy.Parameter()
    param_hotspot_type.value = 'Published High Quality' #'Published All' #'Published SAR' # #
    parameters = [param_geodatabase, param_hotspot_type]
    ghm.runGenerateHotspotMapTool(parameters, None)
