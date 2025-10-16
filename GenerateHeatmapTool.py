# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Samantha Stefanoff
# © NatureServe Canada 2025 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: GenerateHeatmapTool.py
# ArcGIS Python tool for creating JPG heatmaps from EBAR ranges

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import arcpy.management
import EBARUtils
import arcpy
import datetime


class GenerateHeatmapTool:
    """Create JPG heatmaps from EBAR ranges"""
    def __init__(self):
        pass

    def runGenerateHeatmapTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # # debug
        # #desc = arcpy.Describe(EBARUtils.ebar_summary_service + '/22')
        # desc = arcpy.Describe(EBARUtils.ebar_feature_service + '/11')
        # EBARUtils.displayMessage(messages, desc.name)
        # return

        # connect to portal
        # get password from file
        pfile = open(EBARUtils.portal_file)
        password = pfile.read()
        pfile.close()
        arcpy.SignInToPortal('https://gis.natureserve.ca/portal', 'rgreenens', password)

        # settings
        arcpy.gp.overwriteOutput = True
        arcgis_pro_project = EBARUtils.resources_folder + '/EBARMapLayoutsBackup.aprx'

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        param_geodatabase = parameters[0].valueAsText
        param_heatmap_type = parameters[1].valueAsText
        EBARUtils.displayMessage(messages, 'Heatmap type: ' + param_heatmap_type)

        # get map, layout and related objects
        EBARUtils.displayMessage(messages, 'Generating JPG map')
        aprx = arcpy.mp.ArcGISProject(arcgis_pro_project)
        mp = aprx.listMaps('Heatmap')[0]
        layer = mp.listLayers('EcoshapeOverview')[0]
        layout = aprx.listLayouts('Heatmap')[0]
        legend = layout.listElements('LEGEND_ELEMENT', 'Legend')[0]

        # change source of joined table and update symbology
        if param_heatmap_type != 'Published SAR':
            arcpy.management.RemoveJoin(layer) #'L22EcoshapeOverview') #EBARUtils.ebar_summary_service + '/22') #'EcoshapeOverview')
        if param_heatmap_type == 'Published All':
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
        elif param_heatmap_type == 'Published High Quality':
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

        # modify dynamic text
        date_text = layout.listElements('TEXT_ELEMENT', 'DateText')[0]
        date_text.text = datetime.datetime.now().strftime('%B %d, %Y')
        title_text = layout.listElements('TEXT_ELEMENT', 'TitleText')[0]
        if param_heatmap_type != 'Published SAR':
            title_text.text = 'Canadian Biodiversity Heatmap'
        if param_heatmap_type == 'Published All':
            legend.title = 'Count of EBAR Ranges\n(all published ranges)'
        elif param_heatmap_type == 'Published High Quality':
            legend.title = 'Count of EBAR Ranges\n(high quality published ranges)'

        # modify dynamic n= text (directly accesses geodatabase, so only works on server)
        n_text = layout.listElements('TEXT_ELEMENT', 'NText')[0]
        n_view = param_geodatabase + '/s_PublishedSARRangeCount'
        if param_heatmap_type == 'Published All':
            n_view = param_geodatabase + '/s_PublishedRangeCount'
        elif param_heatmap_type == 'Published High Quality':
            n_view = param_geodatabase + '/s_HighQualityRangeCount'
        row = None
        with arcpy.da.SearchCursor(n_view, ['RangeCount']) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                n_text.text = 'n=' + str(int(row['RangeCount']))
        if row:
            del row
        del cursor

        # generate jpg
        jpg = 'EBARHeatmapPublishedSAR'
        if param_heatmap_type == 'Published All':
            jpg = 'EBARHeatmapPublishedAll'
        elif param_heatmap_type == 'Published High Quality':
            jpg = 'EBARHeatmapPublishedHighQuality'
        layout.exportToJPEG(EBARUtils.download_folder + '/' + jpg + '.jpg', 300, clip_to_elements=False)
        #layout.exportToJPEG('D:/GIS/EBAR/' + jpg + '.jpg', 300, clip_to_elements=False)
        EBARUtils.displayMessage(messages, 'Image: ' + EBARUtils.download_url + '/' + jpg + '.jpg')

        # generate species sheet and download zip
        if param_heatmap_type == 'Published SAR':
            # species sheet
            field_mappings = arcpy.FieldMappings()
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'ELEMENT_NATIONAL_ID', 'ELEMENT_NATIONAL_ID', 'LONG'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'ELEMENT_GLOBAL_ID', 'ELEMENT_GLOBAL_ID', 'LONG'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'ELEMENT_CODE', 'ELEMENT_CODE', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'CATEGORY', 'CATEGORY', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'TAX_GROUP', 'TAX_GROUP', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'KINGDOM', 'KINGDOM', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'CLASS', 'CLASS', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'TAX_ORDER', 'TAX_ORDER', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'FAMILY', 'FAMILY', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'NATIONAL_SCIENTIFIC_NAME', 'NATIONAL_SCIENTIFIC_NAME',
                                                                'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'NATIONAL_ENGL_NAME', 'NATIONAL_ENGL_NAME', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'NATIONAL_FR_NAME', 'NATIONAL_FR_NAME', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'COSEWIC_NAME', 'COSEWIC_NAME', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'ENGLISH_COSEWIC_COM_NAME', 'ENGLISH_COSEWIC_COM_NAME',
                                                                'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'FRENCH_COSEWIC_COM_NAME', 'FRENCH_COSEWIC_COM_NAME',
                                                                'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'COSEWIC_STATUS', 'COSEWIC_STATUS', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'SARA_STATUS', 'SARA_STATUS', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'SHORT_CITATION_AUTHOR', 'SHORT_CITATION_AUTHOR',
                                                                'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'SHORT_CITATION_YEAR', 'SHORT_CITATION_YEAR', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'FORMATTED_FULL_CITATION', 'FORMATTED_FULL_CITATION',
                                                                'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                                                'NSX_URL', 'NSX_URL', 'TEXT'))
            arcpy.ExportTable_conversion(param_geodatabase + '/s_PublishedSARDistinctSpecies',
                                         EBARUtils.download_folder + '/' + jpg + '.csv', field_mapping=field_mappings)
            EBARUtils.displayMessage(messages, 'Species sheet: ' + EBARUtils.download_url + '/' + jpg + '.csv')
            # download zip
            zip_folder = EBARUtils.temp_folder + '/EBAR_SAR_Heatmap'
            EBARUtils.createReplaceFolder(zip_folder)
            EBARUtils.createZip(zip_folder, EBARUtils.download_folder + '/EBAR_SAR_Heatmap.zip', None)
            EBARUtils.addToZip(EBARUtils.download_folder + '/EBAR_SAR_Heatmap.zip',
                               EBARUtils.resources_folder + '/EBAR Heatmapping Documentation.pdf')
            EBARUtils.addToZip(EBARUtils.download_folder + '/EBAR_SAR_Heatmap.zip',
                               EBARUtils.download_folder + '/' + jpg + '.jpg')
            EBARUtils.addToZip(EBARUtils.download_folder + '/EBAR_SAR_Heatmap.zip',
                               EBARUtils.download_folder + '/' + jpg + '.csv')
            EBARUtils.displayMessage(messages, 'Download zip: ' + EBARUtils.download_url + '/' + jpg + '.zip')

        return


# controlling process
if __name__ == '__main__':
    ghm = GenerateHeatmapTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:/GIS/EBAR/nsc-gis-ebarkba.sde' #'D:/GIS/EBAR/EBAR.gdb'
    param_heatmap_type = arcpy.Parameter()
    param_heatmap_type.value = 'Published SAR' # 'Published High Quality' # 'Published All' 
    parameters = [param_geodatabase, param_heatmap_type]
    ghm.runGenerateHeatmapTool(parameters, None)
