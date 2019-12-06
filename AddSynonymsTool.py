# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: AddSynonymsTool.py
# ArcGIS Python tool for adding BIOTICS Synonyms not already in the Species or Synonym tables

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import arcpy
import io
import csv
import EBARUtils


class AddSynonymsTool:
    """Add BIOTICS Synonyms not already in the Species or Synonym tables"""
    def __init__(self):
        pass

    def RunAddSynonymsTool(self, parameters, messages):
        # make variables for parms
        param_geodatabase = parameters[0].valueAsText
        param_csv = parameters[1].valueAsText

        # try to open data file as a csv
        infile = io.open(param_csv, 'r', encoding='mbcs') # mbcs encoding is Windows ANSI
        reader = csv.DictReader(infile)

        # read existing Names into lists
        EBARUtils.displayMessage(messages, 'Reading existing Scientific Names')
        species_dict = EBARUtils.readSpecies(param_geodatabase)
        synonym_dict = EBARUtils.readSynonyms(param_geodatabase)
        element_species_dict = EBARUtils.readElementSpecies(param_geodatabase)

        # process all file lines
        EBARUtils.displayMessage(messages, 'Processing file lines')
        count = 0
        added = 0
        for file_line in reader:
            scientific_name = file_line['SCIENTIFIC_NAME']
            if scientific_name in species_dict:
                EBARUtils.displayMessage(messages, 'WARNING: ' + scientific_name + ' already has Species record')
            elif scientific_name in synonym_dict:
                EBARUtils.displayMessage(messages, 'WARNING: ' + scientific_name + ' already has Synonym record')
            else:
                # check element_national_id
                element_national_id = int(float(file_line['ELEMENT_NATIONAL_ID']))
                if element_national_id not in element_species_dict:
                    EBARUtils.displayMessage(messages,
                                             'WARNING: ' + element_national_id + ' does not have Species record')
                else:
                    # add
                    short_citation_author = None
                    if len(file_line['SHORT_CITATION_AUTHOR']) > 0:
                        short_citation_author = file_line['SHORT_CITATION_AUTHOR']
                    short_citation_year = None
                    if len(file_line['SHORT_CITATION_YEAR']) > 0:
                        short_citation_year = file_line['SHORT_CITATION_YEAR']
                    with arcpy.da.InsertCursor(param_geodatabase + '/Synonym',
                                               ['SpeciesID', 'SynonymName', 'SHORT_CITATION_AUTHOR',
                                                'SHORT_CITATION_YEAR']) as insert_cursor:
                        insert_cursor.insertRow([element_species_dict[element_national_id], scientific_name,
                                                 short_citation_author, short_citation_year])
                    EBARUtils.setNewID(param_geodatabase + '/Synonym', 'SynonymID',
                                       "SynonymName = '" + scientific_name + "'")
                    added += 1
            count += 1

        # summary and end time
        EBARUtils.displayMessage(messages, 'Summary:')
        EBARUtils.displayMessage(messages, 'Processed - ' + str(count))
        EBARUtils.displayMessage(messages, 'Added - ' + str(added))

        infile.close()
        return


# controlling process
if __name__ == '__main__':
    ast = AddSynonymsTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value='C:/GIS/EBAR/EBAR-KBA-Dev.gdb'
    param_csv = arcpy.Parameter()
    param_csv.value='C:/Users/rgree/OneDrive/EBAR/Data Mining/Species Prioritization/Biotics Sync/' + \
                    'BioticsSynonymExample8.csv'
    parameters = [param_geodatabase, param_csv]
    ast.RunAddSynonymsTool(parameters, None)
