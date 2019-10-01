# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: ImportGBIFTool.py
# ArcGIS Python tool for importing Global Biodiversity Information System (https://www.gbif.org/) data into the
# InputDataset and InputPoint tables of the EBAR geodatabase

# Note: normally called from EBAR Tools.pyt,
# unless doing interactive debugging (see controlling process at the end of this file)


# import Python packages
#import sys
import EBARUtils
import arcpy
import csv
import datetime
#import locale


class ImportGBIFTool:
    """Import GBIF data into the InputDataset and InputPoint tables of the EBAR geodatabase"""
    def __init__(self):
        pass

    def checkAddGBIFPoint(self, gbif_dict, geodatabase, input_dataset_id, species_id, file_line):
        """If GBIF point already exists, return id and true; otherwise, add and return id and false"""
        # check for existing point with same gbif_id, ensuring the dataset is of source GBIF
        if str(file_line['gbifID']) in gbif_dict:
            return gbif_dict[str(file_line['gbifID'])], True
        #ret_val = None
        #point_row = None
        #dataset_row = None
        #with arcpy.da.SearchCursor(geodatabase + '/InputPoint', ['InputPointID', 'InputDatasetID'],
        #                           "DatasetSourceUniqueID = '" + file_line['gbifID'] + "'") as point_cursor:
        #    for point_row in EBARUtils.searchCursor(point_cursor):
        #        with arcpy.da.SearchCursor(geodatabase + '/InputDataset', ['InputDatasetID'],
        #                                   'InputDatasetID = ' + str(point_row['InputDatasetID']) +
        #                                   " AND DatasetSource = 'GBIF'") as dataset_cursor:
        #            for dataset_row in EBARUtils.searchCursor(dataset_cursor):
        #                ret_val = point_row['InputPointID']
        #if point_row:
        #    del point_row
        #if dataset_row:
        #    del dataset_row
        #if ret_val:
        #    return ret_val, True

        # add new
        # Geometry/Shape
        input_point = arcpy.Point(float(file_line['decimalLongitude']), float(file_line['decimalLatitude']))
        input_geometry = arcpy.PointGeometry(input_point, 
                                             arcpy.SpatialReference(EBARUtils.datum_dict[file_line['geodeticDatum']]))
        output_geometry = input_geometry.projectAs(
            arcpy.SpatialReference(EBARUtils.datum_dict['North America Albers Equal Area Conic']))
        output_point = output_geometry.lastPoint
        # MaxDate
        max_date = None
        if file_line['year'] != 'NA':
            max_year = int(file_line['year'])
            max_month = 1
            if file_line['month'] != 'NA':
                max_month = int(file_line['month'])
            max_day = 1
            if file_line['day'] != 'NA':
                max_day = int(file_line['day'])
            max_date = datetime.datetime(max_year, max_month, max_day)
        # Accuracy
        accuracy = None
        if file_line['coordinateUncertaintyInMeters'] != 'NA':
            accuracy = round(float(file_line['coordinateUncertaintyInMeters']))
        # CurrentHistorical
        current_historical = 'C'
        if file_line['basisOfRecord'] == 'FOSSIL_SPECIMEN':
            current_historical = 'H'
        else:
            if max_date:
                if datetime.datetime.now().year - int(file_line['year']) > 40:
                    current_historical = 'H'
            else:
                current_historical = 'U'
        # IndividualCount
        individual_count = None
        if file_line['individualCount'] != 'NA':
            individual_count = int(file_line['individualCount'])
        # insert, set new id and return
        point_fields = ['SHAPE@XY', 'InputDatasetID', 'DatasetSourceUniqueID', 'SpeciesID', 'MinDate', 'MaxDate',
                        'Accuracy', 'CurrentHistorical', 'IndividualCount']
        with arcpy.da.InsertCursor(geodatabase + '/InputPoint', point_fields) as cursor:
            input_point_id = cursor.insertRow([output_point, input_dataset_id, str(file_line['gbifID']), species_id,
                                               None, max_date, accuracy, current_historical, individual_count])
        EBARUtils.setNewID(geodatabase + '/InputPoint', 'InputPointID', input_point_id)
        gbif_dict[str(file_line['gbifID'])] = input_point_id
        return input_point_id, False

    def RunImportGBIFTool(self, parameters, messages):
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
            param_raw_data_file = parameters[0].valueAsText
            param_geodatabase = parameters[1].valueAsText
            param_dataset_organization = parameters[2].valueAsText
            param_dataset_contact = parameters[3].valueAsText
            param_dataset_source = parameters[4].valueAsText
            param_dataset_type = parameters[5].valueAsText
            param_date_received = parameters[6].valueAsText
            param_restrictions = parameters[7].valueAsText
        else:
            # for debugging, hard code parameters
            param_raw_data_file = 'C:/Users/rgree/OneDrive/EBAR/Data Mining/Online_Platforms/GBIF_Yukon.csv'
            param_geodatabase = 'C:/GIS/EBAR/EBAR_outputs.gdb'
            param_dataset_organization = 'Global Biodiversity Information Facility'
            param_dataset_contact = 'https://www.gbif.org'
            param_dataset_source = 'GBIF'
            param_dataset_type = 'CSV'
            param_date_received = 'September 28, 2019'
            param_restrictions = ''

        # check parameters

        # add InputDataset row
        EBARUtils.displayMessage(messages, 'Adding dataset')
        dataset_fields = ['DatasetOrganization', 'DatasetContact', 'DatasetSource', 'DatasetType', 'DateReceived',
                          'Restrictions']
        with arcpy.da.InsertCursor(param_geodatabase + '/InputDataset', dataset_fields) as cursor:
            input_dataset_id = cursor.insertRow([param_dataset_organization, param_dataset_contact,
                                                 param_dataset_source, param_dataset_type, param_date_received,
                                                 param_restrictions])
        EBARUtils.setNewID(param_geodatabase + '/InputDataset', 'InputDatasetID', input_dataset_id)

        # read existing species into dict
        EBARUtils.displayMessage(messages, 'Reading existing species')
        species_dict = {}
        with arcpy.da.SearchCursor(param_geodatabase + '/Species', ['ScientificName', 'SpeciesID']) as cursor:
            for row in EBARUtils.searchCursor(cursor):
                species_dict[row['ScientificName']] = row['SpeciesID']

        # read existing GBIF IDs into dict
        EBARUtils.displayMessage(messages, 'Reading existing GBIF IDs')
        gbif_dict = {}
        point_dataset_join = arcpy.AddJoin_management(param_geodatabase + '/InputPoint', 'InputDatasetID',
                                                      param_geodatabase + '/InputDataset', 'InputDatasetID')
        with arcpy.da.SearchCursor(point_dataset_join,
                                   ['InputPoint.InputPointID', 'InputPoint.DatasetSourceUniqueID'], 
                                   "InputDataset.DatasetSource = 'GBIF'") as cursor:
            for row in EBARUtils.searchCursor(cursor):
                gbif_dict[row['InputPoint.DatasetSourceUniqueID']] = row['InputPoint.InputPointID']

        # try to open data file as a csv
        infile = open(param_raw_data_file, 'r', encoding='ANSI')
        reader = csv.DictReader(infile)
        #fieldnames = ['basisOfRecord', 'individualCount', 'scientificName', 'species', 'decimalLongitude',
        #              'decimalLatitude', 'coordinateUncertaintyInMeters', 'stateProvince', 'year', 'month', 'day',
        #              'issues', 'license', 'geodeticDatum', 'countryCode', 'locality', 'gbifID', 'occurrenceID',
        #              'recordedBy', 'institutionCode', 'informationWithheld', 'occurrenceRemarks', 'dateIdentified',
        #              'references','verbatimLocality','identifiedBy']

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
                                                                   file_line['species'])
            # check/add GBIF point for current line
            input_point_id, point_exists = self.checkAddGBIFPoint(gbif_dict, param_geodatabase, input_dataset_id,
                                                                  species_id, file_line)
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
    igt = ImportGBIFTool()
    # hard code parameters for debugging
    igt.RunImportGBIFTool(None, None)
