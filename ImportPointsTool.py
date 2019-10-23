# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: ImportPointsTool.py
# ArcGIS Python tool for importing point data into the
# InputDataset and InputPoint tables of the EBAR geodatabase

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
#import sys
import EBARUtils
import arcpy
import io
import csv
import datetime
#import locale


# field mapping dictionaries for data sources
gbif_fields = {'quality_grade': None,
               'unique_id': 'gbifID',
               'uri': 'occurrenceID',
               'license': 'license',
               'scientific_name': 'species',
               'longitude': 'decimalLongitude',
               'latitude': 'decimalLatitude',
               'srs': 'geodeticDatum',
               'coordinates_obscured': None,
               'private_longitude': None,
               'private_latitude': None,
               'accuracy': 'coordinateUncertaintyInMeters',
               'private_accuracy': None,
               'year': 'year',
               'month': 'month',
               'day': 'day',
               'date': None,
               'basis_of_record': 'basisOfRecord',
               'individual_count': 'individualCount'}

ncc_gbif_fields = {'quality_grade': None,
                   'unique_id': 'gbifID',
                   'uri': 'occurrence',
                   'license': 'license',
                   'scientific_name': 'species',
                   'longitude': 'decimalLon',
                   'latitude': 'decimalLat',
                   'srs': None,
                   'coordinates_obscured': None,
                   'private_longitude': None,
                   'private_latitude': None,
                   'accuracy': 'coordinate',
                   'private_accuracy': None,
                   'year': 'year_',
                   'month': 'month_',
                   'day': 'day_',
                   'date': 'eventDate',
                   'basis_of_record': 'basisOfRec',
                   'individual_count': None}

vertnet_fields = {'quality_grade': None,
                  'unique_id': 'occurrenceid',
                  'uri': 'occurrenceid',
                  'license': 'license',
                  'scientific_name': 'name',
                  'longitude': 'longitude',
                  'latitude': 'latitude',
                  'srs': 'geodeticdatum',
                  'coordinates_obscured': None,
                  'private_longitude': None,
                  'private_latitude': None,
                  'accuracy': 'coordinateuncertaintyinmeters',
                  'private_accuracy': None,
                  'year': 'year',
                  'month': 'month',
                  'day': 'day',
                  'date': 'eventdate',
                  'basis_of_record': 'basisofrecord',
                  'individual_count': 'individualcount'}

ecoengine_fields = {'quality_grade': None,
                    'unique_id': 'key',
                    'uri': 'url',
                    'license': None,
                    'scientific_name': 'name',
                    'longitude': 'longitude',
                    'latitude': 'latitude',
                    'srs': None,
                    'coordinates_obscured': None,
                    'private_longitude': None,
                    'private_latitude': None,
                    'accuracy': 'coordinate_uncertainty_in_meters',
                    'private_accuracy': None,
                    'year': None,
                    'month': None,
                    'day': None,
                    'date': 'begin_date',
                    'basis_of_record': 'observation_type',
                    'individual_count': None}

inaturalist_fields = {'quality_grade': 'quality_grade',
                      'unique_id': 'id',
                      'uri': 'url',
                      'license': 'license',
                      'scientific_name': 'scientific_name',
                      'longitude': 'longitude',
                      'latitude': 'latitude',
                      'srs': None,
                      'coordinates_obscured': 'coordinates_obscured',
                      'private_longitude': 'private_longitude',
                      'private_latitude': 'private_latitude',
                      'accuracy': 'positional_accuracy',
                      'private_accuracy': 'private_positional_accuracy',
                      'year': None,
                      'month': None,
                      'day': None,
                      'date': 'observed_on',
                      'basis_of_record': None,
                      'individual_count': None}

bison_fields = {'quality_grade': None,
                'unique_id': 'occurrenceID',
                'uri': None,
                'license': 'license',
                'scientific_name': 'name',
                'longitude': 'longitude',
                'latitude': 'latitude',
                'srs': None,
                'coordinates_obscured': None,
                'private_longitude': None,
                'private_latitude': None,
                'accuracy': None,
                'private_accuracy': None,
                'year': 'year',
                'month': None,
                'day': None,
                'date': 'date',
                'basis_of_record': 'basisOfRecord',
                'individual_count': None}

canadensys_fields = {'quality_grade': None,
                     'unique_id': 'occurrenceID',
                     'uri': None,
                     'license': 'dcterms:license',
                     'scientific_name': 'species',
                     'longitude': 'decimalLongitude',
                     'latitude': 'decimalLatitude',
                     'srs': 'verbatimCoordinateSystem',
                     'coordinates_obscured': None,
                     'private_longitude': None,
                     'private_latitude': None,
                     'accuracy': 'coordinateUncertaintyInMeters',
                     'private_accuracy': None,
                     'year': 'year',
                     'month': 'month',
                     'day': None,
                     'date': 'eventDate',
                     'basis_of_record': 'basisOfRecord',
                     'individual_count': 'individualCount'}

ncc_endemics_fields = {'quality_grade': None,
                       'unique_id': 'OBSERVATIO',
                       'uri': None,
                       'license': None,
                       'scientific_name': 'SCIENTIFIC',
                       'longitude': 'latitude',
                       'latitude': 'longitude',
                       'srs': None,
                       'coordinates_obscured': None,
                       'private_longitude': None,
                       'private_latitude': None,
                       'accuracy': None,
                       'private_accuracy': None,
                       'year': 'OBSERVAT_3',
                       'month': None,
                       'day': None,
                       'date': 'OBSERVAT_2',
                       'basis_of_record': None,
                       'individual_count': None}


class ImportPointsTool:
    """Import point data into the InputDataset and InputPoint tables of the EBAR geodatabase"""
    def __init__(self):
        pass

    def CheckAddPoint(self, id_dict, geodatabase, dataset_source, input_dataset_id, species_id, file_line, field_dict):
        """If point already exists, check if needs update; otherwise, add"""
        # MaxDate
        max_date = None
        if field_dict['date']:
            # date field
            if file_line[field_dict['date']] not in ('NA', ''):
                if len(file_line[field_dict['date']]) == 20:
                    max_date_time = datetime.datetime.strptime(file_line[field_dict['date']], '%Y-%m-%dT%H:%M:%SZ')
                    max_date = max_date_time.date()
                elif str(len(file_line[field_dict['date']])) in ('18', '19'):
                    max_date_time = datetime.datetime.strptime(file_line[field_dict['date']], '%Y-%m-%d %H:%M:%S')
                    max_date = max_date_time.date()
                else:
                    max_date = datetime.datetime.strptime(file_line[field_dict['date']], '%Y-%m-%d')
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

        # CurrentHistorical (informs SpeciesEcoshape.Presence: C -> Present, U-> Presence Expected, H -> Historical)
        # [consider evaluating when generating range map instead of during import]
        if field_dict['basis_of_record']:
            if file_line[field_dict['basis_of_record']] == 'FOSSIL_SPECIMEN':
                # reject fossils records
                return None, 'fossil'
        current_historical = 'C'
        if max_date:
            if (datetime.datetime.now().year - max_date.year) > 40:
                current_historical = 'H'
        else:
            current_historical = 'U'

        # grade
        quality_grade = 'research'
        if field_dict['quality_grade']:
            quality_grade = file_line[field_dict['quality_grade']]

        # CoordinatesObscured
        coordinates_obscured = None
        if field_dict['coordinates_obscured']:
            if file_line[field_dict['coordinates_obscured']] in (True, 'TRUE', 'true', 'T', 't', 1):
                coordinates_obscured = True
            if file_line[field_dict['coordinates_obscured']] in (False, 'FALSE', 'false', 'F', 'f', 0):
                coordinates_obscured = False

        # check for existing point with same unique_id within the dataset source
        delete = False
        update = False
        if str(file_line[field_dict['unique_id']]) in id_dict:
            # already exists
            if quality_grade != 'research':
                # delete it because it has been downgraded
                with arcpy.da.SearchCursor(geodatabase + '/InputPoint', ['CoordinatesObscured'],
                                           "DatasetSourceUniqueID = '" + str(file_line[field_dict['unique_id']]) +
                                           "' AND InputDatasetID = " + str(input_dataset_id)) as cursor:
                    for row in cursor:
                        cursor.deleteRow()
                    del row
                    return id_dict[str(file_line[field_dict['unique_id']])], 'deleted'
            if not coordinates_obscured:
                # check if it has become unobscured
                with arcpy.da.SearchCursor(geodatabase + '/InputPoint', ['CoordinatesObscured'],
                                           "DatasetSourceUniqueID = '" + str(file_line[field_dict['unique_id']]) +
                                           "' AND InputDatasetID = " + str(input_dataset_id)) as cursor:
                    for row in EBARUtils.searchCursor(cursor):
                        update = row['CoordinatesObscured']
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

        # Geometry/Shape
        output_point = None
        input_point = None
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
                if file_line[field_dict['srs']] not in ('unknown', ''):
                    srs = EBARUtils.srs_dict[file_line[field_dict['srs']]]
            input_geometry = arcpy.PointGeometry(input_point, arcpy.SpatialReference(srs))
            output_geometry = input_geometry.projectAs(
                arcpy.SpatialReference(EBARUtils.srs_dict['North America Albers Equal Area Conic']))
            output_point = output_geometry.lastPoint

        # Accuracy
        accuracy = None
        if coordinates_obscured and not private_coords:
            accuracy = 26450
        elif field_dict['accuracy'] and not private_coords:
            if file_line[field_dict['accuracy']] not in ('NA', ''):
                accuracy = round(float(file_line[field_dict['accuracy']]))
        elif field_dict['private_accuracy'] and private_coords:
            if file_line[field_dict['private_accuracy']] not in ('NA', ''):
                accuracy = round(float(file_line[field_dict['private_accuracy']]))

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
                            'MinDate', 'MaxDate', 'CoordinatesObscured', 'Accuracy', 'CurrentHistorical',
                            'IndividualCount']
            with arcpy.da.InsertCursor(geodatabase + '/InputPoint', point_fields) as cursor:
                input_point_id = cursor.insertRow([output_point, input_dataset_id, str(file_line[field_dict['unique_id']]),
                                                   uri, license, species_id, None, max_date, coordinates_obscured,
                                                   accuracy, current_historical, individual_count])
            EBARUtils.setNewID(geodatabase + '/InputPoint', 'InputPointID', input_point_id)
            id_dict[str(file_line[field_dict['unique_id']])] = input_point_id
            return input_point_id, 'new'

    def RunImportPointsTool(self, parameters, messages):
        # debugging/testing
        #print(locale.getpreferredencoding())
        #return

        # check out any needed extension licenses
        #arcpy.CheckOutExtension('Spatial')

        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True
        if not messages:
            # for debugging, set workspace location
            arcpy.env.workspace = 'C:/GIS/EBAR/EBAR_outputs.gdb'

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
            param_dataset_type = parameters[6].valueAsText
            param_date_received = parameters[7].valueAsText
            param_restrictions = parameters[8].valueAsText
        else:
            # for debugging, hard code parameters
            param_geodatabase = 'C:/GIS/EBAR/EBAR_outputs.gdb'

            #param_raw_data_file = 'C:/Users/rgree/OneDrive/EBAR/Data Mining/Online_Platforms/GBIF_Yukon.csv'
            #param_dataset_name = 'GBIF for YK'
            #param_dataset_organization = 'Global Biodiversity Information Facility'
            #param_dataset_contact = 'https://www.gbif.org'
            #param_dataset_source = 'GBIF'
            #param_dataset_type = 'CSV'
            #param_date_received = 'September 28, 2019'
            #param_restrictions = ''

            #param_raw_data_file = 'C:/GIS/EBAR/NCC/NCC_Merge_GBIF.csv'
            #param_dataset_name = 'NCC GBIF Endemics'
            #param_dataset_organization = 'Global Biodiversity Information Facility'
            #param_dataset_contact = 'Andrea Hebb'
            #param_dataset_source = 'NCC_GBIF'
            #param_dataset_type = 'CSV'
            #param_date_received = 'October 15, 2019'
            #param_restrictions = ''

            #param_raw_data_file = 'C:/Users/rgree/OneDrive/Data_Mining/Import_Routine_Data/vertnet.csv'
            #param_dataset_name = 'VerNet Marmot'
            #param_dataset_organization = 'National Science Foundation'
            #param_dataset_contact = 'http://vertnet.org/'
            #param_dataset_source = 'VertNet'
            #param_dataset_type = 'CSV'
            #param_date_received = 'September 30, 2019'
            #param_restrictions = ''

            #param_raw_data_file = 'C:/Users/rgree/OneDrive/EBAR/Data Mining/Online_Platforms/ecoengine.csv'
            #param_dataset_name = 'Ecoengine Microseris'
            #param_dataset_organization = 'Berkeley Ecoinformatics Engine'
            #param_dataset_contact = 'https://ecoengine.berkeley.edu/'
            #param_dataset_source = 'Ecoengine'
            #param_dataset_type = 'CSV'
            #param_date_received = 'September 30, 2019'
            #param_restrictions = ''

            #param_raw_data_file = 'C:/Users/rgree/OneDrive/Data_Mining/Import_Routine_Data/' + \
            #    'All_CDN_iNat_Data.csv'
            ##param_raw_data_file = 'C:/Users/rgree/OneDrive/Data_Mining/Import_Routine_Data/' + \
            ##    'All_CDN_iNat_Data_test.csv'
            #param_dataset_name = 'iNaturalist All Canadian Unobscured Research Grade'
            #param_dataset_organization = 'California Academy of Sciences and the National Geographic Society'
            #param_dataset_contact = 'https://www.inaturalist.org/'
            #param_dataset_source = 'iNaturalist'
            #param_dataset_type = 'CSV'
            #param_date_received = 'October 2, 2019'
            #param_restrictions = ''

            #param_raw_data_file = 'C:/Users/rgree/OneDrive/EBAR/Data Mining/Online_Platforms/bison.csv'
            #param_dataset_name = 'BISON Microseris and Marmota'
            #param_dataset_organization = 'United States Geological Survey'
            #param_dataset_contact = 'https://bison.usgs.gov/'
            #param_dataset_source = 'BISON'
            #param_dataset_type = 'CSV'
            #param_date_received = 'September 30, 2019'
            #param_restrictions = ''

            #param_raw_data_file = 'C:/Users/rgree/OneDrive/EBAR/Data Mining/Online_Platforms/' + \
            #    'Canadensys-records-2019-10-09.csv'
            #param_dataset_name = 'Canadensys Polygonum'
            #param_dataset_organization = 'Université de Montréal Biodiversity Centre'
            #param_dataset_contact = 'http://www.canadensys.net/'
            #param_dataset_source = 'Canadensys'
            #param_dataset_type = 'CSV'
            #param_date_received = 'October 9, 2019'
            #param_restrictions = ''

            param_raw_data_file = 'C:/GIS/EBAR/NCC/NCC_Species_Obs_20190521.csv'
            param_dataset_name = 'NCC Endemics'
            param_dataset_organization = 'Nature Conservancy of Canada'
            param_dataset_contact = 'Andrea Hebb'
            param_dataset_source = 'NCCEndemics'
            param_dataset_type = 'CSV'
            param_date_received = 'October 15, 2019'
            param_restrictions = ''

        # check parameters
        field_dict = gbif_fields
        if param_dataset_source == 'NCC_GBIF':
            field_dict = ncc_gbif_fields
        elif param_dataset_source == 'VertNet':
            field_dict = vertnet_fields
        elif param_dataset_source == 'Ecoengine':
            field_dict = ecoengine_fields
        elif param_dataset_source == 'iNaturalist':
            field_dict = inaturalist_fields
        elif param_dataset_source == 'BISON':
            field_dict = bison_fields
        elif param_dataset_source == 'Canadensys':
            field_dict = canadensys_fields
        if param_dataset_source == 'NCCEndemics':
            field_dict = ncc_endemics_fields

        # check/add InputDataset row
        dataset = param_dataset_name + ', ' + param_dataset_source + ', ' + str(param_date_received)
        EBARUtils.displayMessage(messages, 'Checking for dataset [' + dataset + '] and adding if new')
        input_dataset_id, dataset_exists = EBARUtils.checkAddInputDataset(param_geodatabase,
                                                                          param_dataset_name,
                                                                          param_dataset_organization,
                                                                          param_dataset_contact,
                                                                          param_dataset_source,
                                                                          param_dataset_type,
                                                                          param_date_received,
                                                                          param_restrictions)
        EBARUtils.setNewID(param_geodatabase + '/InputDataset', 'InputDatasetID', input_dataset_id)

        # read existing species into dict
        EBARUtils.displayMessage(messages, 'Reading existing species')
        species_dict = EBARUtils.readSpecies(param_geodatabase)

        # read existing unique IDs into dict
        EBARUtils.displayMessage(messages, 'Reading existing unique IDs')
        id_dict = EBARUtils.readDatasetSourceUniqueIDs(param_geodatabase, param_dataset_source)

        # try to open data file as a csv
        infile = io.open(param_raw_data_file, 'r', encoding='mbcs') # mbcs encoding is Windows ANSI
        reader = csv.DictReader(infile)

        # process all file lines
        EBARUtils.displayMessage(messages, 'Processing file lines')
        count = 0
        fossils = 0
        duplicates = 0
        updates = 0
        non_research = 0
        deleted = 0
        for file_line in reader:
            count += 1
            if count % 1000 == 0:
                EBARUtils.displayMessage(messages, 'Processed ' + str(count))
            # check/add species for current line
            species_id, species_exists = EBARUtils.checkAddSpecies(species_dict, param_geodatabase,
                                                                   file_line[field_dict['scientific_name']])
            # check/add point for current line
            input_point_id, status = self.CheckAddPoint(id_dict, param_geodatabase, param_dataset_source,
                                                        input_dataset_id, species_id, file_line, field_dict)
            if status == 'fossil':
                fossil += 1
            elif status == 'duplicate':
                duplicates += 1
            elif status == 'updated':
                updates += 1
            elif status == 'non-research':
                non_research += 1
            elif status == 'deleted':
                non_research += 1
                deleted += 1

        # summary and end time
        EBARUtils.displayMessage(messages, 'Processed ' + str(count))
        EBARUtils.displayMessage(messages, 'Fossils ' + str(fossils))
        EBARUtils.displayMessage(messages, 'Duplicates ' + str(duplicates))
        EBARUtils.displayMessage(messages, 'Duplicates updated ' + str(updates))
        EBARUtils.displayMessage(messages, 'Non-research ' + str(non_research))
        EBARUtils.displayMessage(messages, 'Non-research deleted ' + str(deleted))
        end_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'End time: ' + str(end_time))
        elapsed_time = end_time - start_time
        EBARUtils.displayMessage(messages, 'Elapsed time: ' + str(elapsed_time))
        return


# controlling process
if __name__ == '__main__':
    ipt = ImportPointsTool()
    # hard code parameters for debugging
    ipt.RunImportPointsTool(None, None)
