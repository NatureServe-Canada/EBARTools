# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Samantha Stefanoff
# © NatureServe Canada 2025 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: CreateExternalRangeReviewFromEbirdAbundance.py
# ArcGIS Python tool for creating an external range review table from eBird Abundance raster(s)

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import arcpy
import datetime
import EBARUtils
#import urllib.request
import requests


class CreateExternalRangeReviewFromEbirdAbundanceTool:
    """Create an external range review table from eBird Abundance raster(s)"""
    def __init__(self):
        pass

    def runCreateExternalRangeReviewFromEbirdAbundanceTool(self, parameters, messages):
        # check out any needed extension licenses
        arcpy.CheckOutExtension('Spatial')

        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        arcpy.env.overwriteOutput = True

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        param_geodatabase = parameters[0].valueAsText
        param_ebird_full_year_raster = parameters[1].valueAsText
        EBARUtils.displayMessage(messages, 'Full Year Raster: ' + param_ebird_full_year_raster)
        param_ebird_breeding_season_raster = parameters[2].valueAsText
        EBARUtils.displayMessage(messages, 'Breeding Season Raster: ' + param_ebird_breeding_season_raster)
        param_label = parameters[3].valueAsText
        EBARUtils.displayMessage(messages, 'Label: ' + param_label)
        param_percent_of_population_cutoff = parameters[4].valueAsText
        EBARUtils.displayMessage(messages, 'Percent of Population Cutoff: ' + param_percent_of_population_cutoff)
        # param_year = parameters[4].valueAsText
        # EBARUtils.displayMessage(messages, 'Year: ' + param_year)

        # use passed geodatabase as workspace for temp outputs
        arcpy.env.workspace = param_geodatabase

        # full year raster is required
        # download fails with 500 error using two different methods despite URLs working correctly in browser!
        # EBARUtils.displayMessage(messages, 'Downloading Full Year raster')
        # url = EBARUtils.ebird_download_url + '?objkey=' + param_year + '/' + param_label + '/web_download/seasonal/' + \
        #       param_label + '_abundance_seasonal_full-year_mean_' + param_year + '.tif&key=' + EBARUtils.ebird_api_key
        # full_year_tif = EBARUtils.temp_folder + '/full_year.tif'
        # #urllib.request.urlretrieve(url, full_year_tif)
        # response = requests.get(url)
        # if response.status_code == 200:
        #     with open(full_year_tif, 'wb') as file:
        #         file.write(response.content)
        # else:
        #     EBARUtils.displayMessage(messages, 'ERROR: Failed to Download Full Year raster with status code ' +
        #                              str(response.status_code))
        #     return
        EBARUtils.displayMessage(messages, 'Processing Full Year raster')
        self.ProcessRaster(messages, param_ebird_full_year_raster, param_percent_of_population_cutoff,
                           param_label, True)
        # self.ProcessRaster(messages, full_year_tif, param_percent_of_population_cutoff, param_label, True)
        # arcpy.Delete_management(full_year_tif)

        # breeding season raster is optional
        if param_ebird_breeding_season_raster:
            EBARUtils.displayMessage(messages, 'Processing Breeding Season raster')
            self.ProcessRaster(messages, param_ebird_breeding_season_raster, param_percent_of_population_cutoff,
                               param_label, False)
            
        # export to CSV
        arcpy.ExportTable_conversion(param_geodatabase + '/' + param_label + '_' + param_percent_of_population_cutoff,
                                     EBARUtils.download_folder + '/' + param_label + '_' +
                                     param_percent_of_population_cutoff + '.csv')
        EBARUtils.displayMessage(messages, 'Output CSV: ' + EBARUtils.download_url + '/' + param_label + '_' +
                                 param_percent_of_population_cutoff + '.csv')
        arcpy.Delete_management(param_geodatabase + '/' + param_label + '_' + param_percent_of_population_cutoff)


    def ProcessRaster(self, messages, ebird_raster, percent_of_population_cutoff,
                      label, is_full_year):
        # Extract by Mask to Canada
        EBARUtils.displayMessage(messages, 'Extracting by Mask for Canada only')
        arcpy.MakeFeatureLayer_management(EBARUtils.ebar_feature_service + '/3', 'cdn_ecoshapes',
                                          'JurisdictionID IN ' + EBARUtils.national_jur_ids)
        cdn_raster = arcpy.sa.ExtractByMask(ebird_raster, 'cdn_ecoshapes', 'INSIDE')
        #cdn_raster.save('cdn_raster')

        # Extract by Attributes to positive
        EBARUtils.displayMessage(messages, 'Extracting by Attributes for positive only')
        pos_raster = arcpy.sa.ExtractByAttributes(cdn_raster, 'VALUE > 0')
        #pos_raster.save('pos_raster')
        arcpy.Delete_management(cdn_raster)

        # Raster X 1M
        EBARUtils.displayMessage(messages, 'Multiplying by 1,000,000')
        times_raster = arcpy.sa.Times(pos_raster, 1000000)
        times_raster.save('times_raster')
        arcpy.Delete_management(pos_raster)

        # Raster1M + 0.5
        EBARUtils.displayMessage(messages, 'Adding 0.5')
        plus_raster = arcpy.sa.Plus('times_raster', 0.5)
        plus_raster.save('plus_raster')
        arcpy.Delete_management('times_raster')
        arcpy.Delete_management(times_raster)

        # Integer Raster
        EBARUtils.displayMessage(messages, 'Converting to integer')
        integer_raster = arcpy.sa.Int('plus_raster')
        integer_raster.save('integer_raster')
        arcpy.Delete_management('plus_raster')
        arcpy.Delete_management(plus_raster)

        # Raster to Point
        # needed to ensure every cell gets included in sum
        # raster to polygon combines neighbouring cells with the same value!!!
        EBARUtils.displayMessage(messages, 'Converting to point')
        arcpy.RasterToPolygon_conversion('integer_raster', 'points', 'NO_SIMPLIFY', 'VALUE')

        # Summary Statistics for sum/population
        EBARUtils.displayMessage(messages, 'Calculating total population')
        arcpy.Statistics_analysis('points', 'stats', [['gridcode', 'SUM']])
        total_pop = 0
        row = None
        with arcpy.da.SearchCursor('stats', ['SUM_gridcode']) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                total_pop = row['SUM_gridcode']
        del cursor
        if row:
            del row
        arcpy.Delete_management('stats')
        arcpy.Delete_management('points')

        # Raster to Polygon
        EBARUtils.displayMessage(messages, 'Converting to polygon')
        arcpy.RasterToPolygon_conversion('integer_raster', 'polygons', 'NO_SIMPLIFY', 'VALUE')
        arcpy.Delete_management('integer_raster')
        arcpy.Delete_management(integer_raster)

        # Percent Population Cutoff
        # for percent_of_population_cutoff in percent_of_population_cutoffs:
        EBARUtils.displayMessage(messages, 'Determining cutoff for ' + percent_of_population_cutoff)
        minimum = self.PercentPopulationCutoff('polygons', total_pop, percent_of_population_cutoff)

        # Select above cutoff
        EBARUtils.displayMessage(messages, 'Applying cutoff for ' + percent_of_population_cutoff)
        arcpy.MakeFeatureLayer_management('polygons', 'included_polygons', 'gridcode > ' + str(minimum))

        # Intersect with ecoshapes
        EBARUtils.displayMessage(messages, 'Intersecting ecoshapes')
        arcpy.SelectLayerByLocation_management('cdn_ecoshapes', 'INTERSECT', 'included_polygons',
                                            selection_type='NEW_SELECTION')
        arcpy.Delete_management('included_polygons')

        # Output to table
        EBARUtils.displayMessage(messages, 'Outputting to table')
        output_table = label + '_' + percent_of_population_cutoff
        if is_full_year:
            # Create table with one Present record for each EcoshapeID
            field_mappings = arcpy.FieldMappings()
            field_mappings.addFieldMap(EBARUtils.createFieldMap('cdn_ecoshapes', 'EcoshapeID', 'EcoshapeID', 'LONG'))
            arcpy.ExportTable_conversion('cdn_ecoshapes', output_table, field_mapping=field_mappings)
            arcpy.AddField_management(output_table, 'Presence', 'TEXT')
            arcpy.CalculateField_management(output_table, 'Presence', "'P'")
        else:
            # # Create table with one Breeding record for each EcoshapeID
            # field_mappings = arcpy.FieldMappings()
            # field_mappings.addFieldMap(EBARUtils.createFieldMap('cdn_ecoshapes', 'EcoshapeID', 'EcoshapeID', 'LONG'))
            # arcpy.ExportTable_conversion('cdn_ecoshapes', output_table + 'U', field_mapping=field_mappings)
            # arcpy.AddField_management(output_table + 'U', 'UsageType', 'TEXT')
            # arcpy.CalculateField_management(output_table + 'U', 'UsageType', "'B'")

            # Update table with UsageType = Breeding for each EcoshapeID
            arcpy.AddField_management(output_table, 'UsageType', 'TEXT')

            # loop through ecoshapes because records may need to be added or updated
            ecoshape_row = None
            with arcpy.da.SearchCursor('cdn_ecoshapes', ['EcoshapeID']) as ecoshape_cursor:
                for ecoshape_row in EBARUtils.searchCursor(ecoshape_cursor):
                    # update if row already exists
                    update_row = None
                    with arcpy.da.UpdateCursor(output_table, ['UsageType'],
                                                'EcoshapeID = ' + str(ecoshape_row['EcoshapeID'])) as update_cursor:
                        for update_row in EBARUtils.updateCursor(update_cursor):
                            update_cursor.updateRow(['B'])
                    del update_cursor
                    if update_row:
                        del update_row
                    else:
                        # insert row
                        with arcpy.da.InsertCursor(output_table,
                                                    ['EcoshapeID', 'Presence', 'UsageType']) as insert_cursor:
                            insert_cursor.insertRow([ecoshape_row['EcoshapeID'], 'P', 'B'])
                        del insert_cursor

            # # export selected ecoshapes to temp because used in a join
            # field_mappings = arcpy.FieldMappings()
            # field_mappings.addFieldMap(EBARUtils.createFieldMap('cdn_ecoshapes', 'EcoshapeID', 'EcoshapeID', 'LONG'))
            # arcpy.ExportTable_conversion('cdn_ecoshapes', 'breeding_ecoshapes_table', field_mapping=field_mappings)
            # arcpy.AddJoin_management(output_table, 'EcoshapeID', 'breeding_ecoshapes_table', 'EcoshapeID',
            #                         'KEEP_COMMON')
            # arcpy.CalculateField_management(output_table, 'UsageType', "'B'")
            #arcpy.RemoveJoin_management(output_table, 'breeding_ecoshapes_table')
            # arcpy.Delete_management('breeding_ecoshapes_table')
        arcpy.Delete_management('polygons')
        arcpy.Delete_management('cdn_ecoshapes')


    def PercentPopulationCutoff(self, population_table, total_pop, cutoff_percent):
        cutoff = round(total_pop * int(cutoff_percent) / 100)
        row = None
        prev_pop = 0
        total = 0
        with arcpy.da.SearchCursor(population_table, ['gridcode'],
                                   sql_clause=[None,'ORDER BY gridcode ASC']) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                total += row['gridcode']
                if total > cutoff:
                    return prev_pop
                prev_pop = row['gridcode']
        del cursor
        if row:
            del row
        return prev_pop


# controlling process
if __name__ == '__main__':
    cerrfea = CreateExternalRangeReviewFromEbirdAbundanceTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'D:/GIS/EBAR/EBAR.gdb' #'C:/GIS/EBAR/nsc-gis-ebarkba.sde'
    param_ebird_full_year_raster = arcpy.Parameter()
    param_ebird_full_year_raster.value = "D:/GIS/eBird/eBird Status and Trends/eBird Raster Files/Solitary Sandpiper/solsan_abundance_seasonal_full-year_mean_2022.tif"
    param_ebird_breeding_season_raster = arcpy.Parameter()
    param_ebird_breeding_season_raster.value = "D:/GIS/eBird/eBird Status and Trends/eBird Raster Files/Solitary Sandpiper/solsan_abundance_seasonal_breeding_mean_2022.tif"
    param_label = arcpy.Parameter()
    param_label.value = 'solsan'
    param_percent_of_population_cutoff = arcpy.Parameter()
    param_percent_of_population_cutoff.value = 5
    # param_year = arcpy.Parameter()
    # param_year.value = 2023
    parameters = [param_geodatabase, param_ebird_full_year_raster, param_ebird_breeding_season_raster,
                  param_label, param_percent_of_population_cutoff] #, param_year]
    cerrfea.runCreateExternalRangeReviewFromEbirdAbundanceTool(parameters, None)
