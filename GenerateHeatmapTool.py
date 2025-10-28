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
import shutil


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

            # make zip folder and copy existing outputs
            EBARUtils.displayMessage(messages, 'Creating ZIP folder and copying files')
            zip_folder = EBARUtils.temp_folder + '/EBAR_SAR_Heatmap'
            EBARUtils.createReplaceFolder(zip_folder)
            shutil.copyfile(EBARUtils.resources_folder + '/EBAR Heatmap Documentation.pdf',
                            zip_folder + '/EBAR Heatmap Documentation.pdf')
            shutil.copyfile(EBARUtils.download_folder + '/' + jpg + '.jpg', zip_folder + '/' + jpg + '.jpg')

            # make file gdb for usability in Pro (also export to shapefile and CSV for compatability)
            arcpy.CreateFileGDB_management(zip_folder, 'EBAR_SAR_Heatmap.gdb')
            filegdb = zip_folder + '/EBAR_SAR_Heatmap.gdb'

            # export species
            EBARUtils.displayMessage(messages, 'Exporting Species')
            EBARUtils.ExportPublishedSARDistinctSpeciesToTable(param_geodatabase, EBARUtils.download_folder, jpg + '.csv', md)
            #EBARUtils.ExportPublishedSARDistinctSpeciesToTable(param_geodatabase, filegdb, 'BIOTICS_ELEMENT_NATIONAL', md)
            arcpy.TableToTable_conversion(EBARUtils.download_folder + '/' + jpg + '.csv', filegdb,
                                          'BIOTICS_ELEMENT_NATIONAL')
            EBARUtils.displayMessage(messages, 'CSV: ' + EBARUtils.download_url + '/' + jpg + '.csv')
            shutil.copyfile(EBARUtils.download_folder + '/' + jpg + '.csv',
                            zip_folder + '/' + 'BIOTICS_ELEMENT_NATIONAL.csv')

            # export RangeMap
            EBARUtils.displayMessage(messages, 'Exporting RangeMap')
            #arcpy.TableToTable_conversion(param_geodatabase + '/s_PublishedSARRangeMap', zip_folder, 'RangeMap.csv')
            EBARUtils.ExportPublishedSARRangeMapsToTable(param_geodatabase, zip_folder, 'RangeMap.csv', md)
            #arcpy.TableToTable_conversion(param_geodatabase + '/s_PublishedSARRangeMap', filegdb, 'RangeMap')
            arcpy.TableToTable_conversion(zip_folder + '/RangeMap.csv', filegdb, 'RangeMap')
            
            # export RangeMapEcoshape
            EBARUtils.displayMessage(messages, 'Exporting RangeMapEcoshape')
            # arcpy.TableToTable_conversion(param_geodatabase + '/s_PublishedSARRangeMapEcoshape', zip_folder,
            #                               'RangeMapEcoshape.csv')
            EBARUtils.ExportPublishedSARRangeMapEcoshapesToTable(param_geodatabase, zip_folder, 'RangeMapEcoshape.csv',
                                                                 md)
            # arcpy.TableToTable_conversion(param_geodatabase + '/s_PublishedSARRangeMapEcoshape', filegdb,
            #                               'RangeMapEcoshape')
            arcpy.TableToTable_conversion(zip_folder + '/RangeMapEcoshape.csv', filegdb, 'RangeMapEcoshape')

            # # export PublishedSARRangeCount
            # EBARUtils.displayMessage(messages, 'Exporting PublishedSARRangeCount')
            # # arcpy.TableToTable_conversion(param_geodatabase + '/s_PublishedSARRangeCount', zip_folder,
            # #                               'PublishedSARRangeCount.csv')
            # EBARUtils.ExportPublishedSARRangeCountToTable(param_geodatabase, zip_folder, 'PublishedSARRangeCount.csv',
            #                                               md)
            # # arcpy.TableToTable_conversion(param_geodatabase + '/s_PublishedSARRangeCount', filegdb,
            # #                               'PublishedSARRangeCount')
            # arcpy.TableToTable_conversion(zip_folder + '/PublishedSARRangeCount.csv', filegdb,
            #                               'PublishedSARRangeCount')
            
            # # export PublishedSARRangeCountByEcoshape
            # EBARUtils.displayMessage(messages, 'Exporting PublishedSARRangeCountByEcoshape')
            # # arcpy.TableToTable_conversion(param_geodatabase + '/s_PublishedSARRangeCountByEcoshape', zip_folder,
            # #                               'PublishedSARRangeCountByEcoshape.csv')
            # EBARUtils.ExportPublishedSARRangeCountByEcoshape(param_geodatabase, zip_folder,
            #                                                  'PublishedSARRangeCountByEcoshape.csv', md)
            # # arcpy.TableToTable_conversion(param_geodatabase + '/s_PublishedSARRangeCountByEcoshape', filegdb,
            # #                               'PublishedSARRangeCountByEcoshape')
            # arcpy.TableToTable_conversion(zip_folder + '/PublishedSARRangeCountByEcoshape.csv', filegdb,
            #                               'PublishedSARRangeCountByEcoshape')
            
            # export HeatmapEcoshapeOverview
            EBARUtils.displayMessage(messages, 'Exporting HeatmapEcoshapeOverview')
            # arcpy.MakeFeatureLayer_management(param_geodatabase + '/EcoshapeOverview', 'CdnEcoshapes',
            #                                   'JurisdictionID NOT IN (14, 15)')
            # arcpy.CopyFeatures_management('CdnEcoshapes', zip_folder + '/EcoshapeOverview.shp')
            EBARUtils.ExportCanadianEcoshapeOverviewsToShapefile(param_geodatabase, zip_folder,
                                                                 'HeatmapEcoshapeOverview.shp', md)
            # arcpy.CopyFeatures_management('CdnEcoshapes', filegdb + '/EcoshapeOverview')
            EBARUtils.ExportCanadianEcoshapeOverviewsToFC(param_geodatabase, filegdb, 'HeatmapEcoshapeOverview', md)

            # create table relationships
            EBARUtils.displayMessage(messages, 'Creating relationships')
            arcpy.CreateRelationshipClass_management(filegdb + '/HeatmapEcoshapeOverview',
                                                     filegdb + '/RangeMapEcoshape',
                                                     filegdb + '/HeatmapEcoshapeOverview_RangeMapEcoshape', 'SIMPLE',
                                                     'RangeMapEcoshape', 'HeatmapEcoshapeOverview', 'NONE',
                                                     'ONE_TO_MANY', 'NONE', 'EcoshapeID', 'EcoshapeID')
            arcpy.CreateRelationshipClass_management(filegdb + '/RangeMap', filegdb + '/RangeMapEcoshape',
                                                     filegdb + '/RangeMap_RangeMapEcoshape', 'SIMPLE',
                                                     'RangeMapEcoshape', 'RangeMap', 'NONE', 'ONE_TO_MANY', 'NONE',
                                                     'RangeMapID', 'RangeMapID')
            arcpy.CreateRelationshipClass_management(filegdb + '/BIOTICS_ELEMENT_NATIONAL', filegdb + '/RangeMap',
                                                     filegdb + '/BIOTICS_ELEMENT_NATIONAL_RangeMap', 'SIMPLE',
                                                     'RangeMap', 'BIOTICS_ELEMENT_NATIONAL', 'NONE', 'ONE_TO_MANY',
                                                     'NONE', 'SpeciesID', 'SpeciesID')
            
            # export APRX and MAPX from templates
            EBARUtils.displayMessage(messages, 'Copying map')
            shutil.copyfile(EBARUtils.resources_folder + '/EBAR_SAR_Heatmap.aprx',
                            zip_folder + '/EBAR_SAR_Heatmap.aprx')
            shutil.copyfile(EBARUtils.resources_folder + '/EBAR_SAR_Heatmap.mapx',
                            zip_folder + '/EBAR_SAR_Heatmap.mapx')

            # zip
            EBARUtils.createZip(zip_folder, EBARUtils.download_folder + '/EBAR_SAR_Heatmap.zip', None)
            #shutil.make_archive(EBARUtils.download_folder + '/EBAR_SAR_Heatmap.zip', 'zip', zip_folder, zip_folder)
            EBARUtils.displayMessage(messages, 'GIS Data: ' + EBARUtils.download_url + '/EBAR_SAR_Heatmap.zip')

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
