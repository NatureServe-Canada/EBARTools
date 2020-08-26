# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2020 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: BuildDownloadTableTool.py
# ArcGIS Python tool for building html table of range map download links

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
#import sys
#import locale
import EBARUtils
import arcpy


class BuildDownloadTableTool:
    """Create JPG, PDF and Spatial Data (Zip) for a Range Map"""
    def __init__(self):
        pass

    def RunBuildDownloadTableTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        temp_folder = 'C:/GIS/EBAR/pub'
        ebar_feature_service = 'https://gis.natureserve.ca/arcgis/rest/services/EBAR-KBA/EBAR/FeatureServer'

        # now includes all RangeMap records where Publish=1
        ## make variables for parms
        #EBARUtils.displayMessage(messages, 'Processing parameters')
        #category_taxa = parameters[0]
        #range_map_ids = parameters[1]

#        # html and table header
#        EBARUtils.displayMessage(messages, 'Building header')
#        html = '''
#<html>
#    <style>
#    	body {font-family:"Trebuchet MS","Lucida Grande","Lucida Sans Unicode","Lucida Sans",Tahoma,sans-serif;
#    	}
#    	table, th, td {
#			text-align: left;
#			vertical-align: top;
#			padding-top: 5px;
#			padding-bottom: 5px;
#            padding-right: 15px;
#    	}
#    </style>
#    <body>'''

        # loop all range maps
        html = ''
        arcpy.MakeTableView_management(ebar_feature_service + '/11', 'range_map_view', 'IncludeInDownloadTable = 1')
        arcpy.AddJoin_management('range_map_view', 'SpeciesID', ebar_feature_service + '/4', 'SpeciesID',
                                 'KEEP_COMMON')
        order_by = 'ORDER BY L4BIOTICS_ELEMENT_NATIONAL.CATEGORY, ' + \
            'L4BIOTICS_ELEMENT_NATIONAL.TAX_GROUP, L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_SCIENTIFIC_NAME'
        with arcpy.da.SearchCursor('range_map_view',
                                   ['L4BIOTICS_ELEMENT_NATIONAL.CATEGORY',
                                    'L4BIOTICS_ELEMENT_NATIONAL.TAX_GROUP',
                                    'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_SCIENTIFIC_NAME',
                                    'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_ENGL_NAME',
                                    'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_FR_NAME',
                                    'L4BIOTICS_ELEMENT_NATIONAL.ELEMENT_GLOBAL_ID',
                                    'L11RangeMap.RangeMapScope'],
                                   sql_clause=(None, order_by)) as cursor:
            # one table for each category - taxa_group
            category_taxa = ''
            for row in EBARUtils.searchCursor(cursor):
                if row['L4BIOTICS_ELEMENT_NATIONAL.CATEGORY'] + ' - ' + \
                    row['L4BIOTICS_ELEMENT_NATIONAL.TAX_GROUP'] != category_taxa:
                    if category_taxa != '':
                        # table footer for previous table
                        html += '''
                        </tbody></table>'''
                    # table header
                    category_taxa = row['L4BIOTICS_ELEMENT_NATIONAL.CATEGORY'] + ' - ' + \
                        row['L4BIOTICS_ELEMENT_NATIONAL.TAX_GROUP']
                    EBARUtils.displayMessage(messages, category_taxa + ' table')
                    html += '''
                        <h2>''' + category_taxa + '''</h2>
                        <table><tbody>
                            <tr>
    	                        <th>Scientific Name</th>
                                <th>English Name</th>
                                <th>Nom Français</th>
                                <th>Scope</th>
                                <th>PDF Link</th>
                                <th>GIS Data Link</th>
                            </tr>'''
                # table row
                scope = 'Global'
                if row['L11RangeMap.RangeMapScope'] == 'N':
                    scope = 'National'
                if row['L11RangeMap.RangeMapScope'] == 'A':
                    scope = 'North American'
                element_global_id = str(row['L4BIOTICS_ELEMENT_NATIONAL.ELEMENT_GLOBAL_ID'])
                if scope == 'National':
                    element_global_id += 'N'
                french_name = ''
                if row['L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_FR_NAME']:
                    french_name = row['L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_FR_NAME']
                html += '''
                            <tr>
                                <td>''' + row['L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_SCIENTIFIC_NAME'] + '''</td>
                                <td>''' + row['L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_ENGL_NAME'] + '''</td>
                                <td>''' + french_name + '''</td>
                                <td>''' + scope + '''</td>
                                <td><a href="https://gis.natureserve.ca/download/EBAR''' + element_global_id + \
                                    '''.pdf" target="_blank">View PDF</a></td>
                                <td><a href="https://gis.natureserve.ca/download/EBAR''' + element_global_id + \
                                    '''.zip" target="_blank">Download GIS Data</a></td>
                            </tr>'''
                EBARUtils.displayMessage(messages, element_global_id + ' EBAR')
            # table footer for final table
            html += '''
                        </tbody></table>'''
                
        # save
        EBARUtils.displayMessage(messages, 'Saving file')
        file = open(temp_folder + '/DownloadTables.html', 'w')
        file.write(html)
        file.close()


# controlling process
if __name__ == '__main__':
    bdt = BuildDownloadTableTool()
    # hard code parameters for debugging
    # 638, 637, 641, 639, 640 Invertebrate Animal - Bumble Bees
    # 625, 626, 628, 627 Invertebrate Animal - Other Moths
    # 631, 616, 633, 447, 50, 629, 51, 622, 634, 635, 636, 608, 52, 618, 234, 449, 680, 619, 621, 620, 448 Vascular Plant - Dicots
    # 53 Vascular Plant - Monocots
    #range_map_ids = [625, 626, 628, 627]
    #bdt.RunBuildDownloadTableTool(['Invertebrate Animal - Other Moths', range_map_ids], None)
    bdt.RunBuildDownloadTableTool(None, None)
