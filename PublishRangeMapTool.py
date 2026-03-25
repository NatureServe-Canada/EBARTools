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
        for suffix in ('_en', '_fr'):
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
        pdfkit.from_string(pdf_html_en, EBARUtils.download_folder + '/EBAR' + element_global_id + '.pdf', pdf_options)
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
    spatial_batch_ids = [3833,3834,3835,3836,3837,3839,3840,3842,3843,3844,3845,3846,3848,3841,3851,3832,3854,3856,3857,3858,3867,3868,3872,3874,3892,3821,3992,3993,3994,3995,4019,4020,4023,3838,4040,4041,3850,4045,4047,4066,4076,3853,4084,3852,4097,4099,4100,4112,3764,4158,4171,4196,4201,4203,4205,4206,4209,4212,4231,4043,3847,3830,4265,4274,4275,3855,4251,4254,4276,3828,4283,4281,4284,4081,4289,4290,4291,4292,4294,4295,3809,4298,4326,4328,4296,4399,4414,4415,4416,4425,4433,4402,4299,4453,4543,4544,4483,4377,3771,4582,4581,2990,4498,4354,4584,4588,4596,4598,4476,4280,4600,4601,4604,4606,4613,4614,4379,4605,4618,4619,4623,4627,4629,4630,4631,4632,4634,4635,4636,4626,4637,4638,4639,4640,4641,4642,4643,4644,4645,4646,4648,4650,4651,4652,4653,4620,4621,4654,4633,4628,4656,4657,4665,4668,4655,4667,4669,4670,4671,4672,4673,4674,4675,4676,4677,4678,4679,4680,4681,4683,4685,4687,4690,4692,4691,4693,4694,4695,4696,4697,4698,4700,4734,4775,4781,3703,4796,4818,4823,4878,4892,4420,4917,3823,4920,4921,4922,4923,4924,4925,4927,4877,4928,4930,4931,4932,4934,4935,4936,4938,4939,4940,4941,4942,4948,4949,4950,4951,4952,4956,4958,4967,4968,4969,4976,4980,4981,4982,4983,4985,4987,4988]
    for id in spatial_batch_ids:
       # hard code parameters for debugging
       param_range_map_id = arcpy.Parameter()
       param_range_map_id.value = str(id)
       param_spatial = arcpy.Parameter()
       param_spatial.value = 'true'
       parameters = [param_range_map_id, param_spatial]
       prm.runPublishRangeMapTool(parameters, None)
    
    # non_spatial_batch_ids = [623,629,705,717,718,723,864,1095,1099,1101,1132,1163,1181,1239,1731,1738,1740,1742,1744,1745,1242,1757,1806,1820,1821,1879,1795,2490,2500,2503,2505,2507,2508,2509,2510,2511,2514,2516,2518,2523,2524,2525,2526,2527,2528,2529,2530,2531,2532,2533,2534,2535,2537,2538,2539,2540,2542,2543,2548,2555,2565,2567,2571,2575,2577,2578,2579,2580,2581,2582,2583,2584,2586,2587,2588,2589,2590,2591,2546,2607,2608,2563,2573,2574,2585,2566,2559,2560,2648,2656,2986,2989,2991,2988,3051,3054,3056,3057,3065,3066,3070,3108,3172,3195,3198,3213,3197,3244,3258,3271,3272,3286,3288,3289,3291,3293,3589,3593,3283,1756,3471,3779,4074,4210,4211,4277,4279,4287,4444,4616,4625,4647,4649,4658,4660,4661,4662,4663,4686,4689,4699,4702,4701,4362,4919,4929]
    # for id in non_spatial_batch_ids:
    #     # hard code parameters for debugging
    #     param_range_map_id = arcpy.Parameter()
    #     param_range_map_id.value = str(id)
    #     param_spatial = arcpy.Parameter()
    #     param_spatial.value = 'false'
    #     parameters = [param_range_map_id, param_spatial]
    #     prm.runPublishRangeMapTool(parameters, None)
