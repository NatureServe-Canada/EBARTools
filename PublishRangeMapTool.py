# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen, Gabrielle Miller, Samantha Stefanoff
# © NatureServe Canada 2026 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

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
import locale

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
        arcgis_pro_project = EBARUtils.resources_folder + '/EBARMapLayoutsEN.aprx'
        pdf_template_file_en = EBARUtils.resources_folder + '/pdf_template_en.html'
        pdf_template_file_fr = EBARUtils.resources_folder + '/pdf_template_fr.html'
        #reviewers_by_taxa_file = 'C:/Users/rgree/OneDrive/EBAR/EBAR Maps/TestReviewersByTaxa.txt'
        #reviewers_by_taxa_link = 'https://onedrive.live.com/download?cid=AAAAAE977404FA3B&resid=AAAAAE977404FA3B' + \
        #    '%21447909&authkey=AGzKOrgGlB1SHSE'

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        param_range_map_id = parameters[0].valueAsText
        EBARUtils.displayMessage(messages, 'Range Map ID: ' + param_range_map_id)
        param_spatial = parameters[1].valueAsText
        EBARUtils.displayMessage(messages, 'Include Spatial: ' + param_spatial)

        # replace metadata html tags with real data
        EBARUtils.displayMessage(messages, 'Filling metadata templates')
        pdf_template_en = open(pdf_template_file_en)
        pdf_html_en = pdf_template_en.read()
        pdf_template_en.close()
        pdf_template_fr = open(pdf_template_file_fr)
        pdf_html_fr = pdf_template_fr.read()
        pdf_template_fr.close()

        # headers - English
        pdf_html_en = pdf_html_en.replace('[logo_image]', EBARUtils.resources_folder +
                                          '/NatureServeCanada H 4C logo Small.png')
        pdf_html_en = pdf_html_en.replace('[species_header_image]', EBARUtils.resources_folder +
                                          '/species_header_en.png')
        pdf_html_en = pdf_html_en.replace('[rank_status_header_image]', EBARUtils.resources_folder +
                                           '/rank_status_header_en.png')
        pdf_html_en = pdf_html_en.replace('[range_map_header_image]', EBARUtils.resources_folder +
                                           '/range_map_header_en.png')
        # pdf_html_en = pdf_html_en.replace('[reviews_header_image]', EBARUtils.resources_folder +
        #                                   '/reviews_header_en.png')
        pdf_html_en = pdf_html_en.replace('[credits_header_image]', EBARUtils.resources_folder +
                                          '/credits_header_en.png')

        # headers - French
        pdf_html_fr = pdf_html_fr.replace('[logo_image]', EBARUtils.resources_folder + '/NatureServeCanada H 4C logo Small.png')
        pdf_html_fr = pdf_html_fr.replace('[species_header_image]', EBARUtils.resources_folder + '/species_header_fr.png')
        pdf_html_fr = pdf_html_fr.replace('[rank_status_header_image]', EBARUtils.resources_folder +
                                          '/rank_status_header_fr.png')
        pdf_html_fr = pdf_html_fr.replace('[range_map_header_image]', EBARUtils.resources_folder +
                                          '/range_map_header_fr.png')
        pdf_html_fr = pdf_html_fr.replace('[credits_header_image]', EBARUtils.resources_folder +
                                          '/credits_header_fr.png')

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
        with arcpy.da.SearchCursor('species_view', ['Endemism']) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                if row['Endemism']:
                    endemism_type = row['Endemism']
            del row
        pdf_html_en = pdf_html_en.replace('[Species.Endemism_Type]', endemism_type)
        pdf_html_fr = pdf_html_fr.replace('[Species.Endemism_Type]', endemism_type)

        # get biotics data from database
        EBARUtils.displayMessage(messages, 'Getting Biotics data from database')
        arcpy.MakeTableView_management(EBARUtils.ebar_feature_service + '/4', 'biotics_view',
                                       'SpeciesID = ' + str(species_id))
        with arcpy.da.SearchCursor('biotics_view', 
                                   ['NATIONAL_SCIENTIFIC_NAME', 'NATIONAL_ENGL_NAME', 'NATIONAL_FR_NAME',
                                    'ELEMENT_NATIONAL_ID', 'ELEMENT_GLOBAL_ID', 'ELEMENT_CODE', 
                                    'GLOBAL_UNIQUE_IDENTIFIER', 'G_JURIS_ENDEM_DESC', 'AUTHOR_NAME',
                                    'FORMATTED_FULL_CITATION', 'COSEWIC_NAME', 'COSEWIC_ID',
                                    'ENGLISH_COSEWIC_COM_NAME', 'FRENCH_COSEWIC_COM_NAME']) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                author_name = ''
                if row['AUTHOR_NAME']:
                    author_name = row['AUTHOR_NAME']
                french_name = ''
                if row['NATIONAL_FR_NAME']:
                    french_name = row['NATIONAL_FR_NAME']
                element_global_id = str(row['ELEMENT_GLOBAL_ID'])
                element_code = row['ELEMENT_CODE']
                global_unique_id = row['GLOBAL_UNIQUE_IDENTIFIER']
                #global_unique_id = global_unique_id.replace('-', '.')
                nsx_url = 'https://explorer.natureserve.org/Taxon/' + global_unique_id
                cosewic_name = ''
                if row['COSEWIC_NAME']:
                    cosewic_name = row['COSEWIC_NAME']
                cosewic_id = ''
                if row['COSEWIC_ID']:
                    cosewic_id = row['COSEWIC_ID']
                english_cosewic_com_name = ''
                if row['ENGLISH_COSEWIC_COM_NAME']:
                    english_cosewic_com_name = row['ENGLISH_COSEWIC_COM_NAME']
                french_cosewic_com_name = ''
                if row['FRENCH_COSEWIC_COM_NAME']:
                    french_cosewic_com_name = row['FRENCH_COSEWIC_COM_NAME']
                # English
                pdf_html_en = pdf_html_en.replace('[BIOTICS_ELEMENT_NATIONAL.NATIONAL_SCIENTIFIC_NAME]',
                                                  row['NATIONAL_SCIENTIFIC_NAME'])
                pdf_html_en = pdf_html_en.replace('[BIOTICS_ELEMENT_NATIONAL.AUTHOR_NAME]', author_name)
                pdf_html_en = pdf_html_en.replace('[BIOTICS_ELEMENT_NATIONAL.FORMATTED_FULL_CITATION]',
                                                  row['FORMATTED_FULL_CITATION'])
                pdf_html_en = pdf_html_en.replace('[BIOTICS_ELEMENT_NATIONAL.NATIONAL_ENGL_NAME]',
                                                  row['NATIONAL_ENGL_NAME'])
                pdf_html_en = pdf_html_en.replace('[BIOTICS_ELEMENT_NATIONAL.NATIONAL_FR_NAME]', french_name)
                pdf_html_en = pdf_html_en.replace('[BIOTICS_ELEMENT_NATIONAL.ELEMENT_NATIONAL_ID]',
                                                  str(row['ELEMENT_NATIONAL_ID']))
                pdf_html_en = pdf_html_en.replace('[BIOTICS_ELEMENT_NATIONAL.ELEMENT_GLOBAL_ID]',
                                                  element_global_id)
                pdf_html_en = pdf_html_en.replace('[BIOTICS_ELEMENT_NATIONAL.ELEMENT_CODE]', element_code)
                pdf_html_en = pdf_html_en.replace('[NSE2.0_URL]', nsx_url)
                pdf_html_en = pdf_html_en.replace('[BIOTICS_ELEMENT_NATIONAL.COSEWIC_NAME]',
                                                  cosewic_name)
                pdf_html_en = pdf_html_en.replace('[BIOTICS_ELEMENT_NATIONAL.COSEWIC_ID]',
                                                  cosewic_id)
                pdf_html_en = pdf_html_en.replace('[BIOTICS_ELEMENT_NATIONAL.ENGLISH_COSEWIC_COM_NAME]',
                                                  english_cosewic_com_name)
                pdf_html_en = pdf_html_en.replace('[BIOTICS_ELEMENT_NATIONAL.FRENCH_COSEWIC_COM_NAME]',
                                                  french_cosewic_com_name)
                # French
                pdf_html_fr = pdf_html_fr.replace('[BIOTICS_ELEMENT_NATIONAL.NATIONAL_SCIENTIFIC_NAME]',
                                                  row['NATIONAL_SCIENTIFIC_NAME'])
                pdf_html_fr = pdf_html_fr.replace('[BIOTICS_ELEMENT_NATIONAL.AUTHOR_NAME]', author_name)
                pdf_html_fr = pdf_html_fr.replace('[BIOTICS_ELEMENT_NATIONAL.FORMATTED_FULL_CITATION]',
                                                  row['FORMATTED_FULL_CITATION'])
                pdf_html_fr = pdf_html_fr.replace('[BIOTICS_ELEMENT_NATIONAL.NATIONAL_ENGL_NAME]',
                                                  row['NATIONAL_ENGL_NAME'])
                pdf_html_fr = pdf_html_fr.replace('[BIOTICS_ELEMENT_NATIONAL.NATIONAL_FR_NAME]', french_name)
                pdf_html_fr = pdf_html_fr.replace('[BIOTICS_ELEMENT_NATIONAL.ELEMENT_NATIONAL_ID]',
                                                  str(row['ELEMENT_NATIONAL_ID']))
                pdf_html_fr = pdf_html_fr.replace('[BIOTICS_ELEMENT_NATIONAL.ELEMENT_GLOBAL_ID]',
                                                  element_global_id)
                pdf_html_fr = pdf_html_fr.replace('[BIOTICS_ELEMENT_NATIONAL.ELEMENT_CODE]', element_code)
                pdf_html_fr = pdf_html_fr.replace('[NSE2.0_URL]', nsx_url)
                pdf_html_fr = pdf_html_fr.replace('[BIOTICS_ELEMENT_NATIONAL.COSEWIC_NAME]',
                                                  cosewic_name)
                pdf_html_fr = pdf_html_fr.replace('[BIOTICS_ELEMENT_NATIONAL.COSEWIC_ID]',
                                                  cosewic_id)
                pdf_html_fr = pdf_html_fr.replace('[BIOTICS_ELEMENT_NATIONAL.ENGLISH_COSEWIC_COM_NAME]',
                                                  english_cosewic_com_name)
                pdf_html_fr = pdf_html_fr.replace('[BIOTICS_ELEMENT_NATIONAL.FRENCH_COSEWIC_COM_NAME]',
                                                  french_cosewic_com_name)
            del row

        # get input citations
        EBARUtils.displayMessage(messages, 'Getting Input Citations from database')
        input_references = ''
        previous_dataset_source_name = ''
        arcpy.MakeTableView_management(EBARUtils.ebar_summary_service + '/7', 'citation_view',
                                       'RangeMapID = ' + param_range_map_id)
        # Nov 2024 - could now be multiple citations per source because InputDataset can have one
        # see database view s_InputCitationsByRangeMap, including DISTINCT clause!
        with arcpy.da.SearchCursor('citation_view', ['DatasetSourceName', 'DatasetSourceCitation',
                                                     'DatasetSourceWebsite', 'DatasetCitation']) as cursor:
            row = None
            for row in EBARUtils.searchCursor(cursor):
                dataset_source_name = row['DatasetSourceName']
                dataset_source_website = row['DatasetSourceWebsite']
                primary_citation = row['DatasetSourceCitation']
                secondary_citation = row['DatasetCitation']
                if dataset_source_name != previous_dataset_source_name:
                    citations_list = []
                # primary citation should never be NULL
                if not primary_citation:
                    EBARUtils.displayMessage('ERROR: ' + dataset_source_name + ' has no Citation')
                    return
                if primary_citation not in citations_list:
                    citations_list.append(primary_citation)
                    if len (input_references) > 0:
                        input_references += '<br>'
                    input_references += dataset_source_name + ' - '
                    # use website if provided as link for citation
                    if dataset_source_website:
                        input_references += ' <a href="' + dataset_source_website + '">' + \
                            primary_citation + '</a>'
                    else:
                        input_references += primary_citation
                # secondary citation can be NULL
                if secondary_citation:
                    if secondary_citation not in citations_list:
                        citations_list.append(secondary_citation)
                        input_references += '<br>'
                        input_references += dataset_source_name + ' - '
                        # use website if provided as link for citation
                        if dataset_source_website:
                            input_references += ' <a href="' + dataset_source_website + '">' + \
                                secondary_citation + '</a>'
                        else:
                            input_references += secondary_citation
                # handle multiple citations per source
                previous_dataset_source_name = dataset_source_name
            if row:
                del row
        pdf_html_en = pdf_html_en.replace('[InputReferences]', input_references)
        pdf_html_fr = pdf_html_fr.replace('[InputReferences]', input_references)

        # get range map data from database
        EBARUtils.displayMessage(messages, 'Getting RangeMap data from database')
        range_map_scope = None
        differentiate_usage_type = False
        row = None
        with arcpy.da.SearchCursor('range_map_view',
                                   ['SpeciesID', 'RangeVersion', 'RangeStage', 'RangeDate', 'RangeMapScope',
                                    'RangeMapNotes', 'RangeMetadata', 'RangeMapComments', 'ReviewerComments',
                                    'IncludeInDownloadTable', 'DifferentiateUsageType']) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                range_map_scope = EBARUtils.scope_dict[row['RangeMapScope']]
                comment = ''
                if row['RangeMapComments']:
                    comment += row['RangeMapComments']
                if len(comment) == 0:
                    comment = 'None'
                if row['IncludeInDownloadTable'] == 1:
                    if len(comment) > 0:
                        comment += '<br>'
                    suffix = ''
                    if range_map_scope == 'Canadian':
                        suffix = 'N'
                    comment += '<a href="' + EBARUtils.download_url + '/EBAR' + element_global_id + suffix + \
                        '.zip" target="_blank">Please see spatial data for Ecoshape-level reviewer comments</a>.'
                if row['DifferentiateUsageType']:
                    differentiate_usage_type = True
                # English
                pdf_html_en = pdf_html_en.replace('[RangeMap.RangeDate]', row['RangeDate'].strftime('%B %d, %Y'))
                pdf_html_en = pdf_html_en.replace('[RangeMap.RangeVersion]', row['RangeVersion'])
                pdf_html_en = pdf_html_en.replace('[RangeMap.RangeStage]', row['RangeStage'])
                pdf_html_en = pdf_html_en.replace('[RangeMap.RangeMapScope]', range_map_scope)
                pdf_html_en = pdf_html_en.replace('[RangeMap.RangeMapNotes]', row['RangeMapNotes'])
                pdf_html_en = pdf_html_en.replace('[RangeMap.RangeMetadata]', row['RangeMetadata'])
                pdf_html_en = pdf_html_en.replace('[RangeMap.RangeMapComments]', comment)
                # French
                # temporarily switch locale for date/time formatting
                original_lc_time = locale.getlocale(locale.LC_TIME)
                locale.setlocale(locale.LC_TIME, 'fr-ca')
                pdf_html_fr = pdf_html_fr.replace('[RangeMap.RangeDate]', row['RangeDate'].strftime('%d %B %Y'))
                locale.setlocale(locale.LC_TIME, original_lc_time)
                pdf_html_fr = pdf_html_fr.replace('[RangeMap.RangeVersion]', row['RangeVersion'])
                pdf_html_fr = pdf_html_fr.replace('[RangeMap.RangeStage]', row['RangeStage'])
                pdf_html_fr = pdf_html_fr.replace('[RangeMap.RangeMapScope]', range_map_scope)
                pdf_html_fr = pdf_html_fr.replace('[RangeMap.RangeMapNotes]', row['RangeMapNotes'])
                pdf_html_fr = pdf_html_fr.replace('[RangeMap.RangeMetadata]', row['RangeMetadata'])
                pdf_html_fr = pdf_html_fr.replace('[RangeMap.RangeMapComments]', comment)
        if range_map_scope:
            del row
        del cursor

        # get taxon attributes
        EBARUtils.displayMessage(messages, 'Getting taxon attributes')
        attributes = EBARUtils.getTaxonAttributes(global_unique_id, element_global_id, param_range_map_id, messages)

        # update template
        if len(attributes['ca_subnational_list']) > 0:
            attributes['ca_subnational_list'].sort()
            attributes['ca_subnational_ranks'] = ', '.join(attributes['ca_subnational_list'])
        if len(attributes['us_subnational_list']) > 0:
            attributes['us_subnational_list'].sort()
            attributes['us_subnational_ranks'] = ', '.join(attributes['us_subnational_list'])
        if len(attributes['mx_subnational_list']) > 0:
            attributes['mx_subnational_list'].sort()
            attributes['mx_subnational_ranks'] = ', '.join(attributes['mx_subnational_list'])
        # English
        pdf_html_en = pdf_html_en.replace('[NSE.grank]', attributes['g_rank'])
        pdf_html_en = pdf_html_en.replace('[NSE.grankReviewDate]', attributes['reviewed_grank'])
        pdf_html_en = pdf_html_en.replace('[NSE.CARank]', attributes['ca_rank'])
        pdf_html_en = pdf_html_en.replace('[NSE.USRank]', attributes['us_rank'])
        pdf_html_en = pdf_html_en.replace('[NSE.MXRank]', attributes['mx_rank'])
        pdf_html_en = pdf_html_en.replace('[NSE.CASubnationalRanks]', attributes['ca_subnational_ranks'])
        pdf_html_en = pdf_html_en.replace('[NSE.USSubnationalRanks]', attributes['us_subnational_ranks'])
        pdf_html_en = pdf_html_en.replace('[NSE.MXSubnationalRanks]', attributes['mx_subnational_ranks'])
        pdf_html_en = pdf_html_en.replace('[NSE.saraStatus]', attributes['sara_status'])
        pdf_html_en = pdf_html_en.replace('[NSE.cosewicStatus]', attributes['cosewic_status'])
        pdf_html_en = pdf_html_en.replace('[NSE.esaStatus]', attributes['esa_status'])
        # French
        pdf_html_fr = pdf_html_fr.replace('[NSE.grank]', attributes['g_rank'])
        pdf_html_fr = pdf_html_fr.replace('[NSE.grankReviewDate]', attributes['reviewed_grank'])
        pdf_html_fr = pdf_html_fr.replace('[NSE.CARank]', attributes['ca_rank'])
        pdf_html_fr = pdf_html_fr.replace('[NSE.USRank]', attributes['us_rank'])
        pdf_html_fr = pdf_html_fr.replace('[NSE.MXRank]', attributes['mx_rank'])
        pdf_html_fr = pdf_html_fr.replace('[NSE.CASubnationalRanks]', attributes['ca_subnational_ranks'])
        pdf_html_fr = pdf_html_fr.replace('[NSE.USSubnationalRanks]', attributes['us_subnational_ranks'])
        pdf_html_fr = pdf_html_fr.replace('[NSE.MXSubnationalRanks]', attributes['mx_subnational_ranks'])
        pdf_html_fr = pdf_html_fr.replace('[NSE.saraStatus]', attributes['sara_status'])
        pdf_html_fr = pdf_html_fr.replace('[NSE.cosewicStatus]', attributes['cosewic_status'])
        pdf_html_fr = pdf_html_fr.replace('[NSE.esaStatus]', attributes['esa_status'])

        # generate jpg and insert into pdf template
        EBARUtils.displayMessage(messages, 'Generating JPG maps')
        for suffix in ('_en', '_fr'):
            if suffix == '_fr':
                # temporarily switch locale for date/time formatting
                original_lc_time = locale.getlocale(locale.LC_TIME)
                locale.setlocale(locale.LC_TIME, 'fr-ca')
            aprx = arcpy.mp.ArcGISProject(arcgis_pro_project)
            map = aprx.listMaps('range map landscape terrain')[0]
            polygon_layer = map.listLayers('ecoshaperangemap')[0]
            polygon_layer.definitionQuery = 'rangemapid = ' + param_range_map_id + ' and presence is not null'
            table_layer = map.listTables('rangemap')[0]
            table_layer.definitionQuery = 'rangemapid = ' + param_range_map_id
            usage_type_layer = map.listLayers('usagetype')[0]
            if differentiate_usage_type:
                usage_type_layer.definitionQuery = 'rangemapid = ' + param_range_map_id
            else:
                usage_type_layer.visible = False
            if suffix == '_en':
                layout = aprx.listLayouts('range map landscape terrain watermark en')[0]
            else:
                layout = aprx.listLayouts('range map landscape terrain watermark fr')[0]
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
            layout.exportToJPEG(EBARUtils.download_folder + '/EBAR' + element_global_id + suffix + '.jpg', 300,
                                clip_to_elements=False)
            if suffix == '_fr':
                locale.setlocale(locale.LC_TIME, original_lc_time)
            pdf_html_en = pdf_html_en.replace('[map_image]', EBARUtils.download_folder + '/EBAR' + element_global_id +
                                              suffix + '.jpg')

        # generate pdf
        EBARUtils.displayMessage(messages, 'Generating PDFs')
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
        pdfkit.from_string(pdf_html_en, EBARUtils.download_folder + '/EBAR' + element_global_id + '_en.pdf', pdf_options)
        pdfkit.from_string(pdf_html_fr, EBARUtils.download_folder + '/EBAR' + element_global_id + '_fr.pdf', pdf_options)

        # generate zip
        if param_spatial == 'true':
            # generate metadata
            for suffix in ('_en', '_fr'):
                EBARUtils.displayMessage(messages, 'Generating zip for ' + suffix)
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
                EBARUtils.createReplaceFolder(EBARUtils.temp_folder + '/EBAR' + element_global_id + suffix)
                zip_folder = EBARUtils.temp_folder + '/EBAR' + element_global_id + suffix
                EBARUtils.createReplaceFolder(zip_folder)
                shutil.copyfile(EBARUtils.resources_folder + '/Readme' + suffix + '.txt', zip_folder + '/Readme.txt')
                shutil.copyfile(EBARUtils.resources_folder + '/EBARMethods' + suffix +'.pdf', zip_folder + '/EBARMethods.pdf')
                shutil.copyfile(EBARUtils.download_folder + '/EBAR' + element_global_id + suffix + '.pdf',
                                zip_folder + '/EBAR' + element_global_id + suffix + '.pdf')
                shutil.copyfile(EBARUtils.resources_folder + '/Jurisdiction.csv', zip_folder + '/Jurisdiction.csv')
                jurisdiction_md = arcpy.metadata.Metadata(zip_folder + '/Jurisdiction.csv')
                md.title = 'EBAR Jurisdiction.csv'
                md.summary = 'Table of jurisdictions'
                jurisdiction_md.copy(md)
                jurisdiction_md.save()

                # export range map, with biotics/species additions
                EBARUtils.displayMessage(messages, 'Exporting RangeMap to CSV')
                if suffix == '_en':
                    EBARUtils.ExportRangeMapToCSV('range_map_view' + param_range_map_id, [param_range_map_id],
                                                  {param_range_map_id: attributes}, zip_folder, 'RangeMap.csv', md)
                else:
                    EBARUtils.ExportRangeMapToCSV('range_map_view' + param_range_map_id, [param_range_map_id],
                                                  {param_range_map_id: attributes}, zip_folder, 'RangeMap.csv', md)

                # export range map ecoshapes
                EBARUtils.displayMessage(messages, 'Exporting RangeMapEcoshape records to CSV')
                if suffix == '_en':
                    EBARUtils.ExportRangeMapEcoshapesToCSV('range_map_ecoshape_view' + param_range_map_id,
                                                           [param_range_map_id], zip_folder, 'RangeMapEcoshape.csv', md)
                else:
                    EBARUtils.ExportRangeMapEcoshapesToCSV('range_map_ecoshape_view' + param_range_map_id,
                                                           [param_range_map_id], zip_folder, 'RangeMapEcoshape.csv', md)

                # export ecoshapes
                EBARUtils.displayMessage(messages, 'Exporting Ecoshape polygons to shapefile')
                if suffix == '_en':
                    EBARUtils.ExportEcoshapesToShapefile('ecoshape_layer' + param_range_map_id,
                                                         'range_map_ecoshape_view' + param_range_map_id, zip_folder, 
                                                         'Ecoshape.shp', md, False)
                else:
                    EBARUtils.ExportEcoshapesToShapefile('ecoshape_layer' + param_range_map_id,
                                                         'range_map_ecoshape_view' + param_range_map_id, zip_folder, 
                                                         'Ecoshape.shp', md, False)

                # export overview ecoshapes
                EBARUtils.displayMessage(messages, 'Exporting EcoshapeOverview polygons to shapefile')
                if suffix == '_en':
                    EBARUtils.ExportEcoshapeOverviewsToShapefile('ecoshape_overview_layer' + param_range_map_id,
                                                                 'range_map_ecoshape_view' + param_range_map_id, zip_folder, 
                                                                 'EcoshapeOverview.shp', md, False)
                else:
                    EBARUtils.ExportEcoshapeOverviewsToShapefile('ecoshape_overview_layer' + param_range_map_id,
                                                                 'range_map_ecoshape_view' + param_range_map_id, zip_folder, 
                                                                 'EcoshapeOverview.shp', md, False)

                # update ArcGIS Pro template
                EBARUtils.displayMessage(messages, 'Updating ArcGIS Pro template')
                EBARUtils.updateArcGISProTemplate(zip_folder, element_global_id, md, param_range_map_id, differentiate_usage_type)

                # copy ArcMap template
                EBARUtils.displayMessage(messages, 'Copying ArcMap template')
                shutil.copyfile(EBARUtils.resources_folder + '/EBAR.mxd',
                                zip_folder + '/EBAR' + element_global_id + suffix + '.mxd')
                if differentiate_usage_type:
                    shutil.copyfile(EBARUtils.resources_folder + '/UsageType.lyr',
                                    zip_folder + '/EBAR' + element_global_id + suffix + 'UsageType.lyr')
                shutil.copyfile(EBARUtils.resources_folder + '/EcoshapeOverview.lyr',
                                zip_folder + '/EBAR' + element_global_id + suffix + 'EcoshapeOverview.lyr')
                shutil.copyfile(EBARUtils.resources_folder + '/RemovedEcoshapes.lyr',
                                zip_folder + '/EBAR' + element_global_id + suffix + 'RemovedEcoshapes.lyr')
                shutil.copyfile(EBARUtils.resources_folder + '/Ecoshape.lyr',
                                zip_folder + '/EBAR' + element_global_id + suffix + 'Ecoshape.lyr')

                # zip
                EBARUtils.displayMessage(messages, 'Creating ZIP')
                EBARUtils.createZip(zip_folder,
                                    EBARUtils.download_folder + '/EBAR' + element_global_id + suffix + '.zip', None)

        # set publish date
        with arcpy.da.UpdateCursor('range_map_view', ['PublishDate']) as update_cursor:
            for update_row in EBARUtils.updateCursor(update_cursor):
                update_cursor.updateRow([datetime.datetime.now()])
            del update_row

        # results link messages
        for suffix in ('_en', '_fr'):
            EBARUtils.displayMessage(messages,
                                    'Image: ' + EBARUtils.download_url + '/EBAR' + element_global_id + suffix + '.jpg')
            EBARUtils.displayMessage(messages,
                                    'PDF: ' + EBARUtils.download_url + '/EBAR' + element_global_id + suffix + '.pdf')
            if param_spatial == 'true':
                EBARUtils.displayMessage(messages,
                                        'GIS Data: ' + EBARUtils.download_url + '/EBAR' + element_global_id + suffix +
                                        '.zip')

        # cleanup
        arcpy.Delete_management('range_map_view')
        arcpy.Delete_management('biotics_view')
        arcpy.Delete_management('species_view')
        arcpy.Delete_management('citation_view')
        if param_spatial == 'true':
            arcpy.Delete_management('range_map_ecoshape_view')
            # attempt to overcome GP service holding a hook into the folder
            del zip_folder

        return


# controlling process
if __name__ == '__main__':
    prm = PublishRangeMapTool()
    
    # #spatial_batch_ids = [2727,4282,4303,4308,4313,4314,4320,4321,4322,4323,4324,4325,4333,4335,4337,4338,4339,4340,4341,4347,4350,4358,4360,4361,4362,4363,4364,4366,4368,4369,4370,4371,4374,4376,4378,4383,4386,4389,4391,4408,4424,4430,4432,4439,4440,4441,4443,4445,4447,4448,4449,4450,4451,4452,4455,4456,4457,4459,4461,4463,4464,4465,4468,4472,4475,4477,4480,4481,4482,4486,4487,4494,4500,4504,4507,4508,4511,4512,4513,4514,4515,4516,4518,4519,4520,4521,4522,4523,4524,4526,4527,4528,4529,4530,4531,4532,4533,4534,4535,4536,4537,4538,4539,4540,4541,4545,4546,4547,4548,4549,4550,4551,4552,4553,4554,4556,4557,4558,4559,4561,4562,4563,4564,4566,4567,4568,4569,4570,4571,4572,4574,4575,4576,4577,4578,4587,4595,4599,4611,4615]
    # spatial_batch_ids = [3337]
    # for id in spatial_batch_ids:
    #    # hard code parameters for debugging
    #    param_range_map_id = arcpy.Parameter()
    #    param_range_map_id.value = str(id)
    #    param_spatial = arcpy.Parameter()
    #    param_spatial.value = 'true'
    #    parameters = [param_range_map_id, param_spatial]
    #    prm.runPublishRangeMapTool(parameters, None)
    
    #non_spatial_batch_ids = [4703,4704,4705,4706,4707,4708,4709,4710,4711,4712] #,4713,4714,4715,4716,4717,4718,4719,4720,4721,4722,4723,4724,4725,4726,4727,4728,4729,4730,4731,4732]
    non_spatial_batch_ids = list(range(4765, 4774)) #[4733]
    for id in non_spatial_batch_ids:
        # hard code parameters for debugging
        param_range_map_id = arcpy.Parameter()
        param_range_map_id.value = str(id)
        param_spatial = arcpy.Parameter()
        param_spatial.value = 'false'
        parameters = [param_range_map_id, param_spatial]
        prm.runPublishRangeMapTool(parameters, None)
