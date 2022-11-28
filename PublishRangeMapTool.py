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
        with arcpy.da.SearchCursor('species_view', ['Endemism']) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                if row['Endemism']:
                    endemism_type = row['Endemism']
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
                                    'FORMATTED_FULL_CITATION', 'COSEWIC_NAME', 'COSEWIC_ID']) as cursor:
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
                #global_unique_id = global_unique_id.replace('-', '.')
                nsx_url = 'https://explorer.natureserve.org/Taxon/' + global_unique_id
                pdf_html = pdf_html.replace('[NSE2.0_URL]', nsx_url)
                cosewic_name = ''
                if row['COSEWIC_NAME']:
                    cosewic_name = row['COSEWIC_NAME']
                pdf_html = pdf_html.replace('[BIOTICS_ELEMENT_NATIONAL.COSEWIC_NAME]',
                                            cosewic_name)
                cosewic_id = ''
                if row['COSEWIC_ID']:
                    cosewic_id = row['COSEWIC_ID']
                pdf_html = pdf_html.replace('[BIOTICS_ELEMENT_NATIONAL.COSEWIC_ID]',
                                            cosewic_id)
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
        differentiate_usage_type = False
        with arcpy.da.SearchCursor('range_map_view',
                                    ['SpeciesID', 'RangeVersion', 'RangeStage', 'RangeDate', 'RangeMapScope',
                                     'RangeMapNotes', 'RangeMetadata', 'RangeMapComments',
                                     'IncludeInDownloadTable', 'DifferentiateUsageType']) as cursor:
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
                if row['DifferentiateUsageType']:
                    differentiate_usage_type = True
        if range_map_scope:
            del row
        del cursor

        # # insert fixed list of reviewers by taxa
        # EBARUtils.displayMessage(messages, 'Inserting ReviewersByTaxa file')
        # reviewers_by_taxa_html = None
        # #reviewers = io.open(reviewers_by_taxa_file, 'r', encoding='mbcs') # mbcs encoding is Windows ANSI
        # #for reviewer_line in reviewers:
        # for reviewer_line in urllib.request.urlopen(reviewers_by_taxa_link):
        #     if not reviewers_by_taxa_html:
        #         reviewers_by_taxa_html = '<tr><th>Reviewers by Taxa:</th>'
        #     else:
        #         reviewers_by_taxa_html += '<tr><th></th>'
        #     # mbcs encoding is Windows ANSI
        #     reviewers_by_taxa_html += '<td>' + reviewer_line.decode('mbcs') + '</td></tr>'
        # pdf_html = pdf_html.replace('[ReviewersByTaxa]', reviewers_by_taxa_html)
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
                                                 'Ecoshape.shp', md, False)

            # export overview ecoshapes
            EBARUtils.displayMessage(messages, 'Exporting EcoshapeOverview polygons to shapefile')
            EBARUtils.ExportEcoshapeOverviewsToShapefile('ecoshape_overview_layer' + param_range_map_id,
                                                         'range_map_ecoshape_view' + param_range_map_id, zip_folder, 
                                                         'EcoshapeOverview.shp', md, False)

            # update ArcGIS Pro template
            EBARUtils.displayMessage(messages, 'Updating ArcGIS Pro template')
            EBARUtils.updateArcGISProTemplate(zip_folder, element_global_id, md, param_range_map_id, differentiate_usage_type)

            # copy ArcMap template
            EBARUtils.displayMessage(messages, 'Copying ArcMap template')
            shutil.copyfile(EBARUtils.resources_folder + '/EBAR.mxd',
                            zip_folder + '/EBAR' + element_global_id + '.mxd')
            if differentiate_usage_type:
                shutil.copyfile(EBARUtils.resources_folder + '/UsageType.lyr',
                                zip_folder + '/EBAR' + element_global_id + 'UsageType.lyr')
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
            # attempt to overcome GP service holding a hook into the folder
            del zip_folder

        return


# controlling process
if __name__ == '__main__':
    prm = PublishRangeMapTool()
    
    # spatial_batch_ids = [2341,2339,2340,2342,2344,2322,2323,2325,2326,2327,2328,2329,2330,2331,2332,2333,2334,2335,
    #                      2336,2337,2338,2324,1283,2315,2237,2240,2239,2238,2313,2311,2241,2308,2306,2307,2309,2305,
    #                      2356,2357,2358,2363,2367,2368,2369,2370,2359,2360,2361,2362,2364,2365,2366]
    spatial_batch_ids = [2829]
    for id in spatial_batch_ids:
       # hard code parameters for debugging
       param_range_map_id = arcpy.Parameter()
       param_range_map_id.value = str(id)
       param_spatial = arcpy.Parameter()
       param_spatial.value = 'true'
       parameters = [param_range_map_id, param_spatial]
       prm.runPublishRangeMapTool(parameters, None)
    
    # #non_spatial_batch_ids = [85,288,311,457,557,559,616,617,618,620,621,624,627,630,637,658,662,670,689,708,713,721,722,733,747,752,778,794,841,843,844,869,928,1093,1101,1102,1103,1105,1112,1115,1120,1121,1123,1124,1131,1133,1134,1136,1138,1139,1144,1145,1147,1149,1184,1187,1278,1283,1341,1344,1497,1503,1504,1507,1508,1516,1518,1587,1592,1603,1609,1617,1622,1624,1644,1646,1647,1658,1703,1707,1718,1723,1724,1729,1740,1747,1761,1769,1777,1781,1784,1795,1805,1809,1810,1822,1825,1847,1848,1871,1873,1874,1875,1876,1879,1880,1896,1922,1923,1925,1927,1928,1929,1931,1932,1933,1934,1937,1938,1940,1941,1947,1957,1961,1962,1963,1964,1968,1999,2000,2010,2015,2016,2020,2024,2025,2028,2046,2053,2063,2068,2072,2073,2074,2075,2076,2078,2079,2084,2086,2089,2097,2102,2103,2110,2112,2114,2115,2116,2119,2120,2121,2122,2123,2124,2125,2126,2127,2131,2132,2138,2143,2144,2145,2154,2155,2158,2161,2162,2164,2165,2166,2167,2168,2170,2172,2175,2178,2180,2181,2182,2183,2188,2190,2191,2192,2195,2197,2199,2201,2204,2206,2208,2209,2210,2213,2214,2216,2220,2223,2227,2231,2235,2237,2238,2241,2243,2247,2248,2254,2255,2256,2260,2262,2264,2265,2266,2267,2268,2269,2270,2271,2272,2274,2275,2278,2279,2280,2282,2283,2284,2287,2288,2289,2290,2292,2293,2307,2309,2313,2316,2317,2318,2321,2324,2334,2342,2344,2346,2347,2350,2351,2355,2356,2357,2358,2359,2360,2361,2362,2363,2364,2365,2366,2367,2368,2369,2370,2375,2376,2377,2381,2382,2383,2384,2385,2386,2387,2388,2389,2390,2391,2392,2393,2398,2402,2405,2407,2409,2412,2413,2414,2415,2416,2417,2418,2419,2420,2421,2423,2424,2425,2426,2427,2428,2429,2430,2431,2432,2433,2434,2435,2436,2437,2438,2439,2440,2442,2443,2444,2445,2446,2447,2448,2450,2452,2453,2460,2461,2462,2463,2464,2465,2469,2470,2471,2474,2475,2476,2477,2478,2480,2482,2487,2489,2490,2491,2492,2493,2497,2498,2499,2500,2501,2502,2503,2506,2511,2512,2513,2514,2517,2518,2519,2521,2522,2523,2524,2526,2527,2528,2530,2531,2533,2535,2536,2537,2539,2540,2542,2544,2546,2548,2550,2551,2554,2555,2556,2557,2558,2559,2560,2561,2563,2564,2565,2566,2567,2568,2569,2570,2571,2572,2573,2574,2575,2576,2577,2578,2579,2580,2581,2582,2583,2584,2585,2586,2587,2588,2589,2590,2591,2594,2595,2596,2597,2598,2599,2606,2607,2608,2610,2611,2612,2616,2618,2619,2621,2624,2625,2626,2628,2629,2630,2631,2632,2633,2634,2635,2636,2637,2638,2639,2640,2641,2642,2643,2644]
    # #non_spatial_batch_ids = [52,616,624,630,633,634,635,636,637,638,639,640,641,670,680,685,689,706,707,708,709,712,713,747,749,824,862,866,867,869,870,1087,1102,1103,1112,1113,1128,1129,1130,1131,1133,1134,1136,1140,1143,1144,1145,1149,1151,1154,1155,1156,1179,1187,1190,1225,1227,1231,1233,1241,1254,1261,1278,1283,1296,1747,1780,1823,1840,1861,1871,1875,1878,1880,2309,2315,2339,2369,2395,2398,2399,2409,2410,2411,2413,2414,2421,2439,2440,2443,2444,2445,2446,2447,2448,2453,2462,2463,2468,2471,2474,2481,2618,2621,2628,2636]
    # non_spatial_batch_ids = [73]
    # for id in non_spatial_batch_ids:
    #     # hard code parameters for debugging
    #     param_range_map_id = arcpy.Parameter()
    #     param_range_map_id.value = str(id)
    #     param_spatial = arcpy.Parameter()
    #     param_spatial.value = 'false'
    #     parameters = [param_range_map_id, param_spatial]
    #     prm.runPublishRangeMapTool(parameters, None)
