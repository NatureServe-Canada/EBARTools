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
import EBARUtils
import arcpy
import datetime
import pdfkit
import shutil
import urllib
import io


class PublishRangeMapTool:
    """Create JPG, PDF and Spatial Data (Zip) for a Range Map"""
    def __init__(self):
        pass

    def runPublishRangeMapTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True
        arcgis_pro_project = EBARUtils.resources_folder + '/EBARMapLayouts.aprx'
        pdf_template_file = EBARUtils.resources_folder + '/pdf_template.html'
        #reviewers_by_taxa_file = 'C:/Users/rgree/OneDrive/EBAR/EBAR Maps/TestReviewersByTaxa.txt'
        reviewers_by_taxa_link = 'https://onedrive.live.com/download?cid=AAAAAE977404FA3B&resid=AAAAAE977404FA3B' + \
            '%21447909&authkey=AGzKOrgGlB1SHSE'

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        param_range_map_id = parameters[0].valueAsText
        EBARUtils.displayMessage(messages, 'Range Map ID: ' + param_range_map_id)
        param_spatial = parameters[1].valueAsText
        EBARUtils.displayMessage(messages, 'Include Spatial: ' + param_spatial)

        # replace metadata html tags with real data
        EBARUtils.displayMessage(messages, 'Filling metadata template')
        pdf_template = open(pdf_template_file)
        pdf_html = pdf_template.read()
        pdf_template.close()

        # headers 
        pdf_html = pdf_html.replace('[logo_image]', EBARUtils.resources_folder + '/NatureServeCanada H 4C logo Small.png')
        pdf_html = pdf_html.replace('[species_header_image]', EBARUtils.resources_folder + '/species_header.png')
        pdf_html = pdf_html.replace('[rank_status_header_image]', EBARUtils.resources_folder +
                                                '/rank_status_header.png')
        pdf_html = pdf_html.replace('[range_map_header_image]', EBARUtils.resources_folder +
                                                '/range_map_header.png')
        pdf_html = pdf_html.replace('[reviews_header_image]', EBARUtils.resources_folder + '/reviews_header.png')
        pdf_html = pdf_html.replace('[credits_header_image]', EBARUtils.resources_folder + '/credits_header.png')

        # get species_id
        EBARUtils.displayMessage(messages, 'Getting SpeciesID from database')
        species_id = None
        arcpy.MakeTableView_management(EBARUtils.ebar_feature_service + '/11', 'range_map_view',
                                       'RangeMapID = ' + param_range_map_id)
        with arcpy.da.SearchCursor('range_map_view', ['SpeciesID']) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                species_id = row['SpeciesID']
            if species_id:
                del row
            else:
                EBARUtils.displayMessage(messages, 'ERROR: Range Map Not Found')
                # terminate with error
                return

        # get species data from database
        EBARUtils.displayMessage(messages, 'Getting Species data from database')
        endemism_type = 'None'
        arcpy.MakeTableView_management(EBARUtils.ebar_feature_service + '/19', 'species_view',
                                       'SpeciesID = ' + str(species_id))
        with arcpy.da.SearchCursor('species_view', ['Endemism_Type']) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                if row['Endemism_Type']:
                    endemism_type = row['Endemism_Type']
            del row
        pdf_html = pdf_html.replace('[Species.Endemism_Type]', endemism_type)

        # get biotics data from database
        EBARUtils.displayMessage(messages, 'Getting Biotics data from database')
        arcpy.MakeTableView_management(EBARUtils.ebar_feature_service + '/4', 'biotics_view',
                                       'SpeciesID = ' + str(species_id))
        with arcpy.da.SearchCursor('biotics_view', 
                                   ['NATIONAL_SCIENTIFIC_NAME', 'NATIONAL_ENGL_NAME', 'NATIONAL_FR_NAME',
                                    'ELEMENT_NATIONAL_ID', 'ELEMENT_GLOBAL_ID', 'ELEMENT_CODE', 
                                    'GLOBAL_UNIQUE_IDENTIFIER', 'G_JURIS_ENDEM_DESC', 'AUTHOR_NAME',
                                    'FORMATTED_FULL_CITATION']) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                pdf_html = pdf_html.replace('[BIOTICS_ELEMENT_NATIONAL.NATIONAL_SCIENTIFIC_NAME]',
                                            row['NATIONAL_SCIENTIFIC_NAME'])
                author_name = ''
                if row['AUTHOR_NAME']:
                    author_name = row['AUTHOR_NAME']
                pdf_html = pdf_html.replace('[BIOTICS_ELEMENT_NATIONAL.AUTHOR_NAME]', author_name)
                pdf_html = pdf_html.replace('[BIOTICS_ELEMENT_NATIONAL.FORMATTED_FULL_CITATION]',
                                            row['FORMATTED_FULL_CITATION'])
                pdf_html = pdf_html.replace('[BIOTICS_ELEMENT_NATIONAL.NATIONAL_ENGL_NAME]',
                                            row['NATIONAL_ENGL_NAME'])
                french_name = ''
                if row['NATIONAL_FR_NAME']:
                    french_name = row['NATIONAL_FR_NAME']
                pdf_html = pdf_html.replace('[BIOTICS_ELEMENT_NATIONAL.NATIONAL_FR_NAME]', french_name)
                pdf_html = pdf_html.replace('[BIOTICS_ELEMENT_NATIONAL.ELEMENT_NATIONAL_ID]',
                                            str(row['ELEMENT_NATIONAL_ID']))
                element_global_id = str(row['ELEMENT_GLOBAL_ID'])
                pdf_html = pdf_html.replace('[BIOTICS_ELEMENT_NATIONAL.ELEMENT_GLOBAL_ID]',
                                            element_global_id)
                element_code = row['ELEMENT_CODE']
                pdf_html = pdf_html.replace('[BIOTICS_ELEMENT_NATIONAL.ELEMENT_CODE]', element_code)
                global_unique_id = row['GLOBAL_UNIQUE_IDENTIFIER']
                global_unique_id = global_unique_id.replace('-', '.')
                nsx_url = 'https://explorer.natureserve.org/Taxon/ELEMENT_GLOBAL.' + global_unique_id
                pdf_html = pdf_html.replace('[NSE2.0_URL]', nsx_url)
                #endemism = 'None'
                #if row['G_JURIS_ENDEM_DESC']:
                #    endemism = row['G_JURIS_ENDEM_DESC']
                #pdf_html = pdf_html.replace('[BIOTICS_ELEMENT_NATIONAL.G_JURIS_ENDEM_DESC]', endemism)
            del row

        # get input references
        EBARUtils.displayMessage(messages, 'Getting InputReferences from database')
        input_references = ''
        arcpy.MakeTableView_management(EBARUtils.ebar_summary_service + '/7', 'citation_view',
                                       'RangeMapID = ' + param_range_map_id)
        with arcpy.da.SearchCursor('citation_view', ['DatasetSourceName', 'DatasetSourceCitation',
                                                     'DatasetSourceWebsite']) as cursor:
            row = None
            for row in EBARUtils.searchCursor(cursor):
                if len (input_references) > 0:
                    input_references += '<br>'
                input_references += row['DatasetSourceName'] + ' - ' + row['DatasetSourceCitation']
                if row['DatasetSourceWebsite']:
                    input_references += ' (<a href="' + row['DatasetSourceWebsite'] + '">' + \
                        row['DatasetSourceWebsite'] + '</a>)'
            if row:
                del row
        pdf_html = pdf_html.replace('[InputReferences]', input_references)

        # get range map data from database
        EBARUtils.displayMessage(messages, 'Getting RangeMap data from database')
        range_map_scope = None
        with arcpy.da.SearchCursor('range_map_view',
                                    ['SpeciesID', 'RangeVersion', 'RangeStage', 'RangeDate', 'RangeMapScope',
                                     'RangeMapNotes', 'RangeMetadata', 'RangeMapComments',
                                     'IncludeInDownloadTable']) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                pdf_html = pdf_html.replace('[RangeMap.RangeDate]', row['RangeDate'].strftime('%B %d, %Y'))
                pdf_html = pdf_html.replace('[RangeMap.RangeVersion]', row['RangeVersion'])
                pdf_html = pdf_html.replace('[RangeMap.RangeStage]', row['RangeStage'])
                range_map_scope = EBARUtils.scope_dict[row['RangeMapScope']]
                pdf_html = pdf_html.replace('[RangeMap.RangeMapScope]', range_map_scope)
                pdf_html = pdf_html.replace('[RangeMap.RangeMapNotes]', row['RangeMapNotes'])
                pdf_html = pdf_html.replace('[RangeMap.RangeMetadata]', row['RangeMetadata'])
                comment = ''
                if row['RangeMapComments']:
                    comment += row['RangeMapComments']
                if row['IncludeInDownloadTable'] == 1:
                    if len(comment) > 0:
                        comment += '<br>'
                    comment += '<a href="' + EBARUtils.download_url + '/EBAR' + element_global_id + \
                        '.zip" target="_blank">Please see spatial data for reviewer comments</a>.'
                if len(comment) == 0:
                    comment = 'None'
                pdf_html = pdf_html.replace('[RangeMap.RangeMapComments]', comment)
            if range_map_scope:
                del row

        # insert fixed list of reviewers by taxa
        EBARUtils.displayMessage(messages, 'Inserting ReviewersByTaxa file')
        reviewers_by_taxa_html = None
        #reviewers = io.open(reviewers_by_taxa_file, 'r', encoding='mbcs') # mbcs encoding is Windows ANSI
        #for reviewer_line in reviewers:
        for reviewer_line in urllib.request.urlopen(reviewers_by_taxa_link):
            if not reviewers_by_taxa_html:
                reviewers_by_taxa_html = '<tr><th>Reviewers by Taxa:</th>'
            else:
                reviewers_by_taxa_html += '<tr><th></th>'
            # mbcs encoding is Windows ANSI
            reviewers_by_taxa_html += '<td>' + reviewer_line.decode('mbcs') + '</td></tr>'
        pdf_html = pdf_html.replace('[ReviewersByTaxa]', reviewers_by_taxa_html)
        #reviewers.close()

        # get taxon attributes
        EBARUtils.displayMessage(messages, 'Getting taxon attributes')
        attributes = EBARUtils.getTaxonAttributes(global_unique_id, element_global_id, param_range_map_id, messages)

        # update template
        pdf_html = pdf_html.replace('[NSE.grank]', attributes['g_rank'])
        pdf_html = pdf_html.replace('[NSE.grankReviewDate]', attributes['reviewed_grank'])
        pdf_html = pdf_html.replace('[NSE.CARank]', attributes['ca_rank'])
        pdf_html = pdf_html.replace('[NSE.USRank]', attributes['us_rank'])
        pdf_html = pdf_html.replace('[NSE.MXRank]', attributes['mx_rank'])
        if len(attributes['ca_subnational_list']) > 0:
            attributes['ca_subnational_list'].sort()
            attributes['ca_subnational_ranks'] = ', '.join(attributes['ca_subnational_list'])
        pdf_html = pdf_html.replace('[NSE.CASubnationalRanks]', attributes['ca_subnational_ranks'])
        if len(attributes['us_subnational_list']) > 0:
            attributes['us_subnational_list'].sort()
            attributes['us_subnational_ranks'] = ', '.join(attributes['us_subnational_list'])
        pdf_html = pdf_html.replace('[NSE.USSubnationalRanks]', attributes['us_subnational_ranks'])
        if len(attributes['mx_subnational_list']) > 0:
            attributes['mx_subnational_list'].sort()
            attributes['mx_subnational_ranks'] = ', '.join(attributes['mx_subnational_list'])
        pdf_html = pdf_html.replace('[NSE.MXSubnationalRanks]', attributes['mx_subnational_ranks'])
        pdf_html = pdf_html.replace('[NSE.saraStatus]', attributes['sara_status'])
        pdf_html = pdf_html.replace('[NSE.cosewicStatus]', attributes['cosewic_status'])
        pdf_html = pdf_html.replace('[NSE.esaStatus]', attributes['esa_status'])

        # generate jpg and insert into pdf template
        EBARUtils.displayMessage(messages, 'Generating JPG map')
        aprx = arcpy.mp.ArcGISProject(arcgis_pro_project)
        map = aprx.listMaps('range map landscape terrain')[0]
        polygon_layer = map.listLayers('ecoshaperangemap')[0]
        polygon_layer.definitionQuery = 'rangemapid = ' + param_range_map_id
        table_layer = map.listTables('rangemap')[0]
        table_layer.definitionQuery = 'rangemapid = ' + param_range_map_id
        layout = aprx.listLayouts('range map landscape terrain watermark')[0]
        map_frame = layout.listElements('mapframe_element')[0]
        extent = map_frame.getLayerExtent(polygon_layer, False, True)
        x_buffer = (extent.XMax - extent.XMin) / 20.0
        y_buffer = (extent.YMax - extent.YMin) / 20.0
        buffered_extent = arcpy.Extent(extent.XMin - x_buffer,
                                       extent.YMin - y_buffer,
                                       extent.XMax + x_buffer,
                                       extent.YMax + y_buffer)
        map_frame.camera.setExtent(buffered_extent)
        if range_map_scope == 'Canadian':
            element_global_id += 'N'
        layout.exportToJPEG(EBARUtils.download_folder + '/EBAR' + element_global_id + '.jpg', 300,
                            clip_to_elements=False)
        pdf_html = pdf_html.replace('[map_image]', EBARUtils.download_folder + '/EBAR' + element_global_id + '.jpg')

        # generate pdf
        EBARUtils.displayMessage(messages, 'Generating PDF')
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
            'no-outline': None,
            'enable-local-file-access': None
        }
        pdfkit.from_string(pdf_html, EBARUtils.download_folder + '/EBAR' + element_global_id + '.pdf', pdf_options)

        # generate zip
        if param_spatial == 'true':
            # generate metadata
            EBARUtils.displayMessage(messages, 'Generating metadata')
            md = arcpy.metadata.Metadata()
            md.tags = 'Species Range, NatureServe Canada, Ecosystem-based Automated Range'
            md.description = 'See EBAR' + element_global_id + '.pdf for map and additional metadata, and ' + \
                'EBARMethods.pdf for additional details. <a href="' + nsx_url + '">Go to ' + \
                'NatureServe Explorer</a> for information about the species.'
            md.credits = 'Copyright NatureServe Canada ' + str(datetime.datetime.now().year)
            md.accessConstraints = 'Publicly shareable under CC BY 4.0 (<a href=' + \
                '"https://creativecommons.org/licenses/by/4.0/">https://creativecommons.org/licenses/by/4.0/</a>)'

            # make folder, copy in static resources and EBAR pdf
            EBARUtils.displayMessage(messages, 'Creating ZIP folder and copying files')
            EBARUtils.createReplaceFolder(EBARUtils.temp_folder + '/EBAR' + element_global_id)
            zip_folder = EBARUtils.temp_folder + '/EBAR' + element_global_id
            EBARUtils.createReplaceFolder(zip_folder)
            shutil.copyfile(EBARUtils.resources_folder + '/Readme.txt', zip_folder + '/Readme.txt')
            shutil.copyfile(EBARUtils.resources_folder + '/EBARMethods.pdf', zip_folder + '/EBARMethods.pdf')
            shutil.copyfile(EBARUtils.download_folder + '/EBAR' + element_global_id + '.pdf',
                            zip_folder + '/EBAR' + element_global_id + '.pdf')
            shutil.copyfile(EBARUtils.resources_folder + '/Jurisdiction.csv', zip_folder + '/Jurisdiction.csv')
            jurisdiction_md = arcpy.metadata.Metadata(zip_folder + '/Jurisdiction.csv')
            md.title = 'EBAR Jurisdiction.csv'
            md.summary = 'Table of Jurisdictions'
            jurisdiction_md.copy(md)
            jurisdiction_md.save()

            # export range map, with biotics/species additions
            EBARUtils.displayMessage(messages, 'Exporting RangeMap to CSV')
            EBARUtils.ExportRangeMapToCSV('range_map_view' + param_range_map_id, [param_range_map_id],
                                          {param_range_map_id: attributes}, zip_folder, 'RangeMap.csv', md)

            # export range map ecoshapes
            EBARUtils.displayMessage(messages, 'Exporting RangeMapEcoshape records to CSV')
            EBARUtils.ExportRangeMapEcoshapesToCSV('range_map_ecoshape_view' + param_range_map_id,
                                                   [param_range_map_id], zip_folder, 'RangeMapEcoshape.csv', md)

            # export ecoshapes
            EBARUtils.displayMessage(messages, 'Exporting Ecoshape polygons to shapefile')
            EBARUtils.ExportEcoshapesToShapefile('ecoshape_layer' + param_range_map_id,
                                                 'range_map_ecoshape_view' + param_range_map_id, zip_folder, 
                                                 'Ecoshape.shp', md)

            # export overview ecoshapes
            EBARUtils.displayMessage(messages, 'Exporting EcoshapeOverview polygons to shapefile')
            EBARUtils.ExportEcoshapeOverviewsToShapefile('ecoshape_overview_layer' + param_range_map_id,
                                                         'range_map_ecoshape_view' + param_range_map_id, zip_folder, 
                                                         'EcoshapeOverview.shp', md)

            # update ArcGIS Pro template
            EBARUtils.displayMessage(messages, 'Updating ArcGIS Pro template')
            EBARUtils.updateArcGISProTemplate(zip_folder, element_global_id, md, param_range_map_id)

            # copy ArcMap template
            EBARUtils.displayMessage(messages, 'Copying ArcMap template')
            shutil.copyfile(EBARUtils.resources_folder + '/EBAR.mxd',
                            zip_folder + '/EBAR' + element_global_id + '.mxd')
            shutil.copyfile(EBARUtils.resources_folder + '/EcoshapeOverview.lyr',
                            zip_folder + '/EBAR' + element_global_id + 'EcoshapeOverview.lyr')
            shutil.copyfile(EBARUtils.resources_folder + '/Ecoshape.lyr',
                            zip_folder + '/EBAR' + element_global_id + 'Ecoshape.lyr')

            # zip
            EBARUtils.displayMessage(messages, 'Creating ZIP')
            EBARUtils.createZip(zip_folder, EBARUtils.download_folder + '/EBAR' + element_global_id + '.zip', None)

        # set publish date
        with arcpy.da.UpdateCursor('range_map_view', ['PublishDate']) as update_cursor:
            for update_row in EBARUtils.updateCursor(update_cursor):
                update_cursor.updateRow([datetime.datetime.now()])
            del update_row

        # results link messages
        EBARUtils.displayMessage(messages,
                                 'Image: ' + EBARUtils.download_url + '/EBAR' + element_global_id + '.jpg')
        EBARUtils.displayMessage(messages,
                                 'PDF: ' + EBARUtils.download_url + '/EBAR' + element_global_id + '.pdf')
        if param_spatial == 'true':
            EBARUtils.displayMessage(messages,
                                     'GIS Data: ' + EBARUtils.download_url + '/EBAR' + element_global_id + '.zip')

        # cleanup
        arcpy.Delete_management('range_map_view')
        arcpy.Delete_management('biotics_view')
        arcpy.Delete_management('species_view')
        arcpy.Delete_management('citation_view')
        if param_spatial == 'true':
            arcpy.Delete_management('range_map_ecoshape_view')

        return


# controlling process
if __name__ == '__main__':
    prm = PublishRangeMapTool()
    
    #spatial_batch_ids = [448,616,617,618,619,620,621,622,624,625,626,627,628,631,633,634,635,636,637,638,639,640,641,
    #                     665,670,680,685,687,689,706,707,708,709,710,712,713,714,716,719,720,747,749,824,858,859,862,
    #                     865,866,867,869,870,871,1087,1093,1098,1102,1103,1104,1105,1112,1113,1115,1128,1129,1130,1131,
    #                     1133,1134,1135,1136,1137,1138,1139,1140,1142,1143,1144,1145,1146,1147,1149,1151,1152,1153,
    #                     1154,1155,1156,1157,1158,1179,1184,1187,1190,1223,1225,1227,1231,1233,1241,1243,1254,1258,
    #                     1261,1283,1296,1729,1737,1739,1747,1752,1780,1823,1840,1861,1871,1875,1878,1880]
    spatial_batch_ids = [1880]
    for id in spatial_batch_ids:
       # hard code parameters for debugging
       param_range_map_id = arcpy.Parameter()
       param_range_map_id.value = str(id)
       param_spatial = arcpy.Parameter()
       param_spatial.value = 'true'
       parameters = [param_range_map_id, param_spatial]
       prm.runPublishRangeMapTool(parameters, None)
    
    #non_spatial_batch_ids = [1806,645,684,704,1100,1150,1456,1500,1732,1733,1735,1750,1755,1758,1759,1760,1762,1763,
    #                         1764,1765,1766,1767,1768,1774,1776,1778,1779,1782,1786,1788,1789,1791,1793,1796,1797,
    #                         1798,1799,1800,1801,1802,1803,1804,1807,1808,1810,1813,1815,1817,1818,1819,1822,1824,
    #                         1826,1827,1828,1829,1830,1831,1832,1833,1834,1838,1839,1841,1842,1843,1844,1845,1846,
    #                         1847,1848,1850,1851,1852,1853,1854,1855,1857,1860,1863,1864,1872,1876,1896,623,629,644,
    #                         646,671,705,717,718,721,722,723,864,1086,1088,1095,1099,1101,1132,1163,1181,1239,1242,
    #                         1266,1731,1738,1740,1742,1744,1745,1751,1753,1757,1769,1795,1820,1821,1877]
    # for id in non_spatial_batch_ids:
    #     # hard code parameters for debugging
    #     param_range_map_id = arcpy.Parameter()
    #     param_range_map_id.value = str(id)
    #     param_spatial = arcpy.Parameter()
    #     param_spatial.value = 'false'
    #     parameters = [param_range_map_id, param_spatial]
    #     prm.runPublishRangeMapTool(parameters, None)
