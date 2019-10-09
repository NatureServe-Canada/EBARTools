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
#gbif_fields = ['basisOfRecord', 'individualCount', 'scientificName', 'species', 'decimalLongitude',
#               'decimalLatitude', 'coordinateUncertaintyInMeters', 'stateProvince', 'year', 'month', 'day',
#               'issues', 'license', 'geodeticDatum', 'countryCode', 'locality', 'gbifID', 'occurrenceID',
#               'recordedBy', 'institutionCode', 'informationWithheld', 'occurrenceRemarks', 'dateIdentified',
#               'references','verbatimLocality','identifiedBy']
gbif_fields = {'unique_id': 'gbifID',
               'uri': 'occurrenceID',
               'license': 'license',
               'scientific_name': 'species',
               'longitude': 'decimalLongitude',
               'latitude': 'decimalLatitude',
               'srs': 'geodeticDatum',
               'year': 'year',
               'month': 'month',
               'day': 'day',
               'date': None,
               'coordinates_obscured': None,
               'accuracy': 'coordinateUncertaintyInMeters',
               'basis_of_record': 'basisOfRecord',
               'individual_count': 'individualCount'}

#vertnet_fields = ['name', 'longitude', 'latitude', 'prov', 'month', 'verbatimcoordinatesystem', 'day', 'occurrenceid',
#                  'identificationqualifier', 'coordinateuncertaintyinmeters', 'year', 'basisofrecord',
#                  'geodeticdatum', 'georeferenceprotocol', 'stateprovince', 'verbatimlocality', 'references',
#                  'license', 'georeferenceverificationstatus', 'eventdate', 'individualcount',
#                  'catalognumber', 'locality', 'locationremarks', 'occurrenceremarks', 'coordinateprecision']
vertnet_fields = {'unique_id': 'occurrenceid',
                  'uri': 'occurrenceid',
                  'license': 'license',
                  'scientific_name': 'name',
                  'longitude': 'longitude',
                  'latitude': 'latitude',
                  'srs': 'geodeticdatum',
                  'year': 'year',
                  'month': 'month',
                  'day': 'day',
                  'date': 'eventdate',
                  'coordinates_obscured': None,
                  'accuracy': 'coordinateuncertaintyinmeters',
                  'basis_of_record': 'basisofrecord',
                  'individual_count': 'individualcount'}

#ecoengine_fields = ['url', 'key', 'longitude', 'latitude', 'observation_type', 'name', source','locality',
#                    'coordinate_uncertainty_in_meters', 'recorded_by', 'prov', 'begin_date']
ecoengine_fields = {'unique_id': 'key',
                    'uri': 'url',
                    'license': None,
                    'scientific_name': 'name',
                    'longitude': 'longitude',
                    'latitude': 'latitude',
                    'srs': None,
                    'year': None,
                    'month': None,
                    'day': None,
                    'date': 'begin_date',
                    'coordinates_obscured': None,
                    'accuracy': 'coordinate_uncertainty_in_meters',
                    'basis_of_record': 'observation_type',
                    'individual_count': None}

#inaturalist_fields = ['id', 'observed_on_string', 'observed_on', 'time_observed_at', 'time_zone', 'out_of_range',
#                      'user_id', 'user_login', 'created_at', 'quality_grade', 'license', 'url', 'image_url',
#                      'sound_url', 'tag_list', 'description', 'id_please', 'num_identification_agreements',
#                      'num_identification_disagreements', 'captive_cultivated', 'place_guess', 'latitude',
#                      'longitude', 'positional_accuracy', 'private_place_guess', 'private_latitude',
#                      'private_longitude', 'private_positional_accuracy', 'geoprivacy', 'taxon_geoprivacy',
#                      'coordinates_obscured', 'positioning_method', 'positioning_device', 'place_town_name',
#                      'place_county_name', 'place_state_name', 'place_country_name', 'place_admin1_name',
#                      'place_admin2_name', 'species_guess', 'scientific_name', 'common_name', 'iconic_taxon_name',
#                      'taxon_id']
inaturalist_fields = {'unique_id': 'id',
                      'uri': 'url',
                      'license': 'license',
                      'scientific_name': 'scientific_name',
                      'longitude': 'longitude',
                      'latitude': 'latitude',
                      'srs': None,
                      'year': None,
                      'month': None,
                      'day': None,
                      'date': 'observed_on',
                      'coordinates_obscured': 'coordinates_obscured',
                      'accuracy': 'positional_accuracy',
                      'basis_of_record': None,
                      'individual_count': None}

#bison_fields = ['catalogNumber', 'providedScientificName', 'name', 'ambiguous', 'generalComments', 'verbatimLocality',
#                'occurrenceID', 'longitude', 'basisOfRecord', 'collectionID', 'institutionID', 'license', 'latitude',
#                'provider', 'centroid', 'date', 'year', 'recordedBy', 'prov', 'geo']
bison_fields = {'unique_id': 'occurrenceID',
                'uri': None,
                'license': 'license',
                'scientific_name': 'name',
                'longitude': 'longitude',
                'latitude': 'latitude',
                'srs': None,
                'year': 'year',
                'month': None,
                'day': None,
                'date': 'date',
                'coordinates_obscured': None,
                'accuracy': None,
                'basis_of_record': 'basisOfRecord',
                'individual_count': None}

#canadensys_fields = ['dcterms:license', 'institutionCode', 'collectionCode', 'datasetName', 'basisOfRecord',
#                     'occurrenceID', 'catalogNumber', 'recordNumber', 'recordedBy', 'individualCount', 'sex',
#                     'reproductiveCondition', 'establishmentMeans', 'occurrenceStatus', 'occurrenceRemarks',
#                     'eventID', 'eventDate', 'year', 'month', 'locationID', 'country', 'countryCode', 'stateProvince',
#                     'locality', 'minimumElevationInMeters', 'maximumElevationInMeters', 'maximumDepthInMeters',
#                     'maximumDepthInMeters', 'locationRemarks', 'decimalLatitude', 'decimalLongitude',
#                     'coordinateUncertaintyInMeters', 'verbatimLatitude', 'verbatimLongitude',
#                     'verbatimCoordinateSystem', 'georeference_verification_status', 'identificationQualifier',
#                     'typeStatus', 'identifiedBy', 'dateIdentified', 'identificationVerificationStatus',
#                     'taxonConceptID', 'scientificName', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus',
#                     'taxonRank', 'vernacularName', 'species', 'verbatimIdentificationQualifier', 'provenance',
#                     'recordID', 'verbatimBasisOfRecord']
canadensys_fields = {'unique_id': 'occurrenceID',
                     'uri': None,
                     'license': 'dcterms:license',
                     'scientific_name': 'species',
                     'longitude': 'decimalLongitude',
                     'latitude': 'decimalLatitude',
                     'srs': 'verbatimCoordinateSystem',
                     'year': 'year',
                     'month': 'month',
                     'day': None,
                     'date': 'eventDate',
                     'coordinates_obscured': None,
                     'accuracy': 'coordinateUncertaintyInMeters',
                     'basis_of_record': 'basisOfRecord',
                     'individual_count': 'individualCount'}


class ImportPointsTool:
    """Import point data into the InputDataset and InputPoint tables of the EBAR geodatabase"""
    def __init__(self):
        pass

    def CheckAddPoint(self, id_dict, geodatabase, input_dataset_id, species_id, file_line, field_dict):
        """If point already exists, return id and true; otherwise, add and return id and false"""
        # check for existing point with same unique_id within the dataset source
        if str(file_line[field_dict['unique_id']]) in id_dict:
            return id_dict[str(file_line[field_dict['unique_id']])], True

        # add new
        # Geometry/Shape
        output_point = None
        if (file_line[field_dict['longitude']] not in ('NA', '') and
            file_line[field_dict['latitude']] not in ('NA', '')):
            input_point = arcpy.Point(float(file_line[field_dict['longitude']]), float(file_line[field_dict['latitude']]))
            # assume WGS84 if not provided
            srs = EBARUtils.srs_dict['WGS84']
            if field_dict['srs']:
                if file_line[field_dict['srs']] not in ('unknown', ''):
                    srs = EBARUtils.srs_dict[file_line[field_dict['srs']]]
            input_geometry = arcpy.PointGeometry(input_point, arcpy.SpatialReference(srs))
            output_geometry = input_geometry.projectAs(
                arcpy.SpatialReference(EBARUtils.srs_dict['North America Albers Equal Area Conic']))
            output_point = output_geometry.lastPoint

        # URI
        uri = None
        if field_dict['uri']:
            uri = file_line[field_dict['uri']]

        # License
        license = None
        if field_dict['license']:
            license = file_line[field_dict['license']]

        # MaxDate
        max_date = None
        if field_dict['date']:
            # date field
            if file_line[field_dict['date']] != 'NA':
                max_date = datetime.datetime.strptime(file_line[field_dict['date']], '%Y-%m-%d')
        if not max_date:
            # separate ymd fields
            if file_line[field_dict['year']] != 'NA':
                max_year = int(file_line[field_dict['year']])
                max_month = 1
                if file_line[field_dict['month']] != 'NA':
                    max_month = int(file_line[field_dict['month']])
                max_day = 1
                if file_line[field_dict['day']] != 'NA':
                    max_day = int(file_line[field_dict['day']])
                max_date = datetime.datetime(max_year, max_month, max_day)

        # CoordinatesObscured
        coordinates_obscured = None
        if field_dict['coordinates_obscured']:
            if file_line[field_dict['coordinates_obscured']] in (True, 'TRUE', 'true', 'T', 't', 1):
                coordinates_obscured = True
            if file_line[field_dict['coordinates_obscured']] in (False, 'FALSE', 'false', 'F', 'f', 0):
                coordinates_obscured = False

        # Accuracy
        accuracy = None
        if field_dict['accuracy']:
            if file_line[field_dict['accuracy']] not in ('NA', ''):
                accuracy = round(float(file_line[field_dict['accuracy']]))

        # CurrentHistorical
        current_historical = 'C'
        if field_dict['basis_of_record']:
            if file_line[field_dict['basis_of_record']] == 'FOSSIL_SPECIMEN':
                current_historical = 'H'
        if current_historical == 'C':
            if max_date:
                if (datetime.datetime.now().year - max_date.year) > 40:
                    current_historical = 'H'
            else:
                current_historical = 'U'

        # IndividualCount
        individual_count = None
        if field_dict['individual_count']:
            if file_line[field_dict['individual_count']] not in ('NA', ''):
                individual_count = int(file_line[field_dict['individual_count']])

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
        return input_point_id, False

    def RunImportPointsTool(self, parameters, messages):
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
            #    'All_CDN_Research_Unobsc_Data.csv'
            ##param_raw_data_file = 'C:/Users/rgree/OneDrive/Data_Mining/Import_Routine_Data/inat_test.csv'
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

            param_raw_data_file = 'C:/Users/rgree/OneDrive/EBAR/Data Mining/Online_Platforms/' + \
                'Canadensys-records-2019-10-09.csv'
            param_dataset_name = 'Canadensys Polygonum'
            param_dataset_organization = 'Université de Montréal Biodiversity Centre'
            param_dataset_contact = 'http://www.canadensys.net/'
            param_dataset_source = 'Canadensys'
            param_dataset_type = 'CSV'
            param_date_received = 'October 9, 2019'
            param_restrictions = ''

        # check parameters
        field_dict = gbif_fields
        if param_dataset_source == 'VertNet':
            field_dict = vertnet_fields
        elif param_dataset_source == 'Ecoengine':
            field_dict = ecoengine_fields
        elif param_dataset_source == 'iNaturalist':
            field_dict = inaturalist_fields
        elif param_dataset_source == 'BISON':
            field_dict = bison_fields
        elif param_dataset_source == 'Canadensys':
            field_dict = canadensys_fields

        # check/add InputDataset row
        EBARUtils.displayMessage(messages, 'Checking for dataset and adding if new')
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
        duplicates = 0
        for file_line in reader:
            count += 1
            if count % 1000 == 0:
                EBARUtils.displayMessage(messages, 'Processed ' + str(count))
            # check/add species for current line
            species_id, species_exists = EBARUtils.checkAddSpecies(species_dict, param_geodatabase,
                                                                   file_line[field_dict['scientific_name']])
            # check/add point for current line
            input_point_id, point_exists = self.CheckAddPoint(id_dict, param_geodatabase, input_dataset_id,
                                                              species_id, file_line, field_dict)
            if point_exists:
                duplicates += 1

        # summary and end time
        EBARUtils.displayMessage(messages, 'Processed ' + str(count))
        EBARUtils.displayMessage(messages, 'Duplicates ' + str(duplicates))
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
