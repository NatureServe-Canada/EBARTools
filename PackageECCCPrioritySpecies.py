# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Gabrielle Miller
# © NatureServe Canada 2022 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: PackageECCCPrioritySpeciesTool.py
# ArcGIS Python tool for creating Zip of PDFs and Spatial Data for all ECCC Priority Species

# Notes:
# - For one off or very occasional use only, so not integrated into the EBARTools toolbox
#   (see controlling process at the end of this file)


# import Python packages
import EBARUtils
import shutil
import arcpy
import datetime


class PackageECCCPrioritySpeciesTool:
    """Create Zip of PDFs and Spatial Data for all ECCC Priority Species"""
    def __init__(self):
        pass

    def processPackage(self, messages, range_map_ids, attributes_dict, zip_folder, metadata):
        # export range maps, with biotics/species additions
        EBARUtils.displayMessage(messages, 'Exporting RangeMap records to CSV')
        EBARUtils.ExportRangeMapToCSV('range_map_view_pkg', range_map_ids, attributes_dict, zip_folder, 'RangeMap.csv',
                                      metadata)

        # export range map ecoshapes
        EBARUtils.displayMessage(messages, 'Exporting RangeMapEcoshape records to CSV')
        EBARUtils.ExportRangeMapEcoshapesToCSV('range_map_ecoshape_view', range_map_ids, zip_folder,
                                               'RangeMapEcoshape.csv', metadata)

        # export ecoshapes
        EBARUtils.displayMessage(messages, 'Exporting Ecoshape polygons to shapefile')
        EBARUtils.ExportEcoshapesToShapefile('ecoshape_layer', 'range_map_ecoshape_view', zip_folder, 'Ecoshape.shp',
                                             metadata, True)

        # export overview ecoshapes
        EBARUtils.displayMessage(messages, 'Exporting EcoshapeOverview polygons to shapefile')
        EBARUtils.ExportEcoshapeOverviewsToShapefile('ecoshape_overview_layer', 'range_map_ecoshape_view', zip_folder, 
                                                     'EcoshapeOverview.shp', metadata, True)

        # copy ArcMap template
        EBARUtils.displayMessage(messages, 'Copying ArcMap template')
        #shutil.copyfile(EBARUtils.resources_folder + '/EBAR.mxd', zip_folder + '/EBAR ECCC Priority Species.mxd')
        shutil.copyfile(EBARUtils.resources_folder + '/EBAR.mxd', zip_folder + '/EBAR G1-3 High Quality.mxd')
        shutil.copyfile(EBARUtils.resources_folder + '/UsageType.lyr', zip_folder + '/UsageType.lyr')
        shutil.copyfile(EBARUtils.resources_folder + '/EcoshapeOverview.lyr', zip_folder + '/EcoshapeOverview.lyr')
        shutil.copyfile(EBARUtils.resources_folder + '/Ecoshape.lyr', zip_folder + '/Ecoshape.lyr')

        # create spatial zip
        # EBARUtils.displayMessage(messages, 'Creating ZIP: https://gis.natureserve.ca/download/' +
        #                          'EBAR ECCC Priority Species.zip')
        # EBARUtils.createZip(zip_folder,
        #                     EBARUtils.download_folder + '/EBAR ECCC Priority Species.zip', None)
        EBARUtils.displayMessage(messages, 'Creating ZIP: https://gis.natureserve.ca/download/' +
                                 'EBAR G1-3 High Quality.zip')
        EBARUtils.createZip(zip_folder,
                            EBARUtils.download_folder + '/EBAR G1-3 High Quality.zip', None)

        # create pdf zip
        # EBARUtils.displayMessage(messages, 'Creating ZIP: https://gis.natureserve.ca/download/' +
        #                          'EBAR ECCC Priority Species - All PDFs.zip')
        # EBARUtils.createZip(zip_folder,
        #                     EBARUtils.download_folder + '/EBAR ECCC Priority Species - All PDFs.zip','.pdf')
        EBARUtils.displayMessage(messages, 'Creating ZIP: https://gis.natureserve.ca/download/' +
                                 'EBAR G1-3 High Quality - All PDFs.zip')
        EBARUtils.createZip(zip_folder,
                            EBARUtils.download_folder + '/EBAR G1-3 High Quality - All PDFs.zip','.pdf')

    def runPackageECCCPrioritySpeciesTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True

        # make variables for parms
        #EBARUtils.displayMessage(messages, 'Processing parameters')

        # generate metadata
        EBARUtils.displayMessage(messages, 'Generating metadata')
        md = arcpy.metadata.Metadata()
        md.tags = 'Species Range, NatureServe Canada, Ecosystem-based Automated Range'
        md.description = 'See EBARxxxxx.pdf for per-species map and additional metadata, RangeMap.csv ' + \
            'for species attributes for each ELEMENT_GLOBAL_ID (xxxxx), and ' + \
            'EBARMethods.pdf for additional details. <a href="https://explorer.natureserve.org/">Go to ' + \
            'NatureServe Explorer</a> for information about the species.'
        md.credits = 'Copyright NatureServe Canada ' + str(datetime.datetime.now().year)
        md.accessConstraints = 'Publicly shareable under CC BY 4.0 (<a href=' + \
            '"https://creativecommons.org/licenses/by/4.0/">https://creativecommons.org/licenses/by/4.0/</a>)'

        # use EBAR BIOTICS table if can't get taxon API
        arcpy.MakeTableView_management(EBARUtils.ebar_feature_service + '/4', 'biotics_view')

        # loop all RangeMap records where IncludeInDownloadTable is populated and Publish=1
        arcpy.MakeTableView_management(EBARUtils.ebar_feature_service + '/11', 'range_map_view',
                                       'RangeMapID IN (616,624,633,634,635,636,637,638,639,640,641,680,685,689,706,707,708,709,712,713,747,749,824,862,866,867,869,870,1087,1102,1103,1112,1113,1128,1129,1130,1131,1133,1134,1136,1140,1143,1144,1145,1149,1151,1154,1155,1156,1179,1187,1190,1225,1227,1231,1233,1241,1254,1261,1283,1296,1747,1780,1823,1840,1861,1871,1875,1878,1880,2309,2315,2339,2369,2395,2398,2399,2409,2410,2411,2413,2414,2421,2439,2440,2443,2444,2445,2446,2447,2448,2453,2462,2463,2468,2471,2474,2481)')
                                       #'RangeMapID IN (85,288,311,457,557,559,616,617,618,620,621,624,627,630,637,658,662,670,689,708,713,721,722,733,747,752,778,794,841,843,844,869,928,1093,1101,1102,1103,1105,1112,1115,1120,1121,1123,1124,1131,1133,1134,1136,1138,1139,1144,1145,1147,1149,1184,1187,1278,1283,1341,1344,1497,1503,1504,1507,1508,1516,1518,1587,1592,1603,1609,1617,1622,1624,1644,1646,1647,1658,1703,1707,1718,1723,1724,1729,1740,1747,1761,1769,1777,1781,1784,1795,1805,1809,1810,1822,1825,1847,1848,1871,1873,1874,1875,1876,1879,1880,1896,1922,1923,1925,1927,1928,1929,1931,1932,1933,1934,1937,1938,1940,1941,1947,1957,1961,1962,1963,1964,1968,1999,2000,2010,2015,2016,2020,2024,2025,2028,2046,2053,2063,2068,2072,2073,2074,2075,2076,2078,2079,2084,2086,2089,2097,2102,2103,2110,2112,2114,2115,2116,2119,2120,2121,2122,2123,2124,2125,2126,2127,2131,2132,2138,2143,2144,2145,2154,2155,2158,2161,2162,2164,2165,2166,2167,2168,2170,2172,2175,2178,2180,2181,2182,2183,2188,2190,2191,2192,2195,2197,2199,2201,2204,2206,2208,2209,2210,2213,2214,2216,2220,2223,2227,2231,2235,2237,2238,2241,2243,2247,2248,2254,2255,2256,2260,2262,2264,2265,2266,2267,2268,2269,2270,2271,2272,2274,2275,2278,2279,2280,2282,2283,2284,2287,2288,2289,2290,2292,2293,2307,2309,2313,2316,2317,2318,2321,2324,2334,2342,2344,2346,2347,2350,2351,2355,2356,2357,2358,2359,2360,2361,2362,2363,2364,2365,2366,2367,2368,2369,2370,2375,2376,2377,2381,2382,2383,2384,2385,2386,2387,2388,2389,2390,2391,2392,2393,2398,2402,2405,2407,2409,2412,2413,2414,2415,2416,2417,2418,2419,2420,2421,2423,2424,2425,2426,2427,2428,2429,2430,2431,2432,2433,2434,2435,2436,2437,2438,2439,2440,2442,2443,2444,2445,2446,2447,2448,2450,2452,2453,2460,2461,2462,2463,2464,2465,2469,2470,2471,2474,2475,2476,2477,2478,2480,2482,2487,2489,2490,2491,2492,2493,2497,2498,2499,2500,2501,2502,2503,2506,2511,2512,2513,2514,2517,2518,2519,2521,2522,2523,2524,2526,2527,2528,2530,2531,2533,2535,2536,2537,2539,2540,2542,2544,2546,2548,2550,2551,2554,2555,2556,2557,2558,2559,2560,2561,2563,2564,2565,2566,2567,2568,2569,2570,2571,2572,2573,2574,2575,2576,2577,2578,2579,2580,2581,2582,2583,2584,2585,2586,2587,2588,2589,2590,2591,2594,2595,2596,2597,2598,2599,2606,2607,2608,2610,2611,2612,2616,2618,2619,2621,2624,2625,2626,2628,2629,2630,2631,2632,2633,2634,2635,2636,2637,2638,2639,2640,2641,2642,2643,2644)')
        # join BIOTICS_ELEMENT_NATIONAL to RangeMap
        arcpy.AddJoin_management('range_map_view', 'SpeciesID', EBARUtils.ebar_feature_service + '/4', 'SpeciesID',
                                 'KEEP_COMMON')
        # join Species to RangeMap
        arcpy.AddJoin_management('range_map_view', 'SpeciesID', EBARUtils.ebar_feature_service + '/19', 'SpeciesID',
                                 'KEEP_COMMON')
        processed = 0
        # use Python sorted (sql_clause ORDER BY doesn't work), which precludes use of EBARUtils.SearchCursor
        #where_clause = "L19Species.ECCC_PrioritySpecies = 'Yes'"

        # make zip folder
        #zip_folder = EBARUtils.temp_folder + '/EBAR ECCC Priority Species'
        zip_folder = EBARUtils.temp_folder + '/EBAR G1-3 High Quality'
        EBARUtils.createReplaceFolder(zip_folder)

        # copy static resources
        shutil.copyfile(EBARUtils.resources_folder + '/ReadmeSet.txt', zip_folder + '/Readme.txt')
        shutil.copyfile(EBARUtils.resources_folder + '/EBARMethods.pdf', zip_folder + '/EBARMethods.pdf')
        shutil.copyfile(EBARUtils.resources_folder + '/Jurisdiction.csv', zip_folder + '/Jurisdiction.csv')

        range_map_ids = []
        attributes_dict = {}
        row = None
        for row in sorted(arcpy.da.SearchCursor('range_map_view',
                          ['L4BIOTICS_ELEMENT_NATIONAL.CATEGORY',
                           'L4BIOTICS_ELEMENT_NATIONAL.TAX_GROUP',
                           'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_SCIENTIFIC_NAME',
                           'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_ENGL_NAME',
                           'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_FR_NAME',
                           'L4BIOTICS_ELEMENT_NATIONAL.ELEMENT_GLOBAL_ID',
                           'L4BIOTICS_ELEMENT_NATIONAL.GLOBAL_UNIQUE_IDENTIFIER',
                           'L11RangeMap.RangeMapScope',
                           'L11RangeMap.RangeMapID',
                           'L11RangeMap.IncludeInDownloadTable',
                           'L4BIOTICS_ELEMENT_NATIONAL.SpeciesID'])):
            processed += 1

            # copy pdf 
            EBARUtils.displayMessage(messages, 'Range Map ID: ' + str(row[8]))
            element_global_id = str(row[5])
            if row[7] == 'N':
                element_global_id += 'N'
            shutil.copyfile(EBARUtils.download_folder + '/EBAR' + element_global_id + '.pdf',
                            zip_folder + '/EBAR' + element_global_id + '.pdf')

            # set range map attributes
            range_map_ids.append(str(row[8]))
            arcpy.SelectLayerByAttribute_management('biotics_view', 'NEW_SELECTION', 'SpeciesID = ' + str(row[10]))
            attributes_dict[str(row[8])] = EBARUtils.getTaxonAttributes(row[6], element_global_id, row[8],
                                                                        messages)

            # update ArcGIS Pro template
            EBARUtils.displayMessage(messages, 'Updating ArcGIS Pro template')
            EBARUtils.updateArcGISProTemplate(zip_folder, element_global_id, md, row[8], False)

        if row:
            self.processPackage(messages, range_map_ids, attributes_dict, zip_folder, md)
            del row

        EBARUtils.displayMessage(messages, 'Processed ' + str(processed) + ' RangeMaps')
        return


# controlling process
if __name__ == '__main__':
    peps = PackageECCCPrioritySpeciesTool()
    parameters = []
    peps.runPackageECCCPrioritySpeciesTool(parameters, None)
