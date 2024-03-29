# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2020 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: BuildEBARDownloadTableTool.py
# ArcGIS Python tool for building html table of range map download links

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import EBARUtils
import arcpy
import datetime


class BuildEBARDownloadTableTool:
    """Build html table of all Range Maps available for download"""
    def __init__(self):
        pass

    def runBuildEBARDownloadTableTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        output_file = EBARUtils.download_folder + '/EBARDownloadTables.html'

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
	<body>'''
        # loop all RangeMap records where IncludeInDownloadTable is populated
        arcpy.MakeTableView_management(EBARUtils.ebar_feature_service + '/11', 'range_map_view',
                                       'IncludeInDownloadTable IN (1, 2, 3, 4) AND Publish = 1')
        # join BIOTICS_ELEMENT_NATIONAL to RangeMap
        arcpy.AddJoin_management('range_map_view', 'SpeciesID', EBARUtils.ebar_feature_service + '/4', 'SpeciesID',
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
                           'L11RangeMap.RangeMapScope',
                           'L11RangeMap.IncludeInDownloadTable'])):
            if row[0] + ' - ' + row[1] != category_taxa:
                if category_taxa != '':
                    # table footer for previous table
                    html += '''
        </tbody></table>'''
                # table header
                category_taxa = row[0] + ' - ' + row[1]
                EBARUtils.displayMessage(messages, category_taxa + ' table')
                html += '''
        <h4>''' + category_taxa + '''</h4>
        <table><tbody>
            <tr>
    	        <th>Scientific Name</th>
                <th>English Name</th>
                <th>Nom Francais</th>
                <th>Scope</th>
                <th>Status</th>
                <th>PDF Link</th>
                <th>GIS Data Link</th>
            </tr>'''
            # table row
            french_name = ''
            if row[4]:
                french_name = row[4]
            scope = 'Global'
            if row[6] == 'N':
                scope = 'Canadian'
            if row[6] == 'A':
                scope = 'North American'
            element_global_id = str(row[5])
            if scope == 'Canadian':
                element_global_id += 'N'
            status = 'Expert Reviewed'
            if row[7] == 2:
                status = 'Insufficient Data'
            if row[7] == 3:
                status = 'Partially Reviewed'
            if row[7] == 4:
                status = 'Low Star Rating'
            html += '''
            <tr>
                <td>''' + row[2] + '''</td>
                <td>''' + row[3] + '''</td>
                <td>''' + french_name + '''</td>
                <td>''' + scope + '''</td>
                <td>''' + status + '''</td>
                <td><a href="https://gis.natureserve.ca/download/EBAR''' + element_global_id + \
                    '''.pdf" target="_blank">View PDF</a></td>'''
            if row[7] == 1:
                html += '''
                <td><a href="https://gis.natureserve.ca/download/EBAR''' + element_global_id + \
                    '''.zip" target="_blank">Download GIS Data</a></td>'''
            else:
                html += '''
                <td></td>'''
            html += '''
            </tr>'''
            EBARUtils.displayMessage(messages, element_global_id)
        # table footer for final table
        html += '''
		</tbody></table>
	</body>'''
                
        # save
        EBARUtils.displayMessage(messages, 'Saving file')
        file = open(output_file, 'w')
        file.write(html)
        file.close()


# # controlling process
# if __name__ == '__main__':
#     bedt = BuildEBARDownloadTableTool()
#     bedt.runBuildEBARDownloadTableTool(None, None)
