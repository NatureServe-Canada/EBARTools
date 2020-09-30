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

    def RunPublishRangeMapSetsTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        param_category = parameters[0].valueAsText
        param_taxagroup = parameters[1].valueAsText

        # loop all RangeMap records where IncludeInDownloadTable=1
        arcpy.MakeTableView_management(EBARUtils.ebar_feature_service + '/11', 'range_map_view', 'IncludeInDownloadTable = 1')
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
                           'L11RangeMap.RangeMapScope'], where_clause)):
            if row[0] + ' - ' + row[1] != category_taxagroup:
                # new category_taxagroup
                processed += 1
                if category_taxagroup != '':
                    # zip PDFs for previous category_taxagroup
                    EBARUtils.displayMessage(messages, 'Creating PDFs ZIP')
                    EBARUtils.createZip(zip_folder,
                                        EBARUtils.download_folder + '/EBAR - ' + category_taxagroup + \
                                            ' - All PDFs.zip')
                # make zip folder
                category_taxagroup = row[0] + ' - ' + row[1]
                EBARUtils.displayMessage(messages, 'Processing ' + category_taxagroup)
                zip_folder = EBARUtils.temp_folder + '/EBAR - ' + category_taxagroup
                EBARUtils.createReplaceFolder(zip_folder)
            # copy pdf
            scope = 'Global'
            if row[6] == 'N':
                scope = 'Canadian'
            if row[6] == 'A':
                scope = 'North American'
            element_global_id = str(row[5])
            if scope == 'Canadian':
                element_global_id += 'N'
            shutil.copyfile(EBARUtils.download_folder + '/EBAR' + element_global_id + '.pdf',
                            zip_folder + '/EBAR' + element_global_id + '.pdf')

        if row:
            # zip PDFs for final category_taxagroupgroup
            EBARUtils.displayMessage(messages, 'Creating PDFs ZIP')
            EBARUtils.createZip(zip_folder,
                                EBARUtils.download_folder + '/EBAR - ' + category_taxagroup + ' - All PDFs.zip')

        EBARUtils.displayMessage(messages, 'Processed ' + str(processed) + ' categories/taxa')
        return


# controlling process
if __name__ == '__main__':
    prms = PublishRangeMapSetsTool()
    param_category = arcpy.Parameter()
    param_category.value = 'Invertebrate Animal'
    param_taxagroup = arcpy.Parameter()
    #param_taxagroup.value = 'Bumble Bees'
    param_taxagroup.value = None
    parameters = [param_category, param_taxagroup]
    prms.RunPublishRangeMapSetsTool(parameters, None)
