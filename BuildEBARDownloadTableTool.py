# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen, Samantha Stefanoff
# © NatureServe Canada 2026 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: BuildEBARDownloadTableTool.py
# ArcGIS Python tool for building html table of range map download links

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import EBARUtils
import arcpy
import datetime
import StaticTranslations


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
        output_file_fr = EBARUtils.download_folder + '/EBARDownloadTables_FR.html'

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
        #html_fr = html

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
        #             html_fr += '''
        # </tbody></table>'''
                # table header
                category_taxa = row[0] + ' - ' + row[1]
                category_taxa_fr = StaticTranslations.biotics_category_translation[row[0]] + ' - ' + \
                    StaticTranslations.biotics_taxa_group_translation[row[1]]
                EBARUtils.displayMessage(messages, category_taxa + ' table')
                # combined bilingual
                html += '''
        <h4>''' + category_taxa + '''<br>
            ''' + category_taxa_fr + '''</h4>
        <table><tbody>
            <tr>
    	        <th>Scientific Name<br>
                    Nom scientifique</th>
                <th>English Name<br>
                    Nom anglais</th>
                <th>French Name<br>
                    Nom français</th>
                <th>Scope<br>
                    Portée</th>
                <th>Status<br>
                    État</th>
                <th>PDF Link<br>
                    Lien PDF</th>
                <th>GIS Data Link<br>
                    Lien de données SIG</th>
            </tr>'''
        #         html_fr += '''
        # <h4>''' + category_taxa_fr + '''</h4>
        # <table><tbody>
        #     <tr>
    	#         <th>Nom scientifique</th>
        #         <th>Nom anglais</th>
        #         <th>Nom français</th>
        #         <th>Portée</th>
        #         <th>État</th>
        #         <th>Liens PDF</th>
        #         <th>Liens de données SIG</th>
        #     </tr>'''
            # table row
            french_name = ''
            if row[4]:
                french_name = row[4]
            scope = 'Global'
            if row[6] == 'N':
                scope = 'Canadian'
            if row[6] == 'A':
                scope = 'North American'
            scope_fr = StaticTranslations.range_map_scope_translation[row[6]]
            element_global_id = str(row[5])
            if scope == 'Canadian':
                element_global_id += 'N'
            status = 'Not Reviewed'
            status_fr = 'Pas examiné'
            if row[7] == 1:
                status = 'Expert Reviewed'
                status_fr = 'Examiné par des experts'
            if row[7] == 2:
                status = 'Insufficient Data'
                status_fr = 'Données insuffisantes'
            if row[7] == 3:
                status = 'Partially Reviewed'
                status_fr = 'Examen partiel'
            if row[7] == 4:
                status = 'Low Star Rating'
                status_fr = "Faible nombre d'étoiles"
            # combined bilingual
            html += '''
            <tr>
                <td>''' + row[2] + '''</td>
                <td>''' + row[3] + '''</td>
                <td>''' + french_name + '''</td>
                <td>''' + scope + '''<br>
                    ''' + scope_fr + '''</td>
                <td>''' + status + '''<br>
                    ''' + status_fr + '''</td>
                <td><a href="https://gis.natureserve.ca/download/EBAR''' + element_global_id + \
                    '''.pdf" target="_blank">PDF EN</a><br><a href="https://gis.natureserve.ca/download/EBAR''' + \
                    element_global_id + '''_FR.pdf" target="_blank">PDF FR</a></td>'''
            # html_fr += '''
            # <tr>
            #     <td>''' + row[2] + '''</td>
            #     <td>''' + row[3] + '''</td>
            #     <td>''' + french_name + '''</td>
            #     <td>''' + scope_fr + '''</td>
            #     <td>''' + status_fr + '''</td>
            #     <td><a href="https://gis.natureserve.ca/download/EBAR''' + element_global_id + \
            #         '''.pdf" target="_blank">PDF EN</a><br><a href="https://gis.natureserve.ca/download/EBAR''' + \
            #         element_global_id + '''_FR.pdf" target="_blank">PDF FR</a></td>'''
            if row[7] == 1:
                # combined bilingual
                html += '''
                <td><a href="https://gis.natureserve.ca/download/EBAR''' + element_global_id + \
                    '''.zip" target="_blank">GIS EN</a><br><a href="https://gis.natureserve.ca/download/EBAR''' + \
                    element_global_id + '''_FR.zip" target="_blank">SIG FR</a></td>'''
                # html_fr += '''
                # <td><a href="https://gis.natureserve.ca/download/EBAR''' + element_global_id + \
                #     '''.zip" target="_blank">SIG EN</a><br><a href="https://gis.natureserve.ca/download/EBAR''' + \
                #     element_global_id + '''_FR.zip" target="_blank">SIG FR</a></td>'''
            else:
                html += '''
                <td></td>'''
                # html_fr += '''
                # <td></td>'''
            html += '''
            </tr>'''
            # html_fr += '''
            # </tr>'''
            EBARUtils.displayMessage(messages, element_global_id)
        # table footer for final table
        html += '''
		</tbody></table>
	</body>'''
    #     html_fr += '''
	# 	</tbody></table>
	# </body>'''
                
        # save
        EBARUtils.displayMessage(messages, 'Saving file')
        file = open(output_file, 'w')
        file.write(html)
        file.close()
        # file_fr = open(output_file_fr, 'w')
        # file_fr.write(html_fr)
        # file_fr.close()


# controlling process
if __name__ == '__main__':
    bedt = BuildEBARDownloadTableTool()
    bedt.runBuildEBARDownloadTableTool(None, None)
