# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2026 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: BuildBulkDownloadTableTool.py
# ArcGIS Python tool for building html table of category/taxagroup download links

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import EBARUtils
import arcpy
import datetime


class BuildBulkDownloadTableTool:
    """Create html table of per category/taxagroup downloads"""
    def __init__(self):
        pass

    def processCategoryTaxaGroup(self, category, taxagroup, category_taxagroup, only_deficient_partial):
        html = '''
            <tr>
                <td>''' + category + '''</td>
                <td>''' + taxagroup + '''</td>
                <td><a href="https://gis.natureserve.ca/download/EBAR - ''' + category_taxagroup + \
                    ''' - All PDFs.zip" target="_blank">Download PDFs</a></td>'''
        if only_deficient_partial:
            html += '''
                <td></td>'''
        else:
            html +='''
                <td><a href="https://gis.natureserve.ca/download/EBAR - ''' + category_taxagroup + \
                    ''' - All Data.zip" target="_blank">Download GIS Data</a></td>'''
        html +='''
            </tr>'''
        return html

    def runBuildBulkDownloadTableTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        output_file = EBARUtils.download_folder + '/CategoryTaxaDownloadTables.html'

        # html header
        html = '''<!doctype html>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
    </style>
    <style>
        body {
            font-family: 'Roboto', sans-serif !important;
            font-size: 14px; 
            color: #222222;
    	}
        h4 {
            font-family: 'Roboto', sans-serif !important;
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 10px;
        }
    	table {
			border: solid 1px #dddddd;
            text-align: left;
			vertical-align: top;
            border-collapse: collapse;
            width: 100% !important;
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
            color: #0449a4;
            text-decoration: none;
        }
    </style>
	<body>
        Last updated ''' + start_time.strftime('%B %d, %Y') + '''
        <h4>Bulk Download by Category - Taxa Group</h4>
        <table><tbody>
            <tr>
    	        <th>Category</th>
                <th>Taxa Group</th>
                <th>PDFs Link</th>
                <th>GIS Data Link</th>
            </tr>'''

        # loop all RangeMap records where IncludeInDownloadTable is populated
        arcpy.MakeTableView_management(EBARUtils.ebar_feature_service + '/11', 'range_map_view',
                                       'IncludeInDownloadTable IN (1, 2, 3, 4) AND Publish = 1')
        # join BIOTICS_ELEMENT_NATIONAL to RangeMap
        arcpy.AddJoin_management('range_map_view', 'SpeciesID', EBARUtils.ebar_feature_service + '/4', 'SpeciesID',
                                 'KEEP_COMMON')
        category_taxagroup = ''
        # use Python sorted (sql_clause ORDER BY doesn't work), which precludes use of EBARUtils.SearchCursor
        for row in sorted(arcpy.da.SearchCursor('range_map_view',
                          ['L4BIOTICS_ELEMENT_NATIONAL.CATEGORY',
                           'L4BIOTICS_ELEMENT_NATIONAL.TAX_GROUP',
                           'L11RangeMap.IncludeInDownloadTable'])):
            if row[0] + ' - ' + row[1] != category_taxagroup:
                # new category_taxagroup
                if category_taxagroup != '':
                    # table row for previous group
                    html += self.processCategoryTaxaGroup(category, taxagroup, category_taxagroup, only_deficient_partial)
                # if all range maps in group have no spatial data then exclude spatial download
                only_deficient_partial = True
                category = row[0]
                taxagroup = row[1]
                category_taxagroup = category + ' - ' + taxagroup
                EBARUtils.displayMessage(messages, category_taxagroup + ' links')
            if row[2] == 1:
                only_deficient_partial = False

        # table row for final group
        html += self.processCategoryTaxaGroup(category, taxagroup, category_taxagroup, only_deficient_partial)
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
