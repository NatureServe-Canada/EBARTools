# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: ImportTabularDataTool.py
# ArcGIS Python tool for importing tabular data into the
# InputDataset and InputPoint tables of the EBAR geodatabase

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import sys
import traceback
import arcpy
import io
import csv
import datetime
#import locale
import EBARUtils
import TabularFieldMapping


class ImportTabularDataTool:
    """Import point data into the InputDataset and InputPoint tables of the EBAR geodatabase"""
    def __init__(self):
        pass

    def RunImportTabularDataTool(self, parameters, messages):
        # debugging/testing
        #print(locale.getpreferredencoding())
        #print(str(EBARUtils.estimateAccuracy(80.0)))
        #return

        # check out any needed extension licenses
        #arcpy.CheckOutExtension('Spatial')

        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        if parameters:
            # passed from tool user interface
            param_geodatabase = parameters[0].valueAsText
            param_raw_data_file = parameters[1].valueAsText
            param_dataset_name = parameters[2].valueAsText
            param_dataset_organization = parameters[3].valueAsText
            param_dataset_contact = parameters[4].valueAsText
            param_dataset_source = parameters[5].valueAsText
            #param_dataset_type = parameters[6].valueAsText
            param_date_received = parameters[6].valueAsText
            param_restrictions = parameters[7].valueAsText
        else:
            # for debugging, hard code parameters
            param_geodatabase = 'C:/GIS/EBAR/EBAR_test.gdb'

            #param_raw_data_file = 'C:/Users/rgree/OneDrive/EBAR_Sensitive_Material/Import_Routine_Data/Real_Data/' + \
            #                      'Endemics_vertnet.csv'
            #param_dataset_name = 'VerNet Endemics'
            #param_dataset_organization = 'National Science Foundation'
            #param_dataset_contact = 'http://vertnet.org/'
            #param_dataset_source = 'VertNet'
            #param_date_received = 'October 15, 2019'
            #param_restrictions = None

            #param_raw_data_file = 'C:/Users/rgree/OneDrive/EBAR/Data Mining/Online_Platforms/ecoengine.csv'
            #param_dataset_name = 'Ecoengine Microseris'
            #param_dataset_organization = 'Berkeley Ecoinformatics Engine'
            #param_dataset_contact = 'https://ecoengine.berkeley.edu/'
            #param_dataset_source = 'Ecoengine'
            #param_date_received = 'September 30, 2019'
            #param_restrictions = None

            param_raw_data_file = 'C:/Users/rgree/OneDrive/EBAR_Sensitive_Material/Import_Routine_Data/Real_Data/' + \
                                  'GBIF_BC.csv'
            param_dataset_name = 'BC GBIF'
            param_dataset_organization = 'Global Biodiversity Information Facility'
            param_dataset_contact = 'http://gbif.org'
            param_dataset_source = 'GBIF'
            param_date_received = 'October 9, 2019'
            param_restrictions = None

        # use passed geodatabase as workspace (still seems to go to default geodatabase)
        arcpy.env.workspace = param_geodatabase

        # check parameters
        # get dataset source id
        with arcpy.da.SearchCursor(param_geodatabase + '/DatasetSource', ['DatasetSourceID'],
                                   "DatasetSourceName = '" + param_dataset_source + "'") as cursor:
            for row in EBARUtils.searchCursor(cursor):
                dataset_source_id = row['DatasetSourceID']
            del row
        # match field_dict with source
        field_dict = TabularFieldMapping.tabular_field_mapping_dict[param_dataset_source]

        # check/add InputDataset row
        dataset = param_dataset_name + ', ' + param_dataset_source + ', ' + str(param_date_received)
        EBARUtils.displayMessage(messages, 'Checking for dataset [' + dataset + '] and adding if new')
        input_dataset_id, dataset_exists = EBARUtils.checkAddInputDataset(param_geodatabase,
                                                                          param_dataset_name,
                                                                          param_dataset_organization,
                                                                          param_dataset_contact,
                                                                          dataset_source_id,
                                                                          param_date_received,
                                                                          param_restrictions)
        if not dataset_exists:
            EBARUtils.setNewID(param_geodatabase + '/InputDataset', 'InputDatasetID', 'OBJECTID = ' + \
                               str(input_dataset_id))

        # read existing species into dict
        EBARUtils.displayMessage(messages, 'Reading full list of Species and Synonyms')
        species_dict = EBARUtils.readSpecies(param_geodatabase)
        synonym_id_dict = EBARUtils.readSynonymIDs(param_geodatabase)
        synonym_species_id_dict = EBARUtils.readSynonymSpeciesIDs(param_geodatabase)

        # read existing unique IDs into dict
        EBARUtils.displayMessage(messages, 'Reading existing Unique IDs for the Dataset Source')
        id_dict = EBARUtils.readDatasetSourceUniqueIDs(param_geodatabase, dataset_source_id, 'Point')

        # try to open data file as a csv
        infile = io.open(param_raw_data_file, 'r', encoding='mbcs') # mbcs encoding is Windows ANSI
        reader = csv.DictReader(infile)

        # process all file lines
        EBARUtils.displayMessage(messages, 'Processing file lines')
        count = 0
        no_species_match = 0
        no_match_list = []
        no_coords = 0
        inaccurate = 0
        fossils = 0
        duplicates = 0
        updates = 0
        non_research = 0
        deleted = 0
        try:
            for file_line in reader:
                # check/add point for current line
                input_point_id, status = self.CheckAddPoint(id_dict, param_geodatabase, input_dataset_id, species_dict,
                                                            synonym_id_dict, synonym_species_id_dict, file_line,
                                                            field_dict, no_match_list, messages)
                # increment/report counts
                count += 1
                if count % 1000 == 0:
                    EBARUtils.displayMessage(messages, 'Processed ' + str(count))
                if status == 'no_species_match':
                    no_species_match += 1
                elif status == 'no_coords':
                    no_coords += 1
                elif status == 'inaccurate':
                    inaccurate += 1
                elif status == 'fossil':
                    fossil += 1
                elif status == 'duplicate':
                    duplicates += 1
                elif status == 'updated':
                    duplicates += 1
                    updates += 1
                elif status == 'non-research':
                    non_research += 1
                elif status == 'deleted':
                    non_research += 1
                    deleted += 1
        except:
            # output error messages in exception so that summary of processing thus far gets displayed in finally
            EBARUtils.displayMessage(messages, '\nERROR processing file row ' + str(count + 1))
            tb = sys.exc_info()[2]
            tbinfo = ''
            for tbitem in traceback.format_tb(tb):
                tbinfo += tbitem
            pymsgs = 'Python ERROR:\nTraceback info:\n' + tbinfo + 'Error Info:\n' + str(sys.exc_info()[1])
            EBARUtils.displayMessage(messages, pymsgs)
            arcmsgs = 'ArcPy ERROR:\n' + arcpy.GetMessages(2)
            EBARUtils.displayMessage(messages, arcmsgs)
            EBARUtils.displayMessage(messages, '')

        finally:
            # summary and end time
            EBARUtils.displayMessage(messages, 'Summary:')
            EBARUtils.displayMessage(messages, 'Processed - ' + str(count))
            EBARUtils.displayMessage(messages, 'Species not matched - ' + str(no_species_match))
            EBARUtils.displayMessage(messages, 'No coordinates - ' + str(no_coords))
            EBARUtils.displayMessage(messages,
                                     'Accuracy worse than ' + str(EBARUtils.worst_accuracy) + ' m - ' + str(inaccurate))
            EBARUtils.displayMessage(messages, 'Fossils - ' + str(fossils))
            EBARUtils.displayMessage(messages, 'Duplicates - ' + str(duplicates))
            EBARUtils.displayMessage(messages, 'Duplicates updated - ' + str(updates))
            EBARUtils.displayMessage(messages, 'Non-research - ' + str(non_research))
            EBARUtils.displayMessage(messages, 'Non-research deleted - ' + str(deleted))
            end_time = datetime.datetime.now()
            EBARUtils.displayMessage(messages, 'End time: ' + str(end_time))
            elapsed_time = end_time - start_time
            EBARUtils.displayMessage(messages, 'Elapsed time: ' + str(elapsed_time))

        infile.close()
        return

    def CheckAddPoint(self, id_dict, geodatabase, input_dataset_id, species_dict, synonym_id_dict,
                      synonym_species_id_dict, file_line, field_dict, no_match_list, messages):
        """If point already exists, check if needs update; otherwise, add"""
        # check for species
        if (file_line[field_dict['scientific_name']] not in species_dict and
            file_line[field_dict['scientific_name']] not in synonym_id_dict):
            if file_line[field_dict['scientific_name']] not in no_match_list:
                no_match_list.append(file_line[field_dict['scientific_name']])
                EBARUtils.displayMessage(messages,
                                         'WARNING: No match for species ' + file_line[field_dict['scientific_name']])
            return None, 'no_species_match'
        else:
            synonym_id = None
            if file_line[field_dict['scientific_name']] in species_dict:
                species_id = species_dict[file_line[field_dict['scientific_name']]]
            else:
                species_id = synonym_species_id_dict[file_line[field_dict['scientific_name']]]
                synonym_id = synonym_id_dict[file_line[field_dict['scientific_name']]]

        # CoordinatesObscured
        coordinates_obscured = False
        if field_dict['coordinates_obscured']:
            if file_line[field_dict['coordinates_obscured']] in (True, 'TRUE', 'true', 'T', 't', 1):
                coordinates_obscured = True
            #if file_line[field_dict['coordinates_obscured']] in (False, 'FALSE', 'false', 'F', 'f', 0):
            #    coordinates_obscured = False

        # Geometry/Shape
        input_point = None
        output_point = None
        private_coords = False
        if coordinates_obscured:
            # check for private lon/lat
            if field_dict['private_longitude'] and field_dict['private_latitude']:
                if (file_line[field_dict['private_longitude']] not in ('NA', '') and
                    file_line[field_dict['private_latitude']] not in ('NA', '')):
                    private_coords = True
                    input_point = arcpy.Point(float(file_line[field_dict['private_longitude']]),
                                              float(file_line[field_dict['private_latitude']]))
        if not private_coords:
            if (file_line[field_dict['longitude']] not in ('NA', '') and
                file_line[field_dict['latitude']] not in ('NA', '')):
                input_point = arcpy.Point(float(file_line[field_dict['longitude']]),
                                          float(file_line[field_dict['latitude']]))
        if input_point:
            # assume WGS84 if not provided
            srs = EBARUtils.srs_dict['WGS84']
            if field_dict['srs']:
                if file_line[field_dict['srs']] not in ('unknown', 'not recorded', ''):
                    srs = EBARUtils.srs_dict[file_line[field_dict['srs']]]
            input_geometry = arcpy.PointGeometry(input_point, arcpy.SpatialReference(srs))
            output_geometry = input_geometry.projectAs(
                arcpy.SpatialReference(EBARUtils.srs_dict['North America Albers Equal Area Conic']))
            output_point = output_geometry.lastPoint
        if not output_point:
            return None, 'no_coords'

        # Accuracy
        accuracy = None
        if (not coordinates_obscured) or private_coords:
            if field_dict['accuracy']:
                if file_line[field_dict['accuracy']] not in ('NA', ''):
                    accuracy = round(float(file_line[field_dict['accuracy']]))
                    if accuracy > EBARUtils.worst_accuracy:
                        return None, 'inaccurate'
        else:
            accuracy = EBARUtils.estimateAccuracy(input_point.Y)

        # MaxDate
        max_date = None
        if field_dict['date']:
            # date field
            max_date = EBARUtils.extractDate(file_line[field_dict['date']])
        if not max_date:
            # separate ymd fields
            if field_dict['year']:
                if file_line[field_dict['year']] not in ('NA', ''):
                    max_year = int(file_line[field_dict['year']])
                    max_month = 1
                    if field_dict['month']:
                        if file_line[field_dict['month']] not in ('NA', ''):
                            max_month = int(file_line[field_dict['month']])
                    max_day = 1
                    if field_dict['day']:
                        if file_line[field_dict['day']] not in ('NA', ''):
                            max_day = int(file_line[field_dict['day']])
                    max_date = datetime.datetime(max_year, max_month, max_day)

        # reject fossils records
        if field_dict['basis_of_record']:
            if file_line[field_dict['basis_of_record']] == 'FOSSIL_SPECIMEN':
                return None, 'fossil'

        # grade
        quality_grade = 'research'
        if field_dict['quality_grade']:
            quality_grade = file_line[field_dict['quality_grade']]

        # check for existing point with same unique_id within the dataset source
        delete = False
        update = False
        if str(file_line[field_dict['unique_id']]) in id_dict:
            # already exists
            if quality_grade != 'research':
                # delete it because it has been downgraded
                with arcpy.da.UpdateCursor(geodatabase + '/InputPoint', ['CoordinatesObscured'],
                                           "DatasetSourceUniqueID = '" + str(file_line[field_dict['unique_id']]) +
                                           "' AND InputDatasetID = " + str(input_dataset_id)) as cursor:
                    row = None
                    for row in cursor:
                        cursor.deleteRow()
                    if row:
                        del row
                    return id_dict[str(file_line[field_dict['unique_id']])], 'deleted'
            if not coordinates_obscured:
                # check if it has become unobscured
                with arcpy.da.SearchCursor(geodatabase + '/InputPoint', ['CoordinatesObscured'],
                                           "DatasetSourceUniqueID = '" + str(file_line[field_dict['unique_id']]) +
                                           "' AND InputDatasetID = " + str(input_dataset_id)) as cursor:
                    row = None
                    for row in EBARUtils.searchCursor(cursor):
                        update = row['CoordinatesObscured']
                    if row:
                        del row
            if not update:
                # existing record that does not need to be updated
                return id_dict[str(file_line[field_dict['unique_id']])], 'duplicate'

        # don't add non research grade
        if quality_grade != 'research':
            return None, 'non-research'

        # URI
        uri = None
        if field_dict['uri']:
            uri = file_line[field_dict['uri']]

        # License
        license = None
        if field_dict['license']:
            license = file_line[field_dict['license']]

        # IndividualCount
        individual_count = None
        if field_dict['individual_count']:
            if file_line[field_dict['individual_count']] not in ('NA', ''):
                individual_count = int(file_line[field_dict['individual_count']])

        # update or insert
        if update:
            with arcpy.da.UpdateCursor(geodatabase + '/InputPoint',
                                       ['SHAPE@XY', 'InputPointID', 'CoordinatesObscured', 'Accuracy'],
                                       "DatasetSourceUniqueID = '" + str(file_line[field_dict['unique_id']]) +
                                       "' AND InputDatasetID = " + str(input_dataset_id)) as cursor:
                for row in EBARUtils.updateCursor(cursor):
                    input_point_id = row['InputPointID']
                    cursor.updateRow([output_point, input_point_id, coordinates_obscured, accuracy])
                del row
            return input_point_id, 'updated'
        else:
            # insert, set new id and return
            point_fields = ['SHAPE@XY', 'InputDatasetID', 'DatasetSourceUniqueID', 'URI', 'License', 'SpeciesID',
                            'SynonymID', 'MaxDate', 'CoordinatesObscured', 'Accuracy', 'IndividualCount']
            with arcpy.da.InsertCursor(geodatabase + '/InputPoint', point_fields) as cursor:
                input_point_id = cursor.insertRow([output_point, input_dataset_id,
                                                   str(file_line[field_dict['unique_id']]), uri, license, species_id,
                                                   synonym_id, max_date, coordinates_obscured, accuracy,
                                                   individual_count])
            EBARUtils.setNewID(geodatabase + '/InputPoint', 'InputPointID', 'OBJECTID = ' + str(input_point_id))
            id_dict[str(file_line[field_dict['unique_id']])] = input_point_id
            return input_point_id, 'new'


# controlling process
if __name__ == '__main__':
    itd = ImportTabularDataTool()
    # hard code parameters for debugging
    itd.RunImportTabularDataTool(None, None)
