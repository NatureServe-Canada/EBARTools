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

        # generate download zip
        if param_heatmap_type == 'Published SAR':
            # generate metadata
            EBARUtils.displayMessage(messages, 'Generating metadata')
            md = arcpy.metadata.Metadata()
            md.tags = 'Species Range, NatureServe Canada, Ecosystem-based Automated Range, Heatmap'
            md.description = 'Heatmap summarizing the number of published EBAR SAR ranges that intersect each Ecoshape'
            md.credits = 'Copyright NatureServe Canada ' + str(datetime.datetime.now().year)
            md.accessConstraints = 'Publicly shareable under CC BY 4.0 (<a href=' + \
                '"https://creativecommons.org/licenses/by/4.0/">https://creativecommons.org/licenses/by/4.0/</a>)'

            # export species to CSV
            # export range map ecoshapes
            EBARUtils.displayMessage(messages, 'Exporting Species to CSV')
            EBARUtils.ExportRangeMapEcoshapesToCSV('range_map_ecoshape_view' + param_range_map_id,
                                                   [param_range_map_id], zip_folder, 'RangeMapEcoshape.csv', md)
            EBARUtils.ExportHeatmapSpeciesToCSV(param_geodatabase, zip_folder, 'BIOTICS_ELEMENT_NATIONAL.csv')

            # make zip and copy static outputs
            zip_folder = EBARUtils.temp_folder + '/EBAR_SAR_Heatmap'
            EBARUtils.createReplaceFolder(zip_folder)
            EBARUtils.createZip(zip_folder, EBARUtils.download_folder + '/EBAR_SAR_Heatmap.zip', None)
            EBARUtils.addToZip(EBARUtils.download_folder + '/EBAR_SAR_Heatmap.zip',
                               EBARUtils.resources_folder + '/EBAR Heatmap Documentation.pdf')
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
