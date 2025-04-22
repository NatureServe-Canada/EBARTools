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

class CreateExternalRangeReviewFromEbirdAbundanceTool:
    """Generate Range Map for a species from available spatial data in the EBAR geodatabase"""
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
        param_ebird_breeding_season_raster = parameters[2].valueAsText
        param_label = parameters[3].valueAsText
        param_percent_of_population_cutoff = parameters[4].valueAsText
        param_external_range_review_table = parameters[5].valueAsText

        # use passed geodatabase as workspace
        arcpy.env.workspace = param_geodatabase

        # full year raster is required
        EBARUtils.displayMessage(messages, 'Processing full year raster')
        self.ProcessRaster(messages, param_geodatabase, param_ebird_full_year_raster, param_label,
                           int(param_percent_of_population_cutoff), param_external_range_review_table, True)

        # breeding season raster is optional
        if param_ebird_breeding_season_raster:
            EBARUtils.displayMessage(messages, 'Processing breeding season raster')
            self.ProcessRaster(messages, param_geodatabase, param_ebird_breeding_season_raster, param_label,
                               int(param_percent_of_population_cutoff), param_external_range_review_table, False)


    def ProcessRaster(self, messages, geodatabase, ebird_raster, label, percent_of_population_cutoff,
                      external_range_review_table, is_full_year):
        # Extract by Mask to Canada
        EBARUtils.displayMessage(messages, 'Extracting by Mask to Canada')
        arcpy.MakeFeatureLayer_management(geodatabase + '/Ecoshape', 'cdn_ecoshapes',
                                          'JurisdictionID IN ' + EBARUtils.national_jur_ids)
        cdn_raster = arcpy.sa.ExtractByMask(ebird_raster, 'cdn_ecoshapes', 'INSIDE')
        # Extract by Attributes to positive
        EBARUtils.displayMessage(messages, 'Extracting by Attributes to positive')
        pos_raster = arcpy.sa.ExtractByAttributes(cdn_raster, 'VALUE > 0')
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
        arcpy.Delete_management(times_raster)
        # Integer Raster
        EBARUtils.displayMessage(messages, 'Converting to integer')
        integer_raster = arcpy.sa.Int('plus_raster')
        integer_raster.save('integer_raster')
        arcpy.Delete_management(plus_raster)
        # Raster to Polygon
        EBARUtils.displayMessage(messages, 'Converting to polygon')
        arcpy.RasterToPolygon_conversion('integer_raster', label + '_polygons', 'NO_SIMPLIFY', 'VALUE')
        arcpy.Delete_management(integer_raster)
        # Summary Statistics for sum/population
        EBARUtils.displayMessage(messages, 'Calculating total population')
        arcpy.Statistics_analysis(label + '_polygons', label + '_stats', [['gridcode', 'SUM']])
        total_pop = 0
        row = None
        with arcpy.da.SearchCursor(label + '_stats', ['SUM_gridcode']) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                total_pop = row['SUM_gridcode']
        del cursor
        if row:
            del row
        # Percent Population Cutoff
        EBARUtils.displayMessage(messages, 'Determining cutoff')
        minimum = self.PercentPopulationCutoff(label + '_polygons', total_pop, percent_of_population_cutoff)
        # Select above cutoff
        EBARUtils.displayMessage(messages, 'Applying cutoff')
        arcpy.MakeFeatureLayer_management(label + '_polygons', 'included_polygons',
                                          'gridcode > ' + minimum)
        # Intersect with ecoshapes
        EBARUtils.displayMessage(messages, 'Intersecting ecoshapes')
        arcpy.SelectLayerByLocation_management('cdn_ecoshapes', 'INTERSECT', 'included_polygons',
                                               selection_type='NEW_SELECTION')
        if is_full_year:
            # Create table with one Present record for each EcoshapeID
            field_mappings = arcpy.FieldMappings()
            field_mappings.addFieldMap(EBARUtils.createFieldMap('cdn_ecoshapes', 'EcoshapeID', 'EcoshapeID', 'LONG'))
            arcpy.ExportTable_conversion('cdn_ecoshapes', external_range_review_table, field_mapping=field_mappings)
            arcpy.AddField_management(external_range_review_table, 'Presence', 'TEXT')
            arcpy.CalculateField_management(external_range_review_table, 'Presence', "'P'")
        else:
            # Update table with UsageType = Breeding for each EcoshapeID
            arcpy.AddField_management(external_range_review_table, 'UsageType', 'TEXT')
            arcpy.AddJoin_management('cdn_ecoshapes', 'EcoshapeID', external_range_review_table, 'EcoshapeID',
                                     'KEEP_COMMON')
            arcpy.CalculateField_management('cdn_ecoshapes', 'UsageType', "'B'")
            

    def PercentPopulationCutoff(self, population_table, total_pop, cutoff_percent):
        cutoff = round(total_pop * cutoff_percent / 100)
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
    param_geodatabase.value = 'D:/GIS/EBAR/EBAR-KBA-Dev.gdb'
    param_ebird_full_year_raster = arcpy.Parameter()
    param_ebird_full_year_raster.value = "D:/GIS/eBird/eBird Status and Trends/eBird Raster Files/Lewis's Woodpecker/lewwoo_abundance_seasonal_breeding_mean_2022.tif"
    param_ebird_breeding_season_raster = arcpy.Parameter()
    param_ebird_breeding_season_raster.value = None
    param_label = arcpy.Parameter()
    param_label.value = 'lewwoo'
    param_percent_of_population_cutoff = arcpy.Parameter()
    param_percent_of_population_cutoff.value = 1
    param_external_range_review_table = arcpy.Parameter()
    param_external_range_review_table.value = 'lewwoo_1'
    parameters = [param_geodatabase, param_ebird_full_year_raster, param_ebird_breeding_season_raster, param_label,
                  param_percent_of_population_cutoff, param_external_range_review_table]
    cerrfea.runCreateExternalRangeReviewFromEbirdAbundanceTool(parameters, None)
