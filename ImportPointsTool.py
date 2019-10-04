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
               'accuracy': 'coordinateUncertaintyInMeters',
               'basis_of_record': 'basisOfRecord',
               'individual_count': 'individualCount'
              }

#vertnet_fields = ['name', 'longitude', 'latitude', 'prov', 'month', 'verbatimcoordinatesystem', 'day', 'occurrenceid',
#                  'identificationqualifier', 'coordinateuncertaintyinmeters', 'year', 'basisofrecord',
#                  'geodeticdatum', 'georeferenceprotocol', 'stateprovince', 'verbatimlocality', 'references',
#                  'license', 'georeferenceverificationstatus', 'eventdate', 'individualcount',
#                  'catalognumber', 'locality', 'locationremarks', 'occurrenceremarks', 'coordinateprecision'
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
                  'accuracy': 'coordinateuncertaintyinmeters',
                  'basis_of_record': 'basisofrecord',
                  'individual_count': 'individualcount'
                 }


class ImportPointsTool:
    """Import point data into the InputDataset and InputPoint tables of the EBAR geodatabase"""
    def __init__(self):
        pass

    def checkAddPoint(self, id_dict, geodatabase, input_dataset_id, species_id, file_line, field_dict):
        """If point already exists, return id and true; otherwise, add and return id and false"""
        # check for existing point with same unique_id within the dataset source
        if str(file_line[field_dict['unique_id']]) in id_dict:
            return id_dict[str(file_line[field_dict['unique_id']])], True

        # add new
        # Geometry/Shape
        input_point = arcpy.Point(float(file_line[field_dict['longitude']]), float(file_line[field_dict['latitude']]))
        input_geometry = arcpy.PointGeometry(input_point, 
                                             arcpy.SpatialReference(EBARUtils.srs_dict[file_line[field_dict['srs']]]))
        output_geometry = input_geometry.projectAs(
            arcpy.SpatialReference(EBARUtils.srs_dict['North America Albers Equal Area Conic']))
        output_point = output_geometry.lastPoint

        # MaxDate
        max_date = None
        if file_line[field_dict['year']] != 'NA':
            max_year = int(file_line[field_dict['year']])
            max_month = 1
            if file_line[field_dict['month']] != 'NA':
                max_month = int(file_line[field_dict['month']])
            max_day = 1
            if file_line[field_dict['day']] != 'NA':
                max_day = int(file_line[field_dict['day']])
            max_date = datetime.datetime(max_year, max_month, max_day)

        # Accuracy
        accuracy = None
        if file_line[field_dict['accuracy']] != 'NA':
            accuracy = round(float(file_line[field_dict['accuracy']]))

        # CurrentHistorical
        current_historical = 'C'
        if file_line[field_dict['basis_of_record']] == 'FOSSIL_SPECIMEN':
            current_historical = 'H'
        else:
            if max_date:
                if datetime.datetime.now().year - int(file_line[field_dict['year']]) > 40:
                    current_historical = 'H'
            else:
                current_historical = 'U'

        # IndividualCount
        individual_count = None
        if file_line[field_dict['individual_count']] != 'NA':
            individual_count = int(file_line[field_dict['individual_count']])

        # insert, set new id and return
        point_fields = ['SHAPE@XY', 'InputDatasetID', 'DatasetSourceUniqueID', 'URI', 'License', 'SpeciesID',
                        'MinDate', 'MaxDate', 'Accuracy', 'CurrentHistorical', 'IndividualCount']
        with arcpy.da.InsertCursor(geodatabase + '/InputPoint', point_fields) as cursor:
            input_point_id = cursor.insertRow([output_point, input_dataset_id, str(file_line[field_dict['unique_id']]),
                                               file_line[field_dict['uri']], file_line[field_dict['license']],
                                               species_id, None, max_date, accuracy, current_historical,
                                               individual_count])
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
            param_raw_data_file = 'C:/Users/rgree/OneDrive/EBAR/Data Mining/Online_Platforms/GBIF_Yukon.csv'
            param_dataset_name = 'GBIF for YK'
            param_dataset_organization = 'Global Biodiversity Information Facility'
            param_dataset_contact = 'https://www.gbif.org'
            param_dataset_source = 'GBIF'
            #param_raw_data_file = 'C:/Users/rgree/OneDrive/Data_Mining/Import_Routine_Data/vertnet.csv'
            #param_dataset_name = 'VerNet Marmot'
            #param_dataset_organization = 'National Science Foundation'
            #param_dataset_contact = 'http://vertnet.org/'
            #param_dataset_source = 'VertNet'
            param_dataset_type = 'CSV'
            param_date_received = 'October 2, 2019'
            param_restrictions = ''

        # check parameters
        field_dict = gbif_fields
        if param_dataset_source == 'VertNet':
            field_dict = vertnet_fields

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
        infile = io.open(param_raw_data_file, 'r', encoding='mbcs')
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
            input_point_id, point_exists = self.checkAddPoint(id_dict, param_geodatabase, input_dataset_id,
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
