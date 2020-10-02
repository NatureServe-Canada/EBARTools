# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2020 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: PublishRangeMapTool.py
# ArcGIS Python tool for creating Zip sets of PDFs and Spatial Data per Category/Taxa

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
#import sys
#import locale
import EBARUtils
import shutil
import arcpy
import arcpy.mp
import arcpy.metadata


class PublishRangeMapSetsTool:
    """Create Zip sets of PDFs and Spatial Data per Category/Taxa"""
    def __init__(self):
        pass

    def ProcessCategoryTaxaGroup(self, messages, category_taxagroup, range_map_ids, attributes_dict, zip_folder,
                                 metadata):
        # export range map, with biotics/species additions
        EBARUtils.displayMessage(messages, 'Exporting RangeMap records to CSV')
        EBARUtils.ExportRangeMapToCSV('range_map_view' + category_taxagroup, range_map_ids, attributes_dict, zip_folder,
                                      'RangeMap.csv', metadata)

        # export range map ecoshapes
        EBARUtils.displayMessage(messages, 'Exporting RangeMapEcoshape records to CSV')
        EBARUtils.ExportRangeMapEcoshapesToCSV('range_map_ecoshape_view' + category_taxagroup, range_map_ids,
                                               zip_folder, 'RangeMapEcoshape.csv', metadata)

        # export ecoshapes
        EBARUtils.displayMessage(messages, 'Exporting Ecoshape polygons to shapefile')
        EBARUtils.ExportEcoshapesToShapefile('ecoshape_layer' + category_taxagroup,
                                             'range_map_ecoshape_view' + category_taxagroup, zip_folder, 
                                             'Ecoshape.shp', metadata)

        # export overview ecoshapes
        EBARUtils.displayMessage(messages, 'Exporting EcoshapeOverview polygons to shapefile')
        EBARUtils.ExportEcoshapeOverviewsToShapefile('ecoshape_overview_layer' + category_taxagroup,
                                                     'range_map_ecoshape_view' + category_taxagroup, zip_folder, 
                                                     'EcoshapeOverview.shp', metadata)

        # create zips
        EBARUtils.displayMessage(messages, 'Creating ZIP: https://gis.natureserve.ca/download/EBAR - ' + \
            category_taxagroup + ' - All PDFs.zip')
        EBARUtils.createZip(zip_folder,
                            EBARUtils.download_folder + '/EBAR - ' + category_taxagroup + ' - All PDFs.zip',
                            '.pdf')
        EBARUtils.displayMessage(messages, 'Creating ZIP: https://gis.natureserve.ca/download/EBAR - ' + \
            category_taxagroup + ' - All Data.zip')
        EBARUtils.createZip(zip_folder,
                            EBARUtils.download_folder + '/EBAR - ' + category_taxagroup + ' - All Data.zip',
                            None)

    def RunPublishRangeMapSetsTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        param_category = parameters[0].valueAsText
        EBARUtils.displayMessage(messages, 'Category: ' + param_category)
        param_taxagroup = parameters[1].valueAsText
        EBARUtils.displayMessage(messages, 'Taxa Group: ' + param_taxagroup)

        # generate metadata
        EBARUtils.displayMessage(messages, 'Generating metadata')
        md = arcpy.metadata.Metadata()
        md.tags = 'Species Range, NatureServe Canada, Ecosystem-based Automated Range'
        md.description = 'See EBARxxxxx.pdf for per-species map and additional metadata, and ' + \
            'EBARMethods.pdf for additional details. <a href="https://explorer.natureserve.org/">Go to ' + \
            'NatureServe Explorer</a> for information about the species.'
        md.credits = '© NatureServe Canada ' + str(datetime.datetime.now().year)
        md.accessConstraints = 'Publicly shareable under CC BY 4.0 (<a href=' + \
            '"https://creativecommons.org/licenses/by/4.0/">https://creativecommons.org/licenses/by/4.0/</a>)'

        # loop all RangeMap records where IncludeInDownloadTable=1
        arcpy.MakeTableView_management(EBARUtils.ebar_feature_service + '/11', 'range_map_view',
                                       'IncludeInDownloadTable = 1')
        # join BIOTICS_ELEMENT_NATIONAL to RangeMap
        arcpy.AddJoin_management('range_map_view', 'SpeciesID', EBARUtils.ebar_feature_service + '/4', 'SpeciesID',
                                 'KEEP_COMMON')
        category_taxagroup = ''
        processed = 0
        # use Python sorted (sql_clause ORDER BY doesn't work), which precludes use of EBARUtils.SearchCursor
        where_clause = None
        if param_category:
            where_clause = "L4BIOTICS_ELEMENT_NATIONAL.CATEGORY = '" + param_category + "'"
        if param_taxagroup:
            if where_clause:
                where_clause += "AND L4BIOTICS_ELEMENT_NATIONAL.TAX_GROUP = '" + param_taxagroup + "'"
            else:
                where_clause = "L4BIOTICS_ELEMENT_NATIONAL.TAX_GROUP = '" + param_taxagroup + "'"
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
                           'L11RangeMap.RangeMapID'], where_clause)):
            if row[0] + ' - ' + row[1] != category_taxagroup:
                # new category_taxagroup
                if category_taxagroup != '':
                    # previous category_taxagroup
                    self.ProcessCategoryTaxaGroup(messages, category_taxagroup, range_map_ids, attributes_dict,
                                                  zip_folder, md)
                processed += 1
                range_map_ids = []
                attributes_dict = {}

                # make zip folder
                category_taxagroup = row[0] + ' - ' + row[1]
                EBARUtils.displayMessage(messages, 'Category - Taxa Group: ' + category_taxagroup)
                zip_folder = EBARUtils.temp_folder + '/EBAR - ' + category_taxagroup
                EBARUtils.createReplaceFolder(zip_folder)

                # copy static resources
                shutil.copyfile(EBARUtils.resources_folder + '/ReadmeSet.txt', zip_folder + '/Readme.txt')
                shutil.copyfile(EBARUtils.resources_folder + '/EBARMethods.pdf', zip_folder + '/EBARMethods.pdf')
                shutil.copyfile(EBARUtils.resources_folder + '/Jurisdiction.csv', zip_folder + '/Jurisdiction.csv')

            # copy pdf
            EBARUtils.displayMessage(messages, 'Range Map ID: ' + str(row[8]))
            element_global_id = str(row[5])
            if row[7] == 'N':
                element_global_id += 'N'
            shutil.copyfile(EBARUtils.download_folder + '/EBAR' + element_global_id + '.pdf',
                            zip_folder + '/EBAR' + element_global_id + '.pdf')

            # set range map attributes
            range_map_ids.append(str(row[8]))
            global_unique_id = row[6].replace('-', '.')
            attributes_dict[str(row[8])] = EBARUtils.getTaxonAttributes(global_unique_id, element_global_id, row[8],
                                                                        messages)

        if row:
            # final category_taxagroup
            self.ProcessCategoryTaxaGroup(messages, category_taxagroup, range_map_ids, attributes_dict, zip_folder, md)

        EBARUtils.displayMessage(messages, 'Processed ' + str(processed) + ' categories/taxa')
        return


# controlling process
if __name__ == '__main__':
    prms = PublishRangeMapSetsTool()
    param_category = arcpy.Parameter()
    param_category.value = 'Invertebrate Animal'
    param_taxagroup = arcpy.Parameter()
    param_taxagroup.value = 'Bumble Bees'
    #param_taxagroup.value = None
    parameters = [param_category, param_taxagroup]
    prms.RunPublishRangeMapSetsTool(parameters, None)
