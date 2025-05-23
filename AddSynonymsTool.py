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

    def runAddSynonymsTool(self, parameters, messages):
        # make variables for parms
        param_geodatabase = parameters[0].valueAsText
        param_csvs = parameters[1].valueAsText
        param_csvs = param_csvs.replace("'", '')
        param_csvs = param_csvs.split(';')

        for param_csv in param_csvs:
            EBARUtils.displayMessage(messages, 'File: ' + param_csv)
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
                if scientific_name.lower() in species_dict:
                    EBARUtils.displayMessage(messages, 'WARNING: ' + scientific_name + ' already has Species record')
                elif scientific_name.lower() in synonym_dict:
                    EBARUtils.displayMessage(messages, 'WARNING: ' + scientific_name + ' already has Synonym record')
                else:
                    # check element_national_id
                    element_national_id = int(float(file_line['ELEMENT_NATIONAL_ID']))
                    if element_national_id not in element_species_dict:
                        EBARUtils.displayMessage(messages,
                                                'WARNING: ' + str(element_national_id) + ' does not have Species record')
                    else:
                        # add
                        short_citation_author = None
                        if len(file_line['SHORT_CITATION_AUTHOR']) > 0:
                            short_citation_author = file_line['SHORT_CITATION_AUTHOR']
                        short_citation_year = None
                        if len(file_line['SHORT_CITATION_YEAR']) > 0:
                            short_citation_year = file_line['SHORT_CITATION_YEAR']
                        formatted_full_citation = None
                        if len(file_line['FORMATTED_FULL_CITATION']) > 0:
                            formatted_full_citation = file_line['FORMATTED_FULL_CITATION']
                        author_name = None
                        if len(file_line['AUTHOR_NAME']) > 0:
                            author_name = file_line['AUTHOR_NAME']
                        insert_cursor = arcpy.da.InsertCursor(param_geodatabase + '/Synonym',
                                                            ['SpeciesID', 'SynonymName', 'SHORT_CITATION_AUTHOR',
                                                            'SHORT_CITATION_YEAR', 'FORMATTED_FULL_CITATION',
                                                            'AUTHOR_NAME'])
                        insert_cursor.insertRow([element_species_dict[element_national_id], scientific_name,
                                                short_citation_author, short_citation_year, formatted_full_citation,
                                                author_name])
                        del insert_cursor
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
    param_geodatabase.value = 'D:/GIS/EBAR/EBARDev2.gdb'
    param_csvs = arcpy.Parameter()
    param_csvs.value = "'D:/GIS/EBAR/EBARTools/Samples/BioticsSynonymExample.csv';'D:/GIS/EBAR/EBARTools/Samples/BioticsSynonymExample.csv'"
    parameters = [param_geodatabase, param_csvs]
    ast.runAddSynonymsTool(parameters, None)
