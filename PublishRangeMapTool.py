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
        arcgis_pro_project = 'C:/GIS/EBAR/EBARTools/resources/EBARMapLayouts.aprx'
        pdf_template_file = 'C:/GIS/EBAR/EBARTools/resources/pdf_template.html'
        resources_folder = 'C:/GIS/EBAR/EBARTools/resources'
        reviewers_by_taxa_file = 'C:/GIS/EBAR/EBARTools/resources/ReviewersByTaxa.txt'
        temp_folder = 'C:/GIS/EBAR/pub/temp'
        download_folder = 'C:/GIS/EBAR/pub/download'
        ebar_feature_service = 'https://gis.natureserve.ca/arcgis/rest/services/EBAR-KBA/EBAR/FeatureServer'
        ebar_summary_service = 'https://gis.natureserve.ca/arcgis/rest/services/EBAR-KBA/Summary/FeatureServer'
        nse_species_search_url = 'https://explorer.natureserve.org/api/data/search'
        nse_taxon_search_url = 'https://explorer.natureserve.org/api/data/taxon/ELEMENT_GLOBAL.2.'

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
            pdf_template = open(pdf_template_file)
            pdf_html = pdf_template.read()
            pdf_template.close()

            # map file and headers 
            pdf_html = pdf_html.replace('[map_image]', download_folder + '/EBAR' + str(param_range_map_id) + '.jpg')
            pdf_html = pdf_html.replace('[logo_image]', resources_folder + '/nscanada_inline_copy.png')
            pdf_html = pdf_html.replace('[species_header_image]', resources_folder + '/species_header.png')
            pdf_html = pdf_html.replace('[rank_status_header_image]', resources_folder +
                                                  '/rank_status_header.png')
            pdf_html = pdf_html.replace('[range_map_header_image]', resources_folder +
                                                  '/range_map_header.png')
            pdf_html = pdf_html.replace('[reviews_header_image]', resources_folder + '/reviews_header.png')
            pdf_html = pdf_html.replace('[credits_header_image]', resources_folder + '/credits_header.png')

            # get range map data from database
            EBARUtils.displayMessage(messages, 'Getting RangeMap data from database')
            species_id = None
            range_map_scope = None
            with arcpy.da.SearchCursor(ebar_feature_service + '/11',
                                       ['SpeciesID', 'RangeVersion', 'RangeStage', 'RangeDate', 'RangeMapScope',
                                        'RangeMapNotes', 'RangeMetadata', 'RangeMapComments'],
                                        'RangeMapID = ' + str(param_range_map_id)) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    species_id = row['SpeciesID']
                    pdf_html = pdf_html.replace('[RangeMap.RangeDate]', row['RangeDate'].strftime('%B %d, %Y'))
                    pdf_html = pdf_html.replace('[RangeMap.RangeVersion]', row['RangeVersion'])
                    pdf_html = pdf_html.replace('[RangeMap.RangeStage]', row['RangeStage'])
                    range_map_scope = EBARUtils.scope_dict[row['RangeMapScope']]
                    pdf_html = pdf_html.replace('[RangeMap.RangeMapScope]', range_map_scope)
                    pdf_html = pdf_html.replace('[RangeMap.RangeMapNotes]', row['RangeMapNotes'])
                    pdf_html = pdf_html.replace('[RangeMap.RangeMetadata]', row['RangeMetadata'])
                    pdf_html = pdf_html.replace('[RangeMap.RangeMapComments]', str(row['RangeMapComments']))
                if species_id:
                    del row
                else:
                    EBARUtils.displayMessage(messages, 'ERROR: Range Map Not Found')
                    # terminate with error
                    return

            # get biotics data from database
            EBARUtils.displayMessage(messages, 'Getting Biotics data from database')
            element_global_id = None
            element_code = None
            with arcpy.da.SearchCursor(ebar_feature_service + '/4', 
                                       ['NATIONAL_SCIENTIFIC_NAME', 'NATIONAL_ENGL_NAME', 'NATIONAL_FR_NAME',
                                        'ELEMENT_NATIONAL_ID', 'ELEMENT_GLOBAL_ID', 'ELEMENT_CODE',
                                        'G_JURIS_ENDEM_DESC'],
                                       'SpeciesID = ' + str(species_id)) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    pdf_html = pdf_html.replace('[BIOTICS_ELEMENT_NATIONAL.NATIONAL_SCIENTIFIC_NAME]',
                                                          row['NATIONAL_SCIENTIFIC_NAME'])
                    pdf_html = pdf_html.replace('[BIOTICS_ELEMENT_NATIONAL.NATIONAL_ENGL_NAME]',
                                                          row['NATIONAL_ENGL_NAME'])
                    french_name = ''
                    if row['NATIONAL_FR_NAME']:
                        french_name = row['NATIONAL_FR_NAME']
                    pdf_html = pdf_html.replace('[BIOTICS_ELEMENT_NATIONAL.NATIONAL_FR_NAME]',
                                                          french_name)
                    pdf_html = pdf_html.replace('[BIOTICS_ELEMENT_NATIONAL.ELEMENT_NATIONAL_ID]',
                                                          str(row['ELEMENT_NATIONAL_ID']))
                    element_global_id = str(row['ELEMENT_GLOBAL_ID'])
                    pdf_html = pdf_html.replace('[BIOTICS_ELEMENT_NATIONAL.ELEMENT_GLOBAL_ID]',
                                                          element_global_id)
                    element_code = row['ELEMENT_CODE']
                    pdf_html = pdf_html.replace('[BIOTICS_ELEMENT_NATIONAL.ELEMENT_CODE]', element_code)
                    #endemism = 'None'
                    #if row['G_JURIS_ENDEM_DESC']:
                    #    endemism = row['G_JURIS_ENDEM_DESC']
                    #pdf_html = pdf_html.replace('[BIOTICS_ELEMENT_NATIONAL.G_JURIS_ENDEM_DESC]', endemism)
                del row

            # get species data from database
            EBARUtils.displayMessage(messages, 'Getting Species data from database')
            endemism_type = 'None'
            with arcpy.da.SearchCursor(ebar_feature_service + '/19', ['Endemism_Type'],
                                       'SpeciesID = ' + str(species_id)) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    if row['Endemism_Type']:
                        endemism_type = row['Endemism_Type']
                del row
            pdf_html = pdf_html.replace('[Species.Endemism_Type]', endemism_type)

            # get input references
            EBARUtils.displayMessage(messages, 'Getting InputReferences from database')
            input_references = ''
            with arcpy.da.SearchCursor(ebar_summary_service + '/7', ['DatasetSourceName', 'DatasetSourceCitation'],
                                       'RangeMapID = ' + str(param_range_map_id)) as cursor:
                row = None
                for row in EBARUtils.searchCursor(cursor):
                    if len (input_references) > 0:
                        input_references += '<br>'
                    input_references += row['DatasetSourceName'] + ' - ' + row['DatasetSourceCitation']
                if row:
                    del row
            pdf_html = pdf_html.replace('[InputReferences]', input_references)

            # insert fixed list of reviewers by taxa
            EBARUtils.displayMessage(messages, 'Inserting ReviewersByTaxa file')
            reviewers = open(reviewers_by_taxa_file)
            pdf_html = pdf_html.replace('[ReviewersByTaxa]', reviewers.read())
            reviewers.close()

            # get attributes from NSE Species Search API
            #EBARUtils.displayMessage(messages, 'Getting attributes from NatureServe Explorer Species Search API')
            #headers = {'Accept': 'application/json', 'Content-Type': 'application/json; charset=UTF-8'}
            #params = {'criteriaType': 'combined',
            #          'textCriteria': [{'paramType': 'textSearch',
            #                            'searchToken': element_code,
            #                            'matchAgainst': 'code',
            #                            'operator': 'equals'}]}
            #payload = json.dumps(params)
            #r = requests.post(nse_species_search_url, data=payload, headers=headers)
            #content = json.loads(r.content)
            #results = content['results']

            # get attributes from NSE Taxon API
            EBARUtils.displayMessage(messages, 'Getting attributes from NatureServe Explorer Taxon API')
            result = requests.get(nse_taxon_search_url + element_global_id)
            results = json.loads(result.content)
            pdf_html = pdf_html.replace('[NSE.grank]', results['grank'])
            pdf_html = pdf_html.replace('[NSE.grankReviewDate]',
                                                  EBARUtils.extractDate(results['grankReviewDate']).strftime('%B %d, %Y'))
            ca_rank = 'None'
            us_rank = 'None'
            mx_rank = 'None'
            ca_subnational_list = []
            us_subnational_list = []
            mx_subnational_list = []
            for key in results:
                if key == 'elementNationals':
                    for en in results[key]:
                        if en['nation']['isoCode'] == 'CA':
                            reviewed = ''
                            if en['nrankReviewYear']:
                                reviewed = ' (reviewed ' + str(en['nrankReviewYear']) + ')'
                            ca_rank = en['nrank'] + reviewed
                            for esn in en['elementSubnationals']:
                                ca_subnational_list.append(esn['subnation']['subnationCode'] + '=' + esn['srank'])
                        if en['nation']['isoCode'] == 'US':
                            reviewed = ''
                            if en['nrankReviewYear']:
                                reviewed = ' (reviewed ' + str(en['nrankReviewYear']) + ')'
                            us_rank = en['nrank'] + reviewed
                            for esn in en['elementSubnationals']:
                                us_subnational_list.append(esn['subnation']['subnationCode'] + '=' + esn['srank'])
                        if en['nation']['isoCode'] == 'MX':
                            reviewed = ''
                            if en['nrankReviewYear']:
                                reviewed = ' (reviewed ' + str(en['nrankReviewYear']) + ')'
                            mx_rank = en['nrank'] + reviewed
                            for esn in en['elementSubnationals']:
                                mx_subnational_list.append(esn['subnation']['subnationCode'] + '=' + esn['srank'])
            pdf_html = pdf_html.replace('[NSE.CARank]', ca_rank)
            pdf_html = pdf_html.replace('[NSE.USRank]', us_rank)
            pdf_html = pdf_html.replace('[NSE.MXRank]', mx_rank)
            ca_subnational_ranks = 'None'
            if len(ca_subnational_list) > 0:
                ca_subnational_list.sort()
                ca_subnational_ranks = ', '.join(ca_subnational_list)
            pdf_html = pdf_html.replace('[NSE.CASubnationalRanks]', ca_subnational_ranks)
            us_subnational_ranks = 'None'
            if len(us_subnational_list) > 0:
                us_subnational_list.sort()
                us_subnational_ranks = ', '.join(us_subnational_list)
            pdf_html = pdf_html.replace('[NSE.USSubnationalRanks]', us_subnational_ranks)
            mx_subnational_ranks = 'None'
            if len(mx_subnational_list) > 0:
                mx_subnational_list.sort()
                mx_subnational_ranks = ', '.join(mx_subnational_list)
            pdf_html = pdf_html.replace('[NSE.MXSubnationalRanks]', mx_subnational_ranks)
            sara_status = 'None'
            if results['speciesGlobal']['saraStatus']:
                sara_status = results['speciesGlobal']['saraStatus']
                if results['speciesGlobal']['saraStatusDate']:
                    sara_status += ' (' + results['speciesGlobal']['saraStatusDate'] + ')'
            pdf_html = pdf_html.replace('[NSE.saraStatus]', sara_status)
            cosewic_status = 'None'
            if results['speciesGlobal']['interpretedCosewic']:
                cosewic_status = results['speciesGlobal']['interpretedCosewic']
                if results['speciesGlobal']['cosewicDate']:
                    cosewic_status += ' (' + results['speciesGlobal']['cosewicDate'] + ')'
            pdf_html = pdf_html.replace('[NSE.cosewicStatus]', cosewic_status)
            esa_status = 'None'
            if results['speciesGlobal']['interpretedUsesa']:
                esa_status = results['speciesGlobal']['interpretedUsesa']
                if results['speciesGlobal']['usesaDate']:
                    esa_status += ' (' + results['speciesGlobal']['usesaDate'] + ')'
            pdf_html = pdf_html.replace('[NSE.esaStatus]', esa_status)

        # generate jpg
        if param_pdf == 'true' or param_jpg == 'true':
            EBARUtils.displayMessage(messages, 'Generating JPG map')
            aprx = arcpy.mp.ArcGISProject(arcgis_pro_project)
            map = aprx.listMaps('range map landscape topographic')[0]
            polygon_layer = map.listLayers('ecoshaperangemap')[0]
            polygon_layer.definitionQuery = 'rangemapid = ' + str(param_range_map_id)
            table_layer = map.listTables('rangemap')[0]
            table_layer.definitionQuery = 'rangemapid = ' + str(param_range_map_id)
            layout = aprx.listLayouts('range map landscape topographic')[0]
            map_frame = layout.listElements('mapframe_element')[0]
            extent = map_frame.getLayerExtent(polygon_layer, False, True)
            x_buffer = (extent.XMax - extent.XMin) / 20.0
            y_buffer = (extent.YMax - extent.YMin) / 20.0
            buffered_extent = arcpy.Extent(extent.XMin - x_buffer,
                                           extent.YMin - y_buffer,
                                           extent.XMax + x_buffer,
                                           extent.YMax + y_buffer)
            map_frame.camera.setExtent(buffered_extent)
            if range_map_scope == 'National':
                element_global_id += 'N'
            layout.exportToJPEG(download_folder + '/EBAR' + element_global_id + '.jpg', 300,
                                clip_to_elements=True)

        # generate pdf
        if param_pdf == 'true':
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
                'cookie': [
                    ('cookie-name1', 'cookie-value1'),
                    ('cookie-name2', 'cookie-value2'),
                ],
                'no-outline': None
            }
            pdfkit.from_string(pdf_html, download_folder + '/EBAR' + element_global_id + '.pdf', pdf_options)

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
    param_range_map_id.value = '615'
    param_pdf = arcpy.Parameter()
    param_pdf.value = 'true'
    param_jpg = arcpy.Parameter()
    param_jpg.value = 'true'
    param_spatial = arcpy.Parameter()
    param_spatial.value = 'true'
    parameters = [param_range_map_id, param_pdf, param_jpg, param_spatial]
    prm.RunPublishRangeMapTool(parameters, None)
