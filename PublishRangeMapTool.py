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
import StaticTranslations


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
        arcgis_pro_project_en = EBARUtils.resources_folder + '/EBARMapLayoutsEN.aprx'
        arcgis_pro_project_fr = EBARUtils.resources_folder + '/EBARMapLayoutsFR.aprx'
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
        pdf_template_en = open(pdf_template_file_en, encoding="utf-8")
        pdf_html_en = pdf_template_en.read()
        pdf_template_en.close()
        pdf_template_fr = open(pdf_template_file_fr, encoding="utf-8")
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
        input_references_fr = ''
        previous_dataset_source_name = ''
        arcpy.MakeTableView_management(EBARUtils.ebar_summary_service + '/7', 'citation_view',
                                       'RangeMapID = ' + param_range_map_id)
        # Nov 2024 - could now be multiple citations per source because InputDataset can have one
        # see database view s_InputCitationsByRangeMap, including DISTINCT clause!
        with arcpy.da.SearchCursor('citation_view', ['DatasetSourceName', 'DatasetSourceCitation',
                                                     'DatasetSourceWebsite', 'DatasetCitation',
                                                     'DatasetSourceName_FR', 'DatasetSourceCitation_FR',
                                                     'DatasetCitation_FR']) as cursor:
            row = None
            for row in EBARUtils.searchCursor(cursor):
                dataset_source_name = row['DatasetSourceName']
                dataset_source_name_fr = row['DatasetSourceName']
                if row['DatasetSourceName_FR']:
                    dataset_source_name_fr = row['DatasetSourceName_FR']
                dataset_source_website = row['DatasetSourceWebsite']
                primary_citation = row['DatasetSourceCitation']
                primary_citation_fr = row['DatasetSourceCitation']
                if row['DatasetSourceCitation_FR']:
                    primary_citation_fr = row['DatasetSourceCitation_FR']
                secondary_citation = row['DatasetCitation']
                secondary_citation_fr = row['DatasetCitation']
                if row['DatasetCitation_FR']:
                    secondary_citation_fr = row['DatasetCitation_FR']
                if dataset_source_name != previous_dataset_source_name:
                    citations_list = []
                    citations_list_fr = []
                # primary citation should never be NULL
                if not primary_citation:
                    EBARUtils.displayMessage('ERROR: ' + dataset_source_name + ' has no Citation')
                    return
                if primary_citation not in citations_list:
                    citations_list.append(primary_citation)
                    if len (input_references) > 0:
                        input_references += '<br>'
                        input_references_fr += '<br>'
                    input_references += dataset_source_name + ' - '
                    input_references_fr += dataset_source_name_fr + ' - '
                    # use website if provided as link for citation
                    if dataset_source_website:
                        input_references += ' <a href="' + dataset_source_website + '">' + \
                            primary_citation + '</a>'
                        input_references_fr += ' <a href="' + dataset_source_website + '">' + \
                            primary_citation_fr + '</a>'
                    else:
                        input_references += primary_citation
                        input_references_fr += primary_citation_fr
                # secondary citation can be NULL
                if secondary_citation:
                    if secondary_citation not in citations_list:
                        citations_list.append(secondary_citation)
                        input_references += '<br>'
                        input_references_fr += '<br>'
                        input_references += dataset_source_name + ' - '
                        input_references_fr += dataset_source_name_fr + ' - '
                        # use website if provided as link for citation
                        if dataset_source_website:
                            input_references += ' <a href="' + dataset_source_website + '">' + \
                                secondary_citation + '</a>'
                            input_references_fr += ' <a href="' + dataset_source_website + '">' + \
                                secondary_citation_fr + '</a>'
                        else:
                            input_references += secondary_citation
                            input_references_fr += secondary_citation_fr
                # handle multiple citations per source
                previous_dataset_source_name = dataset_source_name
            if row:
                del row
        pdf_html_en = pdf_html_en.replace('[InputReferences]', input_references)
        pdf_html_fr = pdf_html_fr.replace('[InputReferences]', input_references_fr)

        # get range map data from database
        EBARUtils.displayMessage(messages, 'Getting RangeMap data from database')
        range_map_scope = None
        differentiate_usage_type = False
        row = None
        with arcpy.da.UpdateCursor('range_map_view',
                                   ['SpeciesID', 'RangeVersion', 'RangeStage', 'RangeStage_FR', 'RangeDate',
                                    'RangeMapScope', 'RangeMapNotes', 'RangeMapNotes_FR', 'RangeMetadata',
                                    'RangeMetadata_FR', 'RangeMapComments', 'RangeMapComments_FR', 'ReviewerComments',
                                    'IncludeInDownloadTable', 'DifferentiateUsageType']) as cursor:
            for row in EBARUtils.updateCursor(cursor):
                if not row['RangeStage_FR']:
                    EBARUtils.displayMessage(messages, 'ERROR: RangeMap has not been translated to French! ' +
                                             'Please rerun the Generate Range Map tool or use bulk translation.')
                    return
                if row['DifferentiateUsageType']:
                    differentiate_usage_type = True
                # English
                range_map_scope = EBARUtils.scope_dict[row['RangeMapScope']]
                comment = ''
                if row['RangeMapComments']:
                    comment = row['RangeMapComments']
                if len(comment) == 0:
                    comment = 'None'
                if row['IncludeInDownloadTable'] == 1:
                    if len(comment) > 0:
                        comment += '<br>'
                    append = ''
                    if range_map_scope == 'Canadian':
                        append = 'N'
                    comment += '<a href="' + EBARUtils.download_url + '/EBAR' + element_global_id + append + \
                        '.zip" target="_blank">Please see spatial data for Ecoshape-level reviewer comments</a>.'
                pdf_html_en = pdf_html_en.replace('[RangeMap.RangeDate]', row['RangeDate'].strftime('%B %d, %Y'))
                pdf_html_en = pdf_html_en.replace('[RangeMap.RangeVersion]', row['RangeVersion'])
                pdf_html_en = pdf_html_en.replace('[RangeMap.RangeStage]', row['RangeStage'])
                pdf_html_en = pdf_html_en.replace('[RangeMap.RangeMapScope]', range_map_scope)
                pdf_html_en = pdf_html_en.replace('[RangeMap.RangeMapNotes]', row['RangeMapNotes'])
                pdf_html_en = pdf_html_en.replace('[RangeMap.RangeMetadata]', row['RangeMetadata'])
                pdf_html_en = pdf_html_en.replace('[RangeMap.RangeMapComments]', comment)
                # French
                range_map_scope_fr = StaticTranslations.range_map_scope_translation[row['RangeMapScope']]
                comment_fr = ''
                if row['RangeMapComments']:
                    comment_fr = EBARUtils.translateENtoFRUsingDeepL(comment) + ' (traduit par DeepL)'
                else:
                    comment_fr = 'Aucun'
                cursor.updateRow([row['SpeciesID'], row['RangeVersion'], row['RangeStage'], row['RangeStage_FR'],
                                  row['RangeDate'], row['RangeMapScope'], row['RangeMapNotes'],
                                  row['RangeMapNotes_FR'], row['RangeMetadata'], row['RangeMetadata_FR'],
                                  row['RangeMapComments'], comment_fr, row['ReviewerComments'],
                                  row['IncludeInDownloadTable'], row['DifferentiateUsageType']])
                if row['IncludeInDownloadTable'] == 1:
                    if len(comment_fr) > 0:
                        comment_fr += '<br>'
                    append = ''
                    if range_map_scope == 'Canadian':
                        append = 'N'
                    comment_fr += '<a href="' + EBARUtils.download_url + '/EBAR' + element_global_id + append + \
                        '_FR.zip" target="_blank">Veuillez consulter les données spatiales pour les commentaires des ' + \
                        'réviseurs au niveau d''Ecoshape</a>.'
                # temporarily switch locale for date/time formatting
                original_lc_time = locale.getlocale(locale.LC_TIME)
                locale.setlocale(locale.LC_TIME, 'fr-ca')
                pdf_html_fr = pdf_html_fr.replace('[RangeMap.RangeDate]', row['RangeDate'].strftime('%d %B %Y'))
                locale.setlocale(locale.LC_TIME, original_lc_time)
                pdf_html_fr = pdf_html_fr.replace('[RangeMap.RangeVersion]', row['RangeVersion'])
                pdf_html_fr = pdf_html_fr.replace('[RangeMap.RangeStage]', row['RangeStage_FR'])
                pdf_html_fr = pdf_html_fr.replace('[RangeMap.RangeMapScope]', range_map_scope_fr)
                pdf_html_fr = pdf_html_fr.replace('[RangeMap.RangeMapNotes]', row['RangeMapNotes_FR'])
                pdf_html_fr = pdf_html_fr.replace('[RangeMap.RangeMetadata]', row['RangeMetadata_FR'])
                pdf_html_fr = pdf_html_fr.replace('[RangeMap.RangeMapComments]', comment_fr)
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
        pdf_html_fr = pdf_html_fr.replace('[NSE.grankReviewDate]', attributes['reviewed_grank_fr'])
        pdf_html_fr = pdf_html_fr.replace('[NSE.CARank]', attributes['ca_rank_fr'])
        pdf_html_fr = pdf_html_fr.replace('[NSE.USRank]', attributes['us_rank_fr'])
        pdf_html_fr = pdf_html_fr.replace('[NSE.MXRank]', attributes['mx_rank_fr'])
        pdf_html_fr = pdf_html_fr.replace('[NSE.CASubnationalRanks]', attributes['ca_subnational_ranks_fr'])
        pdf_html_fr = pdf_html_fr.replace('[NSE.USSubnationalRanks]', attributes['us_subnational_ranks_fr'])
        pdf_html_fr = pdf_html_fr.replace('[NSE.MXSubnationalRanks]', attributes['mx_subnational_ranks_fr'])
        pdf_html_fr = pdf_html_fr.replace('[NSE.saraStatus]', attributes['sara_status_fr'])
        pdf_html_fr = pdf_html_fr.replace('[NSE.cosewicStatus]', attributes['cosewic_status_fr'])
        pdf_html_fr = pdf_html_fr.replace('[NSE.esaStatus]', attributes['esa_status_fr'])

        # generate jpg and insert into pdf template
        EBARUtils.displayMessage(messages, 'Generating JPG maps')
        if range_map_scope == 'Canadian':
            element_global_id += 'N'
        for suffix in ('_fr'): # ('_en', '_fr'):
            if suffix == '_fr':
                aprx = arcpy.mp.ArcGISProject(arcgis_pro_project_fr)
                # temporarily switch locale for date/time formatting
                original_lc_time = locale.getlocale(locale.LC_TIME)
                locale.setlocale(locale.LC_TIME, 'fr-ca')
            else:
                aprx = arcpy.mp.ArcGISProject(arcgis_pro_project_en)
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
            if suffix == '_fr':
                layout.exportToJPEG(EBARUtils.download_folder + '/EBAR' + element_global_id + '_FR.jpg', 300,
                                    clip_to_elements=False)
                pdf_html_fr = pdf_html_fr.replace('[map_image]', EBARUtils.download_folder + '/EBAR' +
                                                  element_global_id + '_FR.jpg')
                locale.setlocale(locale.LC_TIME, original_lc_time)
            else: # _en
                layout.exportToJPEG(EBARUtils.download_folder + '/EBAR' + element_global_id + '.jpg', 300,
                                    clip_to_elements=False)
                pdf_html_en = pdf_html_en.replace('[map_image]', EBARUtils.download_folder + '/EBAR' +
                                                  element_global_id + '.jpg')

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
        #pdfkit.from_string(pdf_html_en, EBARUtils.download_folder + '/EBAR' + element_global_id + '.pdf', pdf_options)
        pdfkit.from_string(pdf_html_fr, EBARUtils.download_folder + '/EBAR' + element_global_id + '_FR.pdf', pdf_options)

        # generate zip
        if param_spatial == 'true':
            for suffix in ('_en', '_fr'):
                EBARUtils.displayMessage(messages, 'Generating GIS ZIP for ' + suffix)
                if suffix == '_en':
                    # generate metadata
                    EBARUtils.displayMessage(messages, 'Generating metadata')
                    md = arcpy.metadata.Metadata()
                    md.tags = 'Species Range, NatureServe Canada, Ecosystem-based Automated Range'
                    md.description = 'See EBAR' + element_global_id + '.pdf for map and additional metadata, and ' + \
                        'EBARMethods.pdf for additional details. <a href="' + nsx_url + '">Go to ' + \
                        'NatureServe Explorer</a> for information about the species.'
                    md.credits = 'Copyright NatureServe Canada ' + str(datetime.datetime.now().year)
                    md.accessConstraints = 'Publicly shareable under CC BY 4.0 (<a href=' + \
                        '"https://creativecommons.org/licenses/by/4.0/">' + \
                        'https://creativecommons.org/licenses/by/4.0/</a>)'

                    # make folder, copy in static resources and EBAR pdf
                    EBARUtils.displayMessage(messages, 'Creating ZIP folder and copying files')
                    EBARUtils.createReplaceFolder(EBARUtils.temp_folder + '/EBAR' + element_global_id + suffix)
                    zip_folder = EBARUtils.temp_folder + '/EBAR' + element_global_id
                    EBARUtils.createReplaceFolder(zip_folder)
                    shutil.copyfile(EBARUtils.resources_folder + '/Readme' + suffix + '.txt',
                                    zip_folder + '/Readme.txt')
                    shutil.copyfile(EBARUtils.resources_folder + '/EBARMethods' + suffix +'.pdf',
                                    zip_folder + '/EBARMethods.pdf')
                    shutil.copyfile(EBARUtils.download_folder + '/EBAR' + element_global_id + '.pdf',
                                    zip_folder + '/EBAR' + element_global_id + '.pdf')
                    shutil.copyfile(EBARUtils.resources_folder + '/Jurisdiction.csv', zip_folder + '/Jurisdiction.csv')
                    jurisdiction_md = arcpy.metadata.Metadata(zip_folder + '/Jurisdiction.csv')
                    md.title = 'EBAR Jurisdiction.csv'
                    md.summary = 'Table of jurisdictions'
                    jurisdiction_md.copy(md)
                    jurisdiction_md.save()

                    # export range map, with biotics/species additions
                    EBARUtils.displayMessage(messages, 'Exporting RangeMap to CSV')
                    EBARUtils.ExportRangeMapToCSV('range_map_view' + suffix + param_range_map_id, [param_range_map_id],
                                                  {param_range_map_id: attributes}, zip_folder, 'RangeMap.csv', md, suffix)

                    # export range map ecoshapes
                    EBARUtils.displayMessage(messages, 'Exporting RangeMapEcoshape records to CSV')
                    EBARUtils.ExportRangeMapEcoshapesToCSV('range_map_ecoshape_view' + suffix + param_range_map_id,
                                                           [param_range_map_id], zip_folder, 'RangeMapEcoshape.csv', md,
                                                           suffix)

                    # export ecoshapes
                    EBARUtils.displayMessage(messages, 'Exporting Ecoshape polygons to shapefile')
                    EBARUtils.ExportEcoshapesToShapefile('ecoshape_layer' + suffix + param_range_map_id,
                                                         'range_map_ecoshape_view' + suffix + param_range_map_id,
                                                         zip_folder, 'Ecoshape.shp', md, False, suffix)

                    # export overview ecoshapes
                    EBARUtils.displayMessage(messages, 'Exporting EcoshapeOverview polygons to shapefile')
                    EBARUtils.ExportEcoshapeOverviewsToShapefile('ecoshape_overview_layer' + suffix + param_range_map_id,
                                                                 'range_map_ecoshape_view' + suffix + param_range_map_id,
                                                                 zip_folder, 'EcoshapeOverview.shp', md, False, suffix)

                else:  # _fr
                    # generate metadata
                    EBARUtils.displayMessage(messages, 'Generating metadata')
                    md = arcpy.metadata.Metadata()
                    md.tags = 'Répartition des Espèces, NatureServe Canada, ' + \
                        'Cartographie automatisée des aires de répartition basée sur les écosystèmes'
                    md.description = 'Voir EBAR' + element_global_id + '_FR.pdf pour la carte et les métadonnées ' + \
                        'supplémentaires, et MethodsEBAR.pdf pour plus de détails. <a href="' + nsx_url + \
                        '"> Rendez-vous sur NatureServe Explorer</a>  pour obtenir des informations sur les espèces.'
                    md.credits = '© NatureServe Canada ' + str(datetime.datetime.now().year)
                    md.accessConstraints = 'Partageable publiquement sous licence CC BY 4.0  (<a href=' + \
                        '"https://creativecommons.org/licenses/by/4.0/deed.fr">' + \
                        'https://creativecommons.org/licenses/by/4.0/deed.fr</a>)'

                    # make folder, copy in static resources and EBAR pdf
                    EBARUtils.displayMessage(messages, 'Creating ZIP folder and copying files')
                    EBARUtils.createReplaceFolder(EBARUtils.temp_folder + '/EBAR' + element_global_id + suffix)
                    zip_folder = EBARUtils.temp_folder + '/EBAR' + element_global_id + '_FR'
                    EBARUtils.createReplaceFolder(zip_folder)
                    shutil.copyfile(EBARUtils.resources_folder + '/Readme' + suffix + '.txt', zip_folder + '/Lisez-moi.txt')
                    shutil.copyfile(EBARUtils.resources_folder + '/EBARMethods' + suffix +'.pdf', zip_folder + '/MethodsEBAR.pdf')
                    shutil.copyfile(EBARUtils.download_folder + '/EBAR' + element_global_id + '_FR.pdf',
                                    zip_folder + '/EBAR' + element_global_id + '_FR.pdf')
                    shutil.copyfile(EBARUtils.resources_folder + '/Juridiction.csv', zip_folder + '/Juridiction.csv')
                    jurisdiction_md = arcpy.metadata.Metadata(zip_folder + '/Juridiction.csv')
                    md.title = 'Juridiction EBAR.csv'
                    md.summary = 'Tableau des juridictions'
                    jurisdiction_md.copy(md)
                    jurisdiction_md.save()

                    # export range map, with biotics/species additions
                    EBARUtils.displayMessage(messages, 'Exporting RangeMap to CSV')
                    EBARUtils.ExportRangeMapToCSV('range_map_view' + suffix + param_range_map_id, [param_range_map_id],
                                                  {param_range_map_id: attributes}, zip_folder, 'CarteRepartition.csv', md, suffix)

                    # export range map ecoshapes
                    EBARUtils.displayMessage(messages, 'Exporting RangeMapEcoshape records to CSV')
                    EBARUtils.ExportRangeMapEcoshapesToCSV('range_map_ecoshape_view' + suffix + param_range_map_id,
                                                           [param_range_map_id], zip_folder, 'CarteRepartitionEcoshape.csv', md,
                                                           suffix)

                    # export ecoshapes
                    EBARUtils.displayMessage(messages, 'Exporting Ecoshape polygons to shapefile')
                    EBARUtils.ExportEcoshapesToShapefile('ecoshape_layer' + suffix + param_range_map_id,
                                                         'range_map_ecoshape_view' + suffix + param_range_map_id,
                                                         zip_folder, 'Ecoshape.shp', md, False, suffix)

                    # export overview ecoshapes
                    EBARUtils.displayMessage(messages, 'Exporting EcoshapeOverview polygons to shapefile')
                    EBARUtils.ExportEcoshapeOverviewsToShapefile('ecoshape_overview_layer' + suffix + param_range_map_id,
                                                                 'range_map_ecoshape_view' + suffix + param_range_map_id,
                                                                 zip_folder, 'EcoshapeApercu.shp', md, False, suffix)
                    
                # update ArcGIS Pro template
                EBARUtils.displayMessage(messages, 'Updating ArcGIS Pro template')
                EBARUtils.updateArcGISProTemplate(zip_folder, element_global_id, md, param_range_map_id,
                                                  differentiate_usage_type, suffix)

                if suffix == '_en':
                    # copy ArcMap template
                    EBARUtils.displayMessage(messages, 'Copying ArcMap template')
                    shutil.copyfile(EBARUtils.resources_folder + '/EBAR.mxd',
                                    zip_folder + '/EBAR' + element_global_id + '.mxd')
                    if differentiate_usage_type:
                        shutil.copyfile(EBARUtils.resources_folder + '/UsageType.lyr',
                                        zip_folder + '/EBAR' + element_global_id + 'UsageType.lyr')
                    shutil.copyfile(EBARUtils.resources_folder + '/EcoshapeOverview.lyr',
                                    zip_folder + '/EBAR' + element_global_id + 'EcoshapeOverview.lyr')
                    shutil.copyfile(EBARUtils.resources_folder + '/RemovedEcoshapes.lyr',
                                    zip_folder + '/EBAR' + element_global_id + 'RemovedEcoshapes.lyr')
                    shutil.copyfile(EBARUtils.resources_folder + '/Ecoshape.lyr',
                                    zip_folder + '/EBAR' + element_global_id + 'Ecoshape.lyr')

                # zip
                if suffix == '_en':
                    EBARUtils.createZip(zip_folder,
                                        EBARUtils.download_folder + '/EBAR' + element_global_id + '.zip',
                                        None)
                else: # _fr
                    EBARUtils.createZip(zip_folder,
                                        EBARUtils.download_folder + '/EBAR' + element_global_id + '_FR.zip',
                                        None)

        # set publish date
        with arcpy.da.UpdateCursor('range_map_view', ['PublishDate']) as update_cursor:
            for update_row in EBARUtils.updateCursor(update_cursor):
                update_cursor.updateRow([datetime.datetime.now()])
            del update_row

        # results link messages
        EBARUtils.displayMessage(messages,
                                'English Image: ' + EBARUtils.download_url + '/EBAR' + element_global_id + '.jpg')
        EBARUtils.displayMessage(messages,
                                'French Image: ' + EBARUtils.download_url + '/EBAR' + element_global_id + '_FR.jpg')
        EBARUtils.displayMessage(messages,
                                'English PDF: ' + EBARUtils.download_url + '/EBAR' + element_global_id + '.pdf')
        EBARUtils.displayMessage(messages,
                                'French PDF: ' + EBARUtils.download_url + '/EBAR' + element_global_id + '_FR.pdf')
        if param_spatial == 'true':
            EBARUtils.displayMessage(messages,
                                    'English GIS Data: ' + EBARUtils.download_url + '/EBAR' + element_global_id +
                                    '.zip')
            EBARUtils.displayMessage(messages,
                                    'French GIS Data: ' + EBARUtils.download_url + '/EBAR' + element_global_id +
                                    '_FR.zip')

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
    
    #[680,616,618,620,622,624,626,627,628,630,631,633,634,635,636,639,640,641,621,448,665,619,617,685,687,689,706,707,709,712,713,714,710,716,719,720,1087,747,749,824,858,859,862,866,867,869,870,871,1093,1096,1098,1102,1103,1104,1105,1112,1113,1115,1129,1130,1131,1133,1134,1135,1137,1138,1139,1140,1141,1142,1144,1146,1147,1149,1151,1153,1154,1155,1156,1157,1158,1179,1184,1187,1190,1223,1225,1227,1231,1233,1241,1243,1254,1258,1296,1729,1737,1739,1152,1747,1752,1136,1780,865,1840,1861,708,1823,1878,1880,625,2238,2239,2240,2307,2309,2311,2313,2315,2308,2241,2322,2324,2325,2326,2327,2328,2329,2330,2331,2333,2334,2335,2336,2337,2338,2339,2341,2342,2323,2340,2344,2332,2237,2356,2357,2358,2359,2361,2363,2364,2365,2366,2367,2368,2369,2370,2360,2362,2379,2381,2382,2383,2384,2385,2386,2387,2388,2389,2390,2393,2395,2377,2376,2391,2399,2401,2398,2410,2411,2412,2413,2414,2415,2416,2417,2418,2419,2420,2423,2424,2425,2428,2429,2430,2431,2432,2433,2435,2436,2438,2439,2443,2444,2445,2446,2447,2448,2450,2452,2453,2409,2426,2421,2427,2434,2437,2460,2462,2461,2463,2465,2466,2473,2474,2475,2476,2478,2479,2480,2481,2484,2470,2472,2471,2477,2468,2467,2487,2489,2469,2491,2497,2498,2499,2501,2502,2506,2512,2517,2521,2522,2541,2547,2554,2556,2561,2576,2593]
    #[2599,1822,1283,2440,2551,2650,2651,2660,2675,2741,2758,2907,2913,2914,2915,2916,2918,2924,2928,2933,2935,2936,2939,2940,2941,2942,2943,2944,2945,2947,2948,2949,2950,2951,2952,2953,2955,2954,2956,2984,2987,2992,3026,3027,3036,3037,3047,3052,3053,3055,3058,3059,3060,3061,3062,3063,3067,3068,3069,3071,3072,3084,3085,3087,3089,3092,3093,3094,3097,3098,3107,3109,3110,3115,3116,3119,3122,3123,3125,3126,3128,3130,3131,3132,3133,3134,3138,3142,3144,3145,3146,3147,3148,3150,3154,3155,3157,3151,3170,3171,3174,3175,3181,3182,3184,3191,3193,3205,3206,3208,3214,3215,3216,3217,3218,3219,3221,3223,3222,3224,3229,3230,3234,3235,3236,3237,3241,3243,3245,3238,3185,3252,3254,3255,3256,3257,3260,3261,3263,3264,3265,3275,3249,1278,3270,3284,3290,3296,3297,3298,3303,3158,3311,3313,3314,3359,3444,3445,3446,3447,3456,3458,3459,3461,3462,3463,3468,3501,3503,3504,3505,3506,3470,3528,3493,3588,3603,3628,2798,3662,3683,3710,3718,3733,3704,3755,3564,3767,3770,3772,3769,3773,3774,3775,3776,3777,3778,3782,3783,3784,3785,3768,3274,3781,3791,3793,3795,3796,3797,3798,3799,3800,3801,3802,3803,3804,3805,3806,3810,3813,3815,3814,3816,3817,3818,3819,3829,3831]
    #[3833,3834,3835,3836,3837,3839,3840,3842,3843,3844,3845,3846,3848,3841,3851,3832,3854,3856,3857,3858,3867,3868,3872,3874,3892,3821,3992,3993,3994,3995,4019,4020,4023,3838,4040,4041,3850,4045,4047,4066,4076,3853,4084,3852,4097,4099,4100,4112,3764,4158,4171,4196,4201,4203,4205,4206,4209,4212,4231,4043,3847,3830,4265,4274,4275,3855,4251,4254,4276,3828,4283,4281,4284,4081,4289,4290,4291,4292,4294,4295,3809,4298,4326,4328,4296,4399,4414,4415,4416,4425,4433,4402,4299,4453,4543,4544,4483,4377,3771,4582,4581,2990,4498,4354,4584,4588,4596,4598,4476,4280,4600,4601,4604,4606,4613,4614,4379,4605,4618,4619,4623,4627,4629,4630,4631,4632,4634,4635,4636,4626,4637,4638,4639,4640,4641,4642,4643,4644,4645,4646,4648,4650,4651,4652,4653,4620,4621,4654,4633,4628,4656,4657,4665,4668,4655,4667,4669,4670,4671,4672,4673,4674,4675,4676,4677,4678,4679,4680,4681,4683,4685,4687,4690,4692,4691,4693,4694,4695,4696,4697,4698,4700,4734]
    #[4781,3703,4796,4818,4823,4878,4892,4420,4917,3823,4920,4921,4922,4923,4924,4925,4927,4877,4928,4930,4931,4932,4934,4935,4936,4938,4939,4940,4941,4942,4948,4949,4950,4951,4952,4956,4958,4967,4968,4969,4976,4980,4981,4982,4983,4985,4987,4988]
    # spatial_batch_ids = [4775]
    # for id in spatial_batch_ids:
    #    # hard code parameters for debugging
    #    param_range_map_id = arcpy.Parameter()
    #    param_range_map_id.value = str(id)
    #    param_spatial = arcpy.Parameter()
    #    param_spatial.value = 'true'
    #    parameters = [param_range_map_id, param_spatial]
    #    prm.runPublishRangeMapTool(parameters, None)
    
    # non_spatial_batch_ids = [623,629,705,717,718,723,864,1095,1099,1101,1132,1163,1181,1239,1731,1738,1740,1742,1744,1745,1242,1757,1806,1820,1821,1879,1795,2490,2500,2503,2505,2507,2508,2509,2510,2511,2514,2516,2518,2523,2524,2525,2526,2527,2528,2529,2530,2531,2532,2533,2534,2535,2537,2538,2539,2540,2542,2543,2548,2555,2565,2567,2571,2575,2577,2578,2579,2580,2581,2582,2583,2584,2586,2587,2588,2589,2590,2591,2546,2607,2608,2563,2573,2574,2585,2566,2559,2560,2648,2656,2986,2989,2991,2988,3051,3054,3056,3057,3065,3066,3070,3108,3172,3195,3198,3213,3197,3244,3258,3271,3272,3286,3288,3289,3291,3293,3589,3593,3283,1756,3471,3779,4074,4210,4211,4277,4279,4287,4444,4616,4625,4647,4649,4658,4660,4661,4662,4663,4686,4689,4699,4702,4701,4362,4919,4929]
    #non_spatial_batch_ids = [2900,2902,2355,4844,2766,3332,3940,3427,601,2700,3240,3013,3385,4339,311,4903,4221,326,3420,3534,3431,753,3335,3358,4946,4947,3352,3697,3606,3414,298,2816,3329,3617,1637,3600,3698,3586,4046,4130,4150,4954,4144,3989,4262,3668,4232,4160,2739,4025,3981,3548,3968,2742,4056,3970,4012,3541,4147,2748,3916,3820,4134,4230,4208,3965,3986,3912,3998,4148,4062,4116,4953,4959,4960,4219,2150,4337,4816,3442,3424,3351,3280,3609,4014,4218,4224,4971,4226,4961,3003,3004,3106,4013,3152,2740,3925,4970,4972,2595,4882,4874,4782,3009,4135,2823,4039,4151,4228,4022,4247,4191,4035,4170,4051,4225,3939,4070,3863,4264,4143,3860,4106,4080,3936,4006,4238,3950,4214,4119,4087,4007,3942,3859,3952,4133,3959,4036,4033,4194,4117,3978,3972,4109,3947,4049,4234,4126,4101,4179,4152,4168,4198,4052,4108,3991,4261,4270,4256,4268,4252,4028,3887,3946,3985,4272,4167,4053,4075,3903,4050,3754,3886,4190,4185,4193,3935,3937,4188,4015,4227,4092,4120,3996,3999,4057,4123,4178,4249,3899,3929,3900,4121,3908,3983,4085,4067,3964,3945,3927,3873,4090,3938,4042,4263,4180,3954,4083,4269,4239,4215,3953,3883,3911,4166,3958,3944,4065,4098,3884,3877,3865,4061,3924,4024,4236,4260,4038,3894,4192,4073,4125,3917,4059,3901,3943,3923,3971,4195,4011,4055,4072,4153,3928,4017,4233,3982,4138,4118,3862,3926,4164,4271,4063,3906,4189,3931,4146,4142,4037,3890,4079,3913,4021,3987,4086,4009,4223,4129,4102,3915,4077,3898,4245,4044,4005,4157,3956,4181,4207,3962,4240,4064,4137,4235,3902,4124,3933,3880,4267,3932,3542,3920,4004,3949,4029,4177,4173,4172,4200,4000,4186,4237,4145,3941,4107,4176,4139,3879,3980,4258,4273,3888,3897,3948,3922,3930,4255,4105,4031,4197,3957,4175,4002,3966,4088,4155,4246,4202,4082,4127,3951,4141,4110,4091,4104,3870,4114,4140,4071,4163,3910,4259,3905,4222,4122,4229,3976,3984,4078,4165,3876,3808,3864,3909,4026,4016,4204,4257,3969,4154,4213,4250,4159,4136,4182,4266,3881,4184,4010,3979,4113,4032,4253,3934,3889,4169,3907,4048,4060,4128,4174,4156,4093,4162,4161,3997,3896,3895,3967,3974,4094,4018,4001,4103,4115,3918,4463,3914,3977,3975,4068,4243,4242,4003,4241,4199,4034,3960,4027,2819,4069,3878,3961,4089,4220,4963,4216,4817,3551,3346,4248,4008,3328,3397,3582,3353,3866,3882,3973,4183,4132,4827,4792,3415,3990,3988,4790,3885,3904,3955,4217,3919,3411,3598,3357,4030,3434,3327,4945,4149,3921,4058,3437,4131,4244,3438,3379,4366,3693,3384,3350,4054,4096,4111,3430,3378,3330,4973,4974,4828,4840,4341,4303,4611,4314,4787]
    non_spatial_batch_ids = [326,753,2819,3003,3004,3076,3328,3335,3350,3378,3397,3430,3431,3437,3551,3609,3411,3697,3940,4147,4149,4144,4339,4787,4840,4972,2442,3225,4363,4568,4870,4873,4015,4532,4181,3251,3302,3655,3330,3420,3442,2700,4946,4947,3438,236,4226,4008,3904,4869,4842,3895,3434,4933,3280,3414,3327,601,4853,4535,4135,1637,4333,4106,3870,4908,4030,4061,4104,4361,4037,4219,3808,3794,4859,2595,3152,4029,4240,3965,3977,4303,4101,4146,3879,4834,4191,4874,3192,4217,3921,3013,4954,4890,4515,4094,4266,3926,4118,4540,4091,3113,4159,4273,3922,3983,3916,4103,3989,4178,3358,2902,3478,3617,4795,3918,4445,4569,4157,3913,4123,4039,3986,4179,4480,4961,298,3329,4554,4531,3880,3554,4017,4798,4508,4257,4320,3541,3278,4186,3998,4826,4185,4193,3914,3534,3415,2823,4001,4236,3984,4550,4105,4082,4051,3907,4049,4364,3304,3600,4314,2355,4208,4899,4864,4067,4070,4807,3106,3898,3876,4169,4160,4141,4139,4215,3927,4256,4464,4369,3968,4054,4457,4128,4443,4255,3595,3900,4260,3971,3950,4558,4046,3997,3903,4262,3938,4784,3897,3990,4248,4137,3974,3934,4170,3956,4048,3427,4089,3919,4142,3889,4527,3548,3351,3352,4220,4223,3960,4011,4805,4003,4267,4134,4172,3902,4117,3384,4162,3586,4222,3929,3924,3877,4031,3933,4200,4122,4809,3894,3910,3952,4513,4247,4865,3936,4065,4526,4207,4246,4024,3939,3226,4574,4374,311,3246,4183,4844,4881,4815,3951,4894,3424,4085,3567,2742,3985,4005,4140,4797,4828,4102,3969,4012,3996,4092,3976,4905,4245,4250,4524,4204,3820,3981,3979,4269,4063,2964,3943,2900,2150,3970,3865,3942,4133,4035,4235,3188,3899,4098,4850,4042,4077,3881,3905,4282,4175,4234,4053,4233,3909,4456,4782,4261,4110,3945,4016,4512,4799,4078,4904,4533,4218,3896,3932,3937,4154,4599,3915,4129,4241,4264,3958,4243,4036,3882,4575,4188,4013,4083,4237,4107,4027,4127,4197,4272,4164,4863,4249,3923,4000,3866,4079,4221,4887,4002,4791,3911,4814,3920,4165,4841,4125,3941,4970,3233,670,4232,4786,4557,4829,4268,4216,4822,4341,3606,4817,4007,4516,4176,4910,4056,4026,4472,4876,3253,3906,4050,4852,2891,4440,4202,4812,3884,4821,4835,4062,3980,4080,3944,4038,4523,4559,4025,4547,4368,4018,3276,3959,4230,4514,4192,2513,4168,4893,4783,4963,3706,4454,4827,4180,4177,4259,4150,4022,4052,4166,4595,4519,4228,4060,4451,4161,3953,4153,3886,4571,4156,3967,3571,4971,3385,3332,4111,4058,2816,3346,3582,4851,4439,4862,4229,4034,4960,4174,4167,3973,2635,4258,4831,4087,4959,3928,4148,3949,4551,3901,3982,2740,4252,3888,4173,4136,4511,4006,4502,3353,3917,4114,4882,4376,4880,4461,4549,3357,4611,3930,4911,4072,4010,3568,4182,4857,3991,2727,4189,4430,4820,4096,4945,4145,4903,3379,4875,4888,4521,3947,4530,3946,4028,3961,4113,3754,3912,4858,4090,3972,3890,3864,4578,4059,4057,3962,4885,3935,4069,4986,4225,4906,4792,4143,4121,4541,4546,3954,4071,4570,4138,4790,3878,4032,4886,3240,4337,4973,3863,4244,4109,4131,4897,4108,4195,3931,4907,4044,3948,3975,4014,4562,4891,3883,3908,3925,4130,3698,4115,4068,4198,4093,3570,4270,4132,4199,4468,4366,1261,4816,4825,4810,4151,4459,3964,4839,4213,4227,4214,4120,3957,4086,4463,3988,4009,4449,4824,4190,4895,4507,4116,4033,4004,4884,2739,4424,2748,4953,3999,4224,4901,4238,4055,4075,3542,4021,4860,3862,4073,3860,4184,4900,2766,4477,3955,3873,4239,4119,4684,4563,4253,3668,3978,4152,4194,3009,4974,4926,4124,3885,3598,3693,4500,3887,4088,4271,4126,3812,4163,4242,3966,4408,4155,4263,3859,4064,3987]
    for id in non_spatial_batch_ids:
        # hard code parameters for debugging
        param_range_map_id = arcpy.Parameter()
        param_range_map_id.value = str(id)
        param_spatial = arcpy.Parameter()
        param_spatial.value = 'false'
        parameters = [param_range_map_id, param_spatial]
        prm.runPublishRangeMapTool(parameters, None)
