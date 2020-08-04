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
import os
import shutil
import time
import csv
import zipfile

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
        resources_folder = 'C:/GIS/EBAR/EBARTools/resources'
        arcgis_pro_project = resources_folder + '/EBARMapLayouts.aprx'
        pdf_template_file = resources_folder + '/pdf_template.html'
        reviewers_by_taxa_file = 'C:/Users/rgree/OneDrive/EBAR/EBAR Maps/ReviewersByTaxa.txt'
        temp_folder = 'C:/GIS/EBAR/pub'
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

            # headers 
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
                    nse_url = 'https://explorer.natureserve.org/Taxon/ELEMENT_GLOBAL.2.' + element_global_id
                    pdf_html = pdf_html.replace('[NSE2.0_URL]', nse_url)
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
            try:
                results = json.loads(result.content)
            except:
                EBARUtils.displayMessage(messages, 'WARNING: ELEMENT_GLOBAL_ID not found - ' + element_global_id)
                return
            g_rank = results['grank']
            pdf_html = pdf_html.replace('[NSE.grank]', g_rank)
            reviewed = ''
            if results['grankReviewDate']:
                reviewed = ' (reviewed ' + EBARUtils.extractDate(results['grankReviewDate']).strftime('%B %d, %Y') + \
                    ')'
            pdf_html = pdf_html.replace('[NSE.grankReviewDate]', reviewed)
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

        # generate jpg and insert into pdf template
        if param_pdf == 'true' or param_jpg == 'true':
            EBARUtils.displayMessage(messages, 'Generating JPG map')
            aprx = arcpy.mp.ArcGISProject(arcgis_pro_project)
            map = aprx.listMaps('range map landscape terrain')[0]
            polygon_layer = map.listLayers('ecoshaperangemap')[0]
            polygon_layer.definitionQuery = 'rangemapid = ' + str(param_range_map_id)
            table_layer = map.listTables('rangemap')[0]
            table_layer.definitionQuery = 'rangemapid = ' + str(param_range_map_id)
            layout = aprx.listLayouts('range map landscape terrain')[0]
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
        pdf_html = pdf_html.replace('[map_image]', download_folder + '/EBAR' + element_global_id + '.jpg')

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
            # make folder, copy in static resources and EBAR pdf
            EBARUtils.displayMessage(messages, 'Creating ZIP folder and copying files')
            zip_folder = temp_folder + '/EBAR' + element_global_id
            if os.path.exists(zip_folder):
                shutil.rmtree(zip_folder)
                # pause before trying to make the dir
                time.sleep(1)
            os.mkdir(zip_folder)
            shutil.copyfile(resources_folder + '/Readme.txt', zip_folder + '/Readme.txt')
            shutil.copyfile(resources_folder + '/EBARMethods.pdf', zip_folder + '/EBARMethods.pdf')
            shutil.copyfile(resources_folder + '/Jurisdiction.csv', zip_folder + '/Jurisdiction.csv')
            shutil.copyfile(download_folder + '/EBAR' + element_global_id + '.pdf',
                            zip_folder + '/EBAR' + element_global_id + '.pdf')

            # export range map, with biotics/species additions
            EBARUtils.displayMessage(messages, 'Exporting RangeMap to CSV')
            arcpy.MakeTableView_management(ebar_feature_service + '/11', 'range_map_view' + param_range_map_id,
                                           'RangeMapID = ' + param_range_map_id)
            arcpy.AddJoin_management('range_map_view' + param_range_map_id, 'SpeciesID', ebar_feature_service + '/4', 'SpeciesID',
                                     'KEEP_COMMON')
            arcpy.AddJoin_management('range_map_view' + param_range_map_id, 'SpeciesID', ebar_feature_service + '/19', 'SpeciesID',
                                     'KEEP_COMMON')
            field_mappings = arcpy.FieldMappings()
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id, 'L11RangeMap.RangeMapID', 'RangeMapID',
                                                                'LONG'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id, 'L11RangeMap.RangeVersion',
                                                                'RangeVersion', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id, 'L11RangeMap.RangeStage', 'RangeStage',
                                                                'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id, 'L11RangeMap.RangeDate', 'RangeDate',
                                                                'DATE'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id, 'L11RangeMap.RangeMapScope',
                                                                'RangeMapScope', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id, 'L11RangeMap.RangeMetadata',
                                                                'RangeMetadata', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id, 'L11RangeMap.RangeMapNotes',
                                                                'RangeMapNotes', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id, 'L11RangeMap.RangeMapComments',
                                                                'RangeMapComments', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id, 'L11RangeMap.SynonymsUsed',
                                                                'SynonymsUsed', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id,
                                                                'L4BIOTICS_ELEMENT_NATIONAL.ELEMENT_NATIONAL_ID',
                                                                'ELEMENT_NATIONAL_ID', 'LONG'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id,
                                                                'L4BIOTICS_ELEMENT_NATIONAL.ELEMENT_GLOBAL_ID',
                                                                'ELEMENT_GLOBAL_ID', 'LONG'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id,
                                                                'L4BIOTICS_ELEMENT_NATIONAL.ELEMENT_CODE',
                                                                'ELEMENT_CODE', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id,
                                                                'L4BIOTICS_ELEMENT_NATIONAL.CATEGORY', 'CATEGORY',
                                                                'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id,
                                                                'L4BIOTICS_ELEMENT_NATIONAL.TAX_GROUP', 'TAX_GROUP',
                                                                'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id,
                                                                'L4BIOTICS_ELEMENT_NATIONAL.FAMILY_COM', 'FAMILY_COM',
                                                                'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id,
                                                                'L4BIOTICS_ELEMENT_NATIONAL.GENUS', 'GENUS', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id,
                                                                'L4BIOTICS_ELEMENT_NATIONAL.PHYLUM', 'PHYLUM', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id,
                                                                'L4BIOTICS_ELEMENT_NATIONAL.CA_NNAME_LEVEL',
                                                                'CA_NNAME_LEVEL', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id,
                                                                'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_SCIENTIFIC_NAME',
                                                                'NATIONAL_SCIENTIFIC_NAME', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id,
                                                                'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_ENGL_NAME',
                                                                'NATIONAL_ENGL_NAME', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id,
                                                                'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_FR_NAME',
                                                                'NATIONAL_FR_NAME', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id,
                                                                'L4BIOTICS_ELEMENT_NATIONAL.COSEWIC_NAME',
                                                                'COSEWIC_NAME', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_view' + param_range_map_id, 'L19Species.ENDEMISM_TYPE',
                                                                'ENDEMISM_TYPE', 'TEXT'))
            arcpy.TableToTable_conversion('range_map_view' + param_range_map_id, zip_folder, 'temp.csv', field_mapping=field_mappings)
            # add NSE Taxon API fields
            with open(zip_folder + '/temp.csv','r') as csv_input:
                with open(zip_folder + '/RangeMap.csv', 'w') as csv_output:
                    writer = csv.writer(csv_output, lineterminator='\n')
                    reader = csv.reader(csv_input)
                    all = []
                    row = next(reader)
                    row[0] = 'objectid'
                    row.append('GRANK')
                    row.append('NRANK_CA')
                    row.append('SRANKS_CA')
                    row.append('NRANK_US')
                    row.append('SRANKS_US')
                    row.append('NRANK_MX')
                    row.append('SRANKS_MX')
                    row.append('SARA_STATUS')
                    row.append('COSEWIC_STATUS')
                    row.append('ESA_STATUS')
                    all.append(row)
                    for row in reader:
                        row[0] = param_range_map_id
                        row.append(g_rank)
                        row.append(ca_rank)
                        row.append(ca_subnational_ranks)
                        row.append(us_rank)
                        row.append(us_subnational_ranks)
                        row.append(mx_rank)
                        row.append(mx_subnational_ranks)
                        row.append(sara_status)
                        row.append(cosewic_status)
                        row.append(esa_status)
                        all.append(row)
                    writer.writerows(all)
            arcpy.Delete_management(zip_folder + '/temp.csv')

            # export range map ecoshapes
            EBARUtils.displayMessage(messages, 'Exporting RangeMapEcoshape records to CSV')
            arcpy.MakeTableView_management(ebar_feature_service + '/12', 'range_map_ecoshape_view' + param_range_map_id,
                                           'RangeMapID = ' + param_range_map_id)
            field_mappings = arcpy.FieldMappings()
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_ecoshape_view' + param_range_map_id, 'RangeMapID', 'RangeMapID',
                                                                'LONG'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_ecoshape_view' + param_range_map_id, 'EcoshapeID', 'EcoshapeID',
                                                                'LONG'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_ecoshape_view' + param_range_map_id, 'Presence', 'Presence',
                                                                'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('range_map_ecoshape_view' + param_range_map_id, 'RangeMapEcoshapeNotes',
                                                                'RangeMapEcoshapeNotes', 'TEXT'))
            arcpy.TableToTable_conversion('range_map_ecoshape_view' + param_range_map_id, zip_folder, 'RangeMapEcoshape.csv',
                                          field_mapping=field_mappings)
            arcpy.Delete_management(zip_folder + '/RangeMapEcoshape.csv.xml')
            arcpy.Delete_management(zip_folder + '/schema.ini')
            arcpy.Delete_management(zip_folder + '/info')

            # export range map ecoshapes
            EBARUtils.displayMessage(messages, 'Exporting Ecoshape polygons to shapefile')
            arcpy.MakeFeatureLayer_management(ebar_feature_service + '/3', 'ecoshape_layer' + param_range_map_id)
            arcpy.AddJoin_management('ecoshape_layer' + param_range_map_id, 'EcoshapeID', 'range_map_ecoshape_view' + param_range_map_id, 'EcoshapeID')
            field_mappings = arcpy.FieldMappings()
            field_mappings.addFieldMap(EBARUtils.createFieldMap('ecoshape_layer' + param_range_map_id, 'L3Ecoshape.EcoshapeID',
                                                                'EcoshapeID', 'LONG'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('ecoshape_layer' + param_range_map_id, 'L3Ecoshape.JurisdictionID',
                                                                'JurisID', 'LONG'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('ecoshape_layer' + param_range_map_id, 'L3Ecoshape.EcoshapeName',
                                                                'EcoName', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('ecoshape_layer' + param_range_map_id, 'L3Ecoshape.ParentEcoregion',
                                                                'ParentEco', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('ecoshape_layer' + param_range_map_id, 'L3Ecoshape.ParentEcoregionFR',
                                                                'ParentEcoF', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('ecoshape_layer' + param_range_map_id, 'L3Ecoshape.Ecozone',
                                                                'Ecozone', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('ecoshape_layer' + param_range_map_id, 'L3Ecoshape.EcozoneFR',
                                                                'EcozoneFR', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('ecoshape_layer' + param_range_map_id, 'L3Ecoshape.MosaicVersion',
                                                                'MosaicVer', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('ecoshape_layer' + param_range_map_id, 'L3Ecoshape.TerrestrialArea',
                                                                'TerrArea', 'DOUBLE'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('ecoshape_layer' + param_range_map_id, 'L3Ecoshape.TotalArea',
                                                                'TotalArea', 'DOUBLE'))
            arcpy.FeatureClassToFeatureClass_conversion('ecoshape_layer' + param_range_map_id, zip_folder, 'Ecoshape.shp',
                                                        field_mapping=field_mappings)
            # export range map overview ecoshapes
            EBARUtils.displayMessage(messages, 'Exporting EcoshapeOverview polygons to shapefile')
            arcpy.MakeFeatureLayer_management(ebar_feature_service + '/22', 'ecoshape_overview_layer' + param_range_map_id)
            arcpy.AddJoin_management('ecoshape_overview_layer' + param_range_map_id, 'EcoshapeID', 'range_map_ecoshape_view' + param_range_map_id, 'EcoshapeID')
            field_mappings = arcpy.FieldMappings()
            field_mappings.addFieldMap(EBARUtils.createFieldMap('ecoshape_overview_layer' + param_range_map_id,
                                                                'L22EcoshapeOverview.EcoshapeID',
                                                                'EcoshapeID', 'LONG'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('ecoshape_overview_layer' + param_range_map_id,
                                                                'L22EcoshapeOverview.JurisdictionID',
                                                                'JurisID', 'LONG'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('ecoshape_overview_layer' + param_range_map_id,
                                                                'L22EcoshapeOverview.EcoshapeName',
                                                                'EcoName', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('ecoshape_overview_layer' + param_range_map_id,
                                                                'L22EcoshapeOverview.ParentEcoregion',
                                                                'ParentEco', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('ecoshape_overview_layer' + param_range_map_id,
                                                                'L22EcoshapeOverview.ParentEcoregionFR',
                                                                'ParentEcoF', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('ecoshape_overview_layer' + param_range_map_id,
                                                                'L22EcoshapeOverview.Ecozone',
                                                                'Ecozone', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('ecoshape_overview_layer' + param_range_map_id,
                                                                'L22EcoshapeOverview.EcozoneFR',
                                                                'EcozoneFR', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('ecoshape_overview_layer' + param_range_map_id,
                                                                'L22EcoshapeOverview.MosaicVersion',
                                                                'MosaicVer', 'TEXT'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('ecoshape_overview_layer' + param_range_map_id,
                                                                'L22EcoshapeOverview.TerrestrialArea',
                                                                'TerrArea', 'DOUBLE'))
            field_mappings.addFieldMap(EBARUtils.createFieldMap('ecoshape_overview_layer' + param_range_map_id,
                                                                'L22EcoshapeOverview.TotalArea',
                                                                'TotalArea', 'DOUBLE'))
            arcpy.FeatureClassToFeatureClass_conversion('ecoshape_overview_layer' + param_range_map_id, zip_folder, 'EcoshapeOverview.shp',
                                                        field_mapping=field_mappings)

            # embed metadata
            EBARUtils.displayMessage(messages, 'Embedding metadata')
            # common
            new_md = arcpy.metadata.Metadata()
            new_md.tags = 'Species Range, NatureServe Canada, Ecosystem-based Automated Range'
            new_md.description = 'See EBAR' + element_global_id + '.pdf for map and additional metadata, and ' + \
                'EBARMethods.pdf for additional details. <a href="' + nse_url + '">Go to ' + \
                'NatureServer Explorer</a> for information about the species.'
            new_md.credits = '© NatureServe Canada ' + str(datetime.datetime.now().year)
            new_md.accessConstraints = 'Publicly shareable under CC BY 4.0 (<a href="https://creativecommons.org/licenses/by/4.0/">https://creativecommons.org/licenses/by/4.0/</a>)'
            # ecoshape
            ecoshape_md = arcpy.metadata.Metadata(zip_folder + '/Ecoshape.shp')
            new_md.title = 'EBAR Ecoshape.shp'
            new_md.summary = 'Polygons shapefile of original ecoshapes for EBAR for selected species'
            ecoshape_md.copy(new_md)
            ecoshape_md.save()
            # ecoshape overview
            ecoshape_overview_md = arcpy.metadata.Metadata(zip_folder + '/EcoshapeOverview.shp')
            new_md.title = 'EBAR EcoshapeOverview.shp'
            new_md.summary = 'Polygons shapefile of generalized ecoshapes for EBAR for selected species'
            ecoshape_overview_md.copy(new_md)
            ecoshape_overview_md.save()
            # range map
            range_map_md = arcpy.metadata.Metadata(zip_folder + '/RangeMap.csv')
            new_md.title = 'EBAR RangeMap.csv'
            new_md.summary = 'Table of species and range attributes for EBAR for selected species'
            range_map_md.copy(new_md)
            range_map_md.save()
            # range map ecoshape
            range_map_ecoshape_md = arcpy.metadata.Metadata(zip_folder + '/RangeMapEcoshape.csv')
            new_md.title = 'EBAR RangeMapEcoshape.csv'
            new_md.summary = 'Table of per-ecoshape attributes for EBAR for selected species'
            range_map_ecoshape_md.copy(new_md)
            range_map_ecoshape_md.save()
            # jurisdiction
            jurisdiction_md = arcpy.metadata.Metadata(zip_folder + '/Jurisdiction.csv')
            new_md.title = 'EBAR Jurisdiction.csv'
            new_md.summary = 'Table of Jurisdictions'
            jurisdiction_md.copy(new_md)
            jurisdiction_md.save()

            # update ArcGIS Pro template
            EBARUtils.displayMessage(messages, 'Updating ArcGIS Pro template')
            shutil.copyfile(resources_folder + '/EBARTemplate.aprx',
                            zip_folder + '/EBAR' + element_global_id + '.aprx')
            aprx = arcpy.mp.ArcGISProject(zip_folder + '/EBAR' + element_global_id + '.aprx')
            aprx.homeFolder = zip_folder
            #arcpy.CreateFileGDB_management(zip_folder, 'default.gdb')
            #aprx.defaultGeodatabase = zip_folder + '/default.gdb'
            #shutil.copyfile(resources_folder + '/default.tbx', zip_folder + '/default.tbx')
            #aprx.defaultToolbox = zip_folder + '/default.tbx'
            map = aprx.listMaps('EBARTemplate')[0]
            map.name = 'EBAR' + element_global_id
            ecoshape_overview_layer =  map.listLayers('EBARTemplateEcoshapeOverview')[0]
            ecoshape_overview_layer_md = ecoshape_overview_layer.metadata
            new_md.title = 'EBAR EcoshapeOverview.shp'
            new_md.summary = 'Polygons shapefile of generalized ecoshapes for EBAR for selected species'
            ecoshape_overview_layer_md.copy(new_md)
            ecoshape_overview_layer_md.save()
            ecoshape_overview_layer.name = 'EBAR' + element_global_id + 'EcoshapeOverview'
            ecoshape_overview_layer.saveACopy(zip_folder + '/EBAR' + element_global_id + 'EcoshapeOverview.lyrx')
            ecoshape_layer =  map.listLayers('EBARTemplateEcoshape')[0]
            ecoshape_layer_md = ecoshape_overview_layer.metadata
            new_md.title = 'EBAR Ecoshape.shp'
            new_md.summary = 'Polygons shapefile of original ecoshapes for EBAR for selected species'
            ecoshape_layer_md.copy(new_md)
            ecoshape_layer_md.save()
            ecoshape_layer.name = 'EBAR' + element_global_id + 'Ecoshape'
            ecoshape_layer.saveACopy(zip_folder + '/EBAR' + element_global_id + 'Ecoshape.lyrx')
            range_map_table = map.listTables('EBARTemplateRangeMap')[0]
            range_map_table.name = 'EBAR' + element_global_id + 'RangeMap'
            range_map_ecoshape_table = map.listTables('EBARTemplateRangeMapEcoshape')[0]
            range_map_ecoshape_table.name = 'EBAR' + element_global_id + 'RangeMapEcoshape'
            aprx.save()

            # copy ArcGIS Pro template
            EBARUtils.displayMessage(messages, 'Copying ArcMap template')
            shutil.copyfile(resources_folder + '/EBAR.mxd', zip_folder + '/EBAR' + element_global_id + '.mxd')
            shutil.copyfile(resources_folder + '/EcoshapeOverview.lyr',
                            zip_folder + '/EBAR' + element_global_id + 'EcoshapeOverview.lyr')
            shutil.copyfile(resources_folder + '/Ecoshape.lyr',
                            zip_folder + '/EBAR' + element_global_id + 'Ecoshape.lyr')

            # zip
            EBARUtils.displayMessage(messages, 'Creating ZIP')
            os.chdir(temp_folder)
            zipf = zipfile.ZipFile(download_folder + '/EBAR' + element_global_id + '.zip', 'w', zipfile.ZIP_DEFLATED)
            for root, dirs, files in os.walk(zip_folder):
                for file in files:
                    if file[-5:] != '.lock':
                        #zipf.write(os.path.join(root, file))
                        zipf.write('EBAR' + element_global_id + '/' + file)
            #shutil.rmtree(zip_folder)

        # cleanup
        if param_jpg != 'true':
            pass

        return


# controlling process
if __name__ == '__main__':
    prm = PublishRangeMapTool()
    # 617, 618, 619, 620, 621, 45, 51, 52, 50, 56, 53, 237, 234, 680, 447, 448, 449
    # 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 608, 633, 634, 635, 636, 638, 637, 639, 640, 643, 644, 645, 646, 647, 648
    batch_ids = [124]
    for id in batch_ids:
        # hard code parameters for debugging
        param_range_map_id = arcpy.Parameter()
        param_range_map_id.value = str(id)
        param_pdf = arcpy.Parameter()
        param_pdf.value = 'true'
        param_jpg = arcpy.Parameter()
        param_jpg.value = 'true'
        param_spatial = arcpy.Parameter()
        param_spatial.value = 'true'
        parameters = [param_range_map_id, param_pdf, param_jpg, param_spatial]
        prm.RunPublishRangeMapTool(parameters, None)
