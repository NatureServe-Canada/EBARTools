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
import arcpy.mp
import arcpy.metadata
import datetime
import pdfkit
import requests
import json
import shutil
import urllib


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
        #resources_folder = 'C:/GIS/EBAR/EBARTools/resources'
        arcgis_pro_project = EBARUtils.resources_folder + '/EBARMapLayouts.aprx'
        pdf_template_file = EBARUtils.resources_folder + '/pdf_template.html'
        #reviewers_by_taxa_file = 'C:/Users/rgree/OneDrive/EBAR/EBAR Maps/ReviewersByTaxa.txt'
        reviewers_by_taxa_link = 'https://onedrive.live.com/download?cid=AAAAAE977404FA3B&resid=AAAAAE977404FA3B' + \
            '%21442509&authkey=APQx60zQOjRu23A'
        #temp_folder = 'C:/GIS/EBAR/temp'
        #download_folder = 'C:/GIS/EBAR/pub/download'
        #download_folder = 'F:/download'
        nse_species_search_url = 'https://explorer.natureserve.org/api/data/search'
        nse_taxon_search_url = 'https://explorer.natureserve.org/api/data/taxon/ELEMENT_GLOBAL.'

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
        pdf_html = pdf_html.replace('[logo_image]', EBARUtils.resources_folder + '/nscanada_inline_copy.png')
        pdf_html = pdf_html.replace('[species_header_image]', EBARUtils.resources_folder + '/species_header.png')
        pdf_html = pdf_html.replace('[rank_status_header_image]', EBARUtils.resources_folder +
                                                '/rank_status_header.png')
        pdf_html = pdf_html.replace('[range_map_header_image]', EBARUtils.resources_folder +
                                                '/range_map_header.png')
        pdf_html = pdf_html.replace('[reviews_header_image]', EBARUtils.resources_folder + '/reviews_header.png')
        pdf_html = pdf_html.replace('[credits_header_image]', EBARUtils.resources_folder + '/credits_header.png')

        # get range map data from database
        EBARUtils.displayMessage(messages, 'Getting RangeMap data from database')
        species_id = None
        range_map_scope = None
        arcpy.MakeTableView_management(EBARUtils.ebar_feature_service + '/11', 'range_map_view',
                                       'RangeMapID = ' + param_range_map_id)
        with arcpy.da.SearchCursor('range_map_view',
                                    ['SpeciesID', 'RangeVersion', 'RangeStage', 'RangeDate', 'RangeMapScope',
                                    'RangeMapNotes', 'RangeMetadata', 'RangeMapComments']) as cursor:
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
        #element_global_id = None
        #element_code = None
        #global_unique_id = None
        arcpy.MakeTableView_management(EBARUtils.ebar_feature_service + '/4', 'biotics_view',
                                       'SpeciesID = ' + str(species_id))
        with arcpy.da.SearchCursor('biotics_view', 
                                    ['NATIONAL_SCIENTIFIC_NAME', 'NATIONAL_ENGL_NAME', 'NATIONAL_FR_NAME',
                                    'ELEMENT_NATIONAL_ID', 'ELEMENT_GLOBAL_ID', 'ELEMENT_CODE', 
                                    'GLOBAL_UNIQUE_IDENTIFIER', 'G_JURIS_ENDEM_DESC']) as cursor:
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
                global_unique_id = row['GLOBAL_UNIQUE_IDENTIFIER']
                global_unique_id = global_unique_id.replace('-', '.')
                #nse_url = 'https://explorer.natureserve.org/Taxon/ELEMENT_GLOBAL.2.' + element_global_id
                nse_url = 'https://explorer.natureserve.org/Taxon/ELEMENT_GLOBAL.' + global_unique_id
                pdf_html = pdf_html.replace('[NSE2.0_URL]', nse_url)
                #endemism = 'None'
                #if row['G_JURIS_ENDEM_DESC']:
                #    endemism = row['G_JURIS_ENDEM_DESC']
                #pdf_html = pdf_html.replace('[BIOTICS_ELEMENT_NATIONAL.G_JURIS_ENDEM_DESC]', endemism)
            del row

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

        # get input references
        EBARUtils.displayMessage(messages, 'Getting InputReferences from database')
        input_references = ''
        arcpy.MakeTableView_management(EBARUtils.ebar_summary_service + '/7', 'citation_view',
                                       'RangeMapID = ' + param_range_map_id)
        with arcpy.da.SearchCursor('citation_view', ['DatasetSourceName', 'DatasetSourceCitation']) as cursor:
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
        #reviewers = open(reviewers_by_taxa_file)
        reviewers = urllib.request.urlopen(reviewers_by_taxa_link).read().decode('ansi')
        #pdf_html = pdf_html.replace('[ReviewersByTaxa]', reviewers.read())
        #reviewers.close()
        pdf_html = pdf_html.replace('[ReviewersByTaxa]', reviewers)

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
        results = None
        try:
            result = requests.get(nse_taxon_search_url + global_unique_id)
            results = json.loads(result.content)
        except:
            EBARUtils.displayMessage(messages, 'WARNING: could not find ELEMENT_GLOBAL_ID ' + element_global_id +
                                        ' or other NSE Taxon API issue for RangeMapID ' + param_range_map_id)
        attribute_dict = {}
        attribute_dict['reviewed_grank'] = ''
        attribute_dict['ca_rank'] = 'None'
        attribute_dict['us_rank'] = 'None'
        attribute_dict['mx_rank'] = 'None'
        attribute_dict['ca_subnational_list'] = []
        attribute_dict['us_subnational_list'] = []
        attribute_dict['mx_subnational_list'] = []
        attribute_dict['ca_subnational_ranks'] = 'None'
        attribute_dict['us_subnational_ranks'] = 'None'
        attribute_dict['mx_subnational_ranks'] = 'None'
        attribute_dict['sara_status'] = 'None'
        attribute_dict['cosewic_status'] = 'None'
        attribute_dict['esa_status'] = 'None'
        if results:
            # get from Taxon API
            attribute_dict['g_rank'] = results['grank']
            if results['grankReviewDate']:
                attribute_dict['reviewed_grank'] = ' (reviewed ' + \
                    EBARUtils.extractDate(results['grankReviewDate']).strftime('%B %d, %Y') + ')'
            for key in results:
                if key == 'elementNationals':
                    for en in results[key]:
                        if en['nation']['isoCode'] == 'CA':
                            reviewed = ''
                            if en['nrankReviewYear']:
                                reviewed = ' (reviewed ' + str(en['nrankReviewYear']) + ')'
                            attribute_dict['ca_rank'] = en['nrank'] + reviewed
                            for esn in en['elementSubnationals']:
                                attribute_dict['ca_subnational_list'].append(esn['subnation']['subnationCode'] + \
                                    '=' + esn['srank'])
                        if en['nation']['isoCode'] == 'US':
                            reviewed = ''
                            if en['nrankReviewYear']:
                                reviewed = ' (reviewed ' + str(en['nrankReviewYear']) + ')'
                            attribute_dict['us_rank'] = en['nrank'] + reviewed
                            for esn in en['elementSubnationals']:
                                attribute_dict['us_subnational_list'].append(esn['subnation']['subnationCode'] + \
                                    '=' + esn['srank'])
                        if en['nation']['isoCode'] == 'MX':
                            reviewed = ''
                            if en['nrankReviewYear']:
                                reviewed = ' (reviewed ' + str(en['nrankReviewYear']) + ')'
                            attribute_dict['mx_rank'] = en['nrank'] + reviewed
                            for esn in en['elementSubnationals']:
                                attribute_dict['mx_subnational_list'].append(esn['subnation']['subnationCode'] + \
                                    '=' + esn['srank'])
            if results['speciesGlobal']['saraStatus']:
                attribute_dict['sara_status'] = results['speciesGlobal']['saraStatus']
                if results['speciesGlobal']['saraStatusDate']:
                    attribute_dict['sara_status'] += ' (' + \
                        EBARUtils.extractDate(results['speciesGlobal']['saraStatusDate']).strftime('%B %d, %Y') + ')'
            if results['speciesGlobal']['cosewic']:
                if results['speciesGlobal']['cosewic']['cosewicDescEn']:
                    attribute_dict['cosewic_status'] = results['speciesGlobal']['cosewic']['cosewicDescEn']
                    if results['speciesGlobal']['cosewicDate']:
                        attribute_dict['cosewic_status'] += ' (' + \
                            EBARUtils.extractDate(results['speciesGlobal']['cosewicDate']).strftime('%B %d, %Y') + ')'
            if results['speciesGlobal']['interpretedUsesa']:
                attribute_dict['esa_status'] = results['speciesGlobal']['interpretedUsesa']
                if results['speciesGlobal']['usesaDate']:
                    attribute_dict['esa_status'] += ' (' + \
                        EBARUtils.extractDate(results['speciesGlobal']['usesaDate']).strftime('%B %d, %Y') + ')'
        else:
            # get from BIOTICS table
            attribute_dict['us_rank'] = 'Not available'
            attribute_dict['mx_rank'] = 'Not available'
            attribute_dict['ca_subnational_ranks'] = 'Not available'
            attribute_dict['us_subnational_ranks'] = 'Not available'
            attribute_dict['mx_subnational_ranks'] = 'Not available'
            attribute_dict['esa_status'] = 'Not available'
            with arcpy.da.SearchCursor('biotics_view', 
                                        ['G_RANK', 'G_RANK_REVIEW_DATE', 'N_RANK', 'N_RANK_REVIEW_DATE', 
                                        'COSEWIC_STATUS', 'SARA_STATUS']) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    attribute_dict['g_rank'] = row['G_RANK']
                    if row['G_RANK_REVIEW_DATE']:
                        attribute_dict['reviewed_grank'] = ' (reviewed ' + \
                            row['G_RANK_REVIEW_DATE'].strftime('%B %d, %Y') + ')'
                    attribute_dict['ca_rank'] = row['N_RANK']
                    if row['N_RANK_REVIEW_DATE']:
                        attribute_dict['ca_rank'] += ' (reviewed ' + \
                            row['N_RANK_REVIEW_DATE'].strftime('%B %d, %Y') + ')'
                    if row['COSEWIC_STATUS']:
                        attribute_dict['cosewic_status'] = row['COSEWIC_STATUS']
                    if row['SARA_STATUS']:
                        attribute_dict['sara_status'] = row['SARA_STATUS']
        # update template
        pdf_html = pdf_html.replace('[NSE.grank]', attribute_dict['g_rank'])
        pdf_html = pdf_html.replace('[NSE.grankReviewDate]', attribute_dict['reviewed_grank'])
        pdf_html = pdf_html.replace('[NSE.CARank]', attribute_dict['ca_rank'])
        pdf_html = pdf_html.replace('[NSE.USRank]', attribute_dict['us_rank'])
        pdf_html = pdf_html.replace('[NSE.MXRank]', attribute_dict['mx_rank'])
        if len(attribute_dict['ca_subnational_list']) > 0:
            attribute_dict['ca_subnational_list'].sort()
            attribute_dict['ca_subnational_ranks'] = ', '.join(attribute_dict['ca_subnational_list'])
        pdf_html = pdf_html.replace('[NSE.CASubnationalRanks]', attribute_dict['ca_subnational_ranks'])
        if len(attribute_dict['us_subnational_list']) > 0:
            attribute_dict['us_subnational_list'].sort()
            attribute_dict['us_subnational_ranks'] = ', '.join(attribute_dict['us_subnational_list'])
        pdf_html = pdf_html.replace('[NSE.USSubnationalRanks]', attribute_dict['us_subnational_ranks'])
        if len(attribute_dict['mx_subnational_list']) > 0:
            attribute_dict['mx_subnational_list'].sort()
            attribute_dict['mx_subnational_ranks'] = ', '.join(attribute_dict['mx_subnational_list'])
        pdf_html = pdf_html.replace('[NSE.MXSubnationalRanks]', attribute_dict['mx_subnational_ranks'])
        pdf_html = pdf_html.replace('[NSE.saraStatus]', attribute_dict['sara_status'])
        pdf_html = pdf_html.replace('[NSE.cosewicStatus]', attribute_dict['cosewic_status'])
        pdf_html = pdf_html.replace('[NSE.esaStatus]', attribute_dict['esa_status'])

        # generate jpg and insert into pdf template
        EBARUtils.displayMessage(messages, 'Generating JPG map')
        aprx = arcpy.mp.ArcGISProject(arcgis_pro_project)
        map = aprx.listMaps('range map landscape terrain')[0]
        polygon_layer = map.listLayers('ecoshaperangemap')[0]
        polygon_layer.definitionQuery = 'rangemapid = ' + param_range_map_id
        table_layer = map.listTables('rangemap')[0]
        table_layer.definitionQuery = 'rangemapid = ' + param_range_map_id
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
        if range_map_scope == 'Canadian':
            element_global_id += 'N'
        layout.exportToJPEG(EBARUtils.download_folder + '/EBAR' + element_global_id + '.jpg', 300,
                            clip_to_elements=True)
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
            # make folder, copy in static resources and EBAR pdf
            EBARUtils.displayMessage(messages, 'Creating ZIP folder and copying files')
            EBARUtils.createReplaceFolder(EBARUtils.temp_folder + '/EBAR' + element_global_id)
            zip_folder = EBARUtils.temp_folder + '/EBAR' + element_global_id
            EBARUtils.createReplaceFolder(zip_folder)
            shutil.copyfile(EBARUtils.resources_folder + '/Readme.txt', zip_folder + '/Readme.txt')
            shutil.copyfile(EBARUtils.resources_folder + '/EBARMethods.pdf', zip_folder + '/EBARMethods.pdf')
            shutil.copyfile(EBARUtils.resources_folder + '/Jurisdiction.csv', zip_folder + '/Jurisdiction.csv')
            shutil.copyfile(EBARUtils.download_folder + '/EBAR' + element_global_id + '.pdf',
                            zip_folder + '/EBAR' + element_global_id + '.pdf')

            # export range map, with biotics/species additions
            EBARUtils.displayMessage(messages, 'Exporting RangeMap to CSV')
            EBARUtils.ExportRangeMapToCSV('range_map_view' + param_range_map_id, 'RangeMapID = ' + param_range_map_id,
                                           attribute_dict, zip_folder, '/RangeMap.csv')

            # export range map ecoshapes
            EBARUtils.displayMessage(messages, 'Exporting RangeMapEcoshape records to CSV')
            EBARUtils.ExportRangeMapEcoshapesToCSV('range_map_ecoshape_view' + param_range_map_id,
                                                   'RangeMapID = ' + param_range_map_id,
                                                   zip_folder, '/RangeMapEcoshape.csv')

            # export ecoshapes
            EBARUtils.displayMessage(messages, 'Exporting Ecoshape polygons to shapefile')
            EBARUtils.ExportEcoshapesToShapefile('ecoshape_layer' + param_range_map_id,
                                                 'range_map_ecoshape_view' + param_range_map_id, zip_folder, 
                                                 'Ecoshape.shp', )

            # export overview ecoshapes
            EBARUtils.displayMessage(messages, 'Exporting EcoshapeOverview polygons to shapefile')
            EBARUtils.ExportEcoshapeOverviewsToShapefile('ecoshape_overview_layer' + param_range_map_id,
                                                         'range_map_ecoshape_view' + param_range_map_id, zip_folder, 
                                                         'EcoshapeOverview.shp', )

            # embed metadata
            EBARUtils.displayMessage(messages, 'Embedding metadata')
            # common
            new_md = arcpy.metadata.Metadata()
            new_md.tags = 'Species Range, NatureServe Canada, Ecosystem-based Automated Range'
            new_md.description = 'See EBAR' + element_global_id + '.pdf for map and additional metadata, and ' + \
                'EBARMethods.pdf for additional details. <a href="' + nse_url + '">Go to ' + \
                'NatureServer Explorer</a> for information about the species.'
            new_md.credits = '© NatureServe Canada ' + str(datetime.datetime.now().year)
            new_md.accessConstraints = 'Publicly shareable under CC BY 4.0 (<a href=' + \
                '"https://creativecommons.org/licenses/by/4.0/">https://creativecommons.org/licenses/by/4.0/</a>)'
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
            shutil.copyfile(EBARUtils.resources_folder + '/EBARTemplate.aprx',
                            zip_folder + '/EBAR' + element_global_id + '.aprx')
            aprx = arcpy.mp.ArcGISProject(zip_folder + '/EBAR' + element_global_id + '.aprx')
            aprx.homeFolder = zip_folder
            #arcpy.CreateFileGDB_management(zip_folder, 'default.gdb')
            #aprx.defaultGeodatabase = zip_folder + '/default.gdb'
            #shutil.copyfile(EBARUtils.resources_folder + '/default.tbx', zip_folder + '/default.tbx')
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
                                 'Image: https://gis.natureserve.ca/download/EBAR' + element_global_id + '.jpg')
        EBARUtils.displayMessage(messages,
                                 'PDF: https://gis.natureserve.ca/download/EBAR' + element_global_id + '.pdf')
        if param_spatial == 'true':
            EBARUtils.displayMessage(messages,
                                     'GIS Data: https://gis.natureserve.ca/download/EBAR' + element_global_id + '.zip')

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
    # Unpublished batch = 645, 613, 642, 135
    # Batch 1 = 616, 618, 619, 620, 621, 622, 625, 626, 627, 628, 629, 631, 608, 633, 634, 635, 636, 638, 637, 639, 640, 641, 51, 52, 50, 53, 234, 680, 447, 448, 449
    # Batch 2a = 124, 617, 45, 56, 237, 623, 624, 630, 632, 643, 644, 646, 647, 648, 670, 671
    # Batch 2b = 685, 1086, 687, 688, 689, 683, 705, 706, 707, 708, 709, 710, 716, 717, 718, 719, 720, 721, 722, 723, 1087, 714, 713, 711, 728, 1089, 737, 1090, 740, 820, 821, 822, 747, 823
    # Batch 2c = 749, 824
    batch_ids = [824]
    for id in batch_ids:
        # hard code parameters for debugging
        param_range_map_id = arcpy.Parameter()
        param_range_map_id.value = str(id)
        param_spatial = arcpy.Parameter()
        param_spatial.value = 'true'
        parameters = [param_range_map_id, param_spatial]
        prm.RunPublishRangeMapTool(parameters, None)
