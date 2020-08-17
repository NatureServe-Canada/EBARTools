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

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        category_taxa = parameters[0]
        range_map_ids = parameters[1]

        # html and table header
        EBARUtils.displayMessage(messages, 'Building header')
        html = '''
<html>
    <style>
    	body {font-family:"Trebuchet MS","Lucida Grande","Lucida Sans Unicode","Lucida Sans",Tahoma,sans-serif;
    	}
    	table, th, td {
			text-align: left;
			vertical-align: top;
			padding-top: 5px;
			padding-bottom: 5px;
            padding-right: 15px;
    	}
    </style>
    <body>
        <p><span style="color: rgb(54, 87, 0); font-size: 1.75rem;">''' + category_taxa + '''</span></p>
        <table>
            <tr>
    	        <th>Scientific Name</th><th>English Name</th><th>Nom Français</th><th>Scope</th><th>PDF Link</th><th>GIS Data Link</th>
            </tr>'''
                
        # loop range maps
        EBARUtils.displayMessage(messages, 'Building table')
        for range_map_id in range_map_ids:
            species_id = None
            with arcpy.da.SearchCursor(ebar_feature_service + '/11',
                                       ['SpeciesID', 'RangeMapScope'], 'RangeMapID = ' + str(range_map_id)) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    species_id = row['SpeciesID']
                    scope = 'Global'
                    if row['RangeMapScope'] == 'N':
                        scope = 'National'
                    if row['RangeMapScope'] == 'A':
                        scope = 'North American'
                if species_id:
                    del row
                else:
                    EBARUtils.displayMessage(messages, 'ERROR: Range Map Not Found')
                    # terminate with error
                    return
            with arcpy.da.SearchCursor(ebar_feature_service + '/4', 
                                       ['NATIONAL_SCIENTIFIC_NAME', 'NATIONAL_ENGL_NAME', 'NATIONAL_FR_NAME',
                                        'ELEMENT_GLOBAL_ID'],
                                       'SpeciesID = ' + str(species_id)) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    element_global_id = str(row['ELEMENT_GLOBAL_ID'])
                    if scope == 'National':
                        element_global_id += 'N'
                    french_name = ''
                    if row['NATIONAL_FR_NAME']:
                        french_name = row['NATIONAL_FR_NAME']
                    html += '''
            <tr>
                <td>''' + row['NATIONAL_SCIENTIFIC_NAME'] + '''</td>
                <td>''' + row['NATIONAL_ENGL_NAME'] + '''</td>
                <td>''' + french_name + '''</td>
                <td>''' + scope + '''</td>
                <td><a href="https://gis.natureserve.ca/download/EBAR''' + element_global_id + '''.pdf" target="_blank">View PDF</a></td>
                <td><a href="https://gis.natureserve.ca/download/EBAR''' + element_global_id + '''.zip" target="_blank">Download GIS Data</a></td>
            </tr>'''

        # html and table footer
        EBARUtils.displayMessage(messages, 'Building footer')
        html += '''
        </table><br>
    </body>
</html>'''

        # save
        EBARUtils.displayMessage(messages, 'Saving file')
        file = open(temp_folder + '/' + category_taxa + '.html', 'w')
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
    range_map_ids = [625, 626, 628, 627]
    bdt.RunBuildDownloadTableTool(['Invertebrate Animal - Other Moths', range_map_ids], None)
