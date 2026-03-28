# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen, Samantha Stefanoff
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
import StaticTranslations
import locale
import unidecode


class BuildBulkDownloadTableTool:
    """Create html table of per category/taxagroup downloads"""
    def __init__(self):
        pass

    def processCategoryTaxaGroup(self, category, taxagroup, category_taxagroup, only_deficient_partial):
        category_taxagroup_fr_unidecode = unidecode.unidecode(StaticTranslations.biotics_category_translation[category]) + \
            ' - ' + unidecode.unidecode(StaticTranslations.biotics_taxa_group_translation[taxagroup])
        # combined bilingual
        html = '''
            <tr>
                <td>''' + category + '''<br>
                    ''' + StaticTranslations.biotics_category_translation[category] + '''</td>
                <td>''' + taxagroup + '''<br>
                    ''' + StaticTranslations.biotics_taxa_group_translation[taxagroup] + '''</td>
                <td><a href="https://gis.natureserve.ca/download/EBAR - ''' + category_taxagroup + \
                    ''' - All PDFs.zip" target="_blank">PDFs EN</a><br><a href="https://gis.natureserve.ca/download/EBAR - ''' + \
                    category_taxagroup_fr_unidecode + ''' - Tous les PDFs.zip" target="_blank">PDFs FR</a></td>'''
        # html_fr = '''
        #     <tr>
        #         <td>''' + StaticTranslations.biotics_category_translation[category] + '''</td>
        #         <td>''' + StaticTranslations.biotics_taxa_group_translation[taxagroup] + '''</td>
        #         <td><a href="https://gis.natureserve.ca/download/EBAR - ''' + category_taxagroup + \
        #             ''' - All PDFs.zip" target="_blank">PDFs EN</a><br><a href="https://gis.natureserve.ca/download/EBAR - ''' + \
        #             category_taxagroup_fr_unidecode + ''' - Tous les PDFs.zip" target="_blank">PDFs FR</a></td>'''
        if only_deficient_partial:
            html += '''
                <td></td>'''
            # html_fr += '''
            #     <td></td>'''
        else:
            html +='''
                <td><a href="https://gis.natureserve.ca/download/EBAR - ''' + category_taxagroup + \
                    ''' - All Data.zip" target="_blank">GIS EN</a><br><a href="https://gis.natureserve.ca/download/EBAR - ''' + \
                    category_taxagroup_fr_unidecode + ''' - Toutes les donnees.zip" target="_blank">SIG FR</a></td>'''
            # html_fr +='''
            #     <td><a href="https://gis.natureserve.ca/download/EBAR - ''' + category_taxagroup + \
            #         ''' - All Data.zip" target="_blank">SIG EN</a><br><a href="https://gis.natureserve.ca/download/EBAR - ''' + \
            #         category_taxagroup_fr_unidecode + ''' - Toutes les donnees.zip" target="_blank">SIG FR</a></td>'''
        html +='''
            </tr>'''
        # html_fr +='''
        #     </tr>'''
        return html #, html_fr

    def runBuildBulkDownloadTableTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        output_file = EBARUtils.download_folder + '/CategoryTaxaDownloadTables.html'
        #output_file_fr = EBARUtils.download_folder + '/CategoryTaxaDownloadTables_FR.html'

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
        # combined bilingual
        html += '''Last updated ''' + start_time.strftime('%B %d, %Y')
        original_lc_time = locale.getlocale(locale.LC_TIME)
        locale.setlocale(locale.LC_TIME, 'fr-ca')
        html += '''<br>Dernière mise à jour : ''' + start_time.strftime('%B %d, %Y')
        locale.setlocale(locale.LC_TIME, original_lc_time)
        html += '''<h4>Bulk Download by Category - Taxa Group<br>
                       Téléchargement en masse par categorie - groupe taxonomique</h4>
        <table><tbody>
            <tr>
    	        <th>Category<br>
                    Categorie</th>
                <th>Taxa Group<br>
                    Groupe taxonomique</th>
                <th>PDFs Link<br>
                    Lien PDFs</th>
                <th>GIS Data Link<br>
                    Lien de données SIG</th>
            </tr>'''
        # original_lc_time = locale.getlocale(locale.LC_TIME)
        # locale.setlocale(locale.LC_TIME, 'fr-ca')
        # html_fr += '''Dernière mise à jour : ''' + start_time.strftime('%B %d, %Y') + '''
        # <h4>Téléchargement en masse par categorie - groupe taxonomique</h4>
        # <table><tbody>
        #     <tr>
    	#         <th>Categorie</th>
        #         <th>Groupe taxonomique</th>
        #         <th>Liens PDFs</th>
        #         <th>Liens de données SIG</th>
        #     </tr>'''
        # locale.setlocale(locale.LC_TIME, original_lc_time)

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
                    # combined bilingual
                    html += self.processCategoryTaxaGroup(category, taxagroup, category_taxagroup, only_deficient_partial)
                    # category_taxagroup_html_en, category_taxagroup_html_fr = self.processCategoryTaxaGroup(category, taxagroup,
                    #                                                                                        category_taxagroup,
                    #                                                                                        only_deficient_partial)
                    # html += category_taxagroup_html_en
                    # html_fr += category_taxagroup_html_fr
                # if all range maps in group have no spatial data then exclude spatial download
                only_deficient_partial = True
                category = row[0]
                taxagroup = row[1]
                category_taxagroup = category + ' - ' + taxagroup
                EBARUtils.displayMessage(messages, category_taxagroup + ' links')
            if row[2] == 1:
                only_deficient_partial = False

        # table row for final group
        # combined bilingual
        html += self.processCategoryTaxaGroup(category, taxagroup, category_taxagroup, only_deficient_partial)
        # category_taxagroup_html_en, category_taxagroup_html_fr = self.processCategoryTaxaGroup(category, taxagroup,
        #                                                                                        category_taxagroup,
        #                                                                                        only_deficient_partial)
        #html += category_taxagroup_html_en
        #html_fr += category_taxagroup_html_fr
        # footer
        html += '''
		</tbody></table>
	</body>'''
    #     html_fr += '''
	# 	</tbody></table>
	# </body>'''
                
        # save
        EBARUtils.displayMessage(messages, 'Saving file')
        file_en = open(output_file, 'w')
        file_en.write(html)
        file_en.close()
        # file_en = open(output_file_fr, 'w')
        # file_en.write(html_fr)
        # file_en.close()


# controlling process
if __name__ == '__main__':
    bbdt = BuildBulkDownloadTableTool()
    bbdt.runBuildBulkDownloadTableTool(None, None)
