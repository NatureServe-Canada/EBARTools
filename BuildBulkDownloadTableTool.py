# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2020 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: BuildBulkDownloadTableTool.py
# ArcGIS Python tool for building html table of category/taxa download links

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import EBARUtils
import arcpy
import datetime


class BuildBulkDownloadTableTool:
    """Create html table per taxa / category group downloads"""
    def __init__(self):
        pass

    def runBuildBulkDownloadTableTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        output_file = EBARUtils.download_folder + '/CategoryTaxaDownloadTables.html'

        # html header
        html = '''<!doctype html>
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
            color: #222222;
    	}
    	table {
			border: solid 1px #dddddd;
            text-align: left;
			vertical-align: top;
            border-collapse: collapse;
            width: 560px;
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
	<body>
        <h2>Bulk Download by Category - Taxa Group</h2>
        <table><tbody>
            <tr>
    	        <th>Category</th>
                <th>Taxa Group</th>
                <th>PDFs Link</th>
                <th>GIS Data Link</th>
            </tr>'''
        # loop all RangeMap records where IncludeInDownloadTable=1
        arcpy.MakeTableView_management(EBARUtils.ebar_feature_service + '/11', 'range_map_view',
                                       'IncludeInDownloadTable = 1')
        # join BIOTICS_ELEMENT_NATIONAL to RangeMap
        arcpy.AddJoin_management('range_map_view', 'SpeciesID', EBARUtils.ebar_feature_service + '/4', 'SpeciesID',
                                 'KEEP_COMMON')
        category_taxa = ''
        # use Python sorted (sql_clause ORDER BY doesn't work), which precludes use of EBARUtils.SearchCursor
        for row in sorted(arcpy.da.SearchCursor('range_map_view',
                          ['L4BIOTICS_ELEMENT_NATIONAL.CATEGORY',
                           'L4BIOTICS_ELEMENT_NATIONAL.TAX_GROUP'])):
            if row[0] + ' - ' + row[1] != category_taxa:
                # table row
                category_taxa = row[0] + ' - ' + row[1]
                EBARUtils.displayMessage(messages, category_taxa + ' links')
                html += '''
            <tr>
                <td>''' + row[0] + '''</td>
                <td>''' + row[1] + '''</td>
                <td><a href="https://gis.natureserve.ca/download/EBAR - ''' + category_taxa + \
                    ''' - All PDFs.zip" target="_blank">Download PDFs</a></td>
                <td><a href="https://gis.natureserve.ca/download/EBAR - ''' + category_taxa + \
                    ''' - All Data.zip" target="_blank">Download Data</a></td>
            </tr>'''

        # footer
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
    bbdt = BuildBulkDownloadTableTool()
    bbdt.runBuildBulkDownloadTableTool(None, None)
