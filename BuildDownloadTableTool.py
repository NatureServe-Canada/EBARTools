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
import EBARUtils
import arcpy
import datetime


class BuildDownloadTableTool:
    """Create JPG, PDF and Spatial Data (Zip) for a Range Map"""
    def __init__(self):
        pass

    def RunBuildDownloadTableTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #output_file = 'F:/download/EBARDownloadTables.html'
        output_file = 'C:/GIS/EBAR/pub/EBARDownloadTables.html'
        ebar_feature_service = 'https://gis.natureserve.ca/arcgis/rest/services/EBAR-KBA/EBAR/FeatureServer'

        # html header
        html = '''
<!doctype html>
    <style>
        h2 {
            font-family: "Trebuchet MS","Lucida Grande","Lucida Sans Unicode","Lucida Sans",Tahoma,sans-serif;
            font-size: 28px;
            color: #365700;
            font-weight: normal;
        }
        body {
            font-family:"Calibri",Candara,Segoe,"Segoe UI",Optima,Arial,sans-serif;
            font-size: 14px; 
            color: #222222
    	}
    	table {
			border: solid 1px #dddddd;
            text-align: left;
			vertical-align: top;
            border-collapse: collapse;
            width: 600px;
                        
    	}
        th {
            border-bottom: 3px solid #ccc;
            padding: 7px;
        }
        td {
            padding: 5px;  
        }
        tr:nth-child(even) {background-color: #f9f9f9;}
        a {
            font-weight: bold;
            color: #5c9400;
            text-decoration: none;
        }
    </style>
	<body>'''
        # loop all RangeMap records where IncludeInDownloadTable=1
        arcpy.MakeTableView_management(ebar_feature_service + '/11', 'range_map_view', 'IncludeInDownloadTable = 1')
        # join BIOTICS_ELEMENT_NATIONAL to RangeMap
        arcpy.AddJoin_management('range_map_view', 'SpeciesID', ebar_feature_service + '/4', 'SpeciesID',
                                 'KEEP_COMMON')
        category_taxa = ''
        # use Python sorted (sql_clause ORDER BY doesn't work), which precludes use of EBARUtils.SearchCursor
        for row in sorted(arcpy.da.SearchCursor('range_map_view',
                          ['L4BIOTICS_ELEMENT_NATIONAL.CATEGORY',
                           'L4BIOTICS_ELEMENT_NATIONAL.TAX_GROUP',
                           'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_SCIENTIFIC_NAME',
                           'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_ENGL_NAME',
                           'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_FR_NAME',
                           'L4BIOTICS_ELEMENT_NATIONAL.ELEMENT_GLOBAL_ID',
                           'L11RangeMap.RangeMapScope'])):
            if row[0] + ' - ' + row[1] != category_taxa:
                if category_taxa != '':
                    # table footer for previous table
                    html += '''
        </tbody></table>'''
                # table header
                category_taxa = row[0] + ' - ' + row[1]
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
            if row[6] == 'N':
                scope = 'Canadian'
            if row[6] == 'A':
                scope = 'North American'
            element_global_id = str(row[5])
            if scope == 'National':
                element_global_id += 'N'
            french_name = ''
            if row[4]:
                french_name = row[4]
            html += '''
            <tr>
                <td>''' + row[2] + '''</td>
                <td>''' + row[3] + '''</td>
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
		</tbody></table>
	</body>'''
                
        # save
        EBARUtils.displayMessage(messages, 'Saving file')
        file = open(output_file, 'w')
        file.write(html)
        file.close()


# controlling process
if __name__ == '__main__':
    bdt = BuildDownloadTableTool()
    bdt.RunBuildDownloadTableTool(None, None)
