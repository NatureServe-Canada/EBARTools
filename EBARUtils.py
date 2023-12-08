# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: EBARUtils.py
# Code shared by ArcGIS Python tools in the EBAR Tools Python Toolbox


import collections
import arcpy
import math
import datetime
import os
import pathlib
import shutil
import time
import zipfile
import csv
import requests
import json

#from xarray import where


# shared folders and addresses
resources_folder = 'C:/GIS/EBAR/EBARTools/resources'
temp_folder = 'C:/GIS/EBAR/temp'
download_folder = 'C:/GIS/EBAR/pub/download'
#download_folder = 'F:/download'
download_url = 'https://gis.natureserve.ca/download'
#nsx_species_search_url = 'https://explorer.natureserve.org/api/data/search'
nsx_taxon_search_url = 'https://explorer.natureserve.org/api/data/taxon/'
#log_folder = 'C:/inetpub/logs/LogFiles/W3SVC1'
log_folder = 'C:/GIS/EBAR/temp'


# various services
ebar_feature_service = 'https://gis.natureserve.ca/arcgis/rest/services/EBAR-KBA/EBAR/FeatureServer'
ebar_summary_service = 'https://gis.natureserve.ca/arcgis/rest/services/EBAR-KBA/Summary/FeatureServer'
#restricted_service = 'https://gis.natureserve.ca/arcgis/rest/services/EBAR-KBA/Restricted/FeatureServer'


# lowest accuracy data added to database (metres, based on diagonal of 0.2 degrees square at equator)
worst_accuracy = 32000


# buffer size in metres #, used if Accuracy not provided
default_buffer_size = 10


## proportion of point buffer that must be within ecoshape to get Present; otherwise gets Presence Expected
#buffer_proportion_overlap = 0.6


# number of years beyond which Presence gets set to Historical
age_for_historical = 40


# WKIDs for datums/SRSs
srs_dict = {'North America Albers Equal Area Conic': 102008,
            'WGS84': 4326,
            'WGS 1984': 4326,
            'World Geodetic System 1984': 4326,
            'World Geodetic System 1972': 4322,
            'WGS72': 4322,
            'NAD83': 4269,
            'NAD 1983': 4269,
            'North American Datum 1983': 4269,
            'NAD27': 4267,
            'NAD 1927': 4267,
            'North American Datum 1927': 4267,
            'Australian Geodetic Datum 1984': 4203,
            'Ain el Abd 1970': 4204,
            'Amersfoort': 4289,
            'Ocotepeque 1935': 5451}


# element observation rank values
eo_rank_dict = {'Excellent estimated viability/ecological integrity': 'A',
                'Excellent estimated viability': 'A',
                'Possibly excellent estimated viability/ecological integrity': 'A?',
                'Possibly excellent estimated viability': 'A?',
                'Excellent or good estimated viability/ecological integrity': 'AB',
                'Excellent or good estimated viability': 'AB',
                'Excellent, good, or fair estimated viability/ecological integrity': 'AC',
                'Excellent, good, or fair estimated viability': 'AC',
                'Good estimated viability/ecological integrity': 'B',
                'Good estimated viability': 'B',
                'Possibly good estimated viability/ecological integrity': 'B?',
                'Possibly good estimated viability': 'B?',
                'Good or fair estimated viability/ecological integrity': 'BC',
                'Good or fair estimated viability': 'BC',
                'Good, fair, or poor estimated viability/ecological integrity': 'BD',
                'Good, fair, or poor estimated viability': 'BD',
                'Fair estimated viability/ecological integrity': 'C',
                'Fair estimated viability': 'C',
                'Possibly fair estimated viability/ecological integrity': 'C?',
                'Possibly fair estimated viability': 'C?',
                'Fair or poor estimated viability/ecological integrity': 'CD',
                'Fair or poor estimated viability': 'CD',
                'Poor estimated viability/ecological integrity': 'D',
                'Poor estimated viability': 'D',
                'Possibly poor estimated viability/ecological integrity': 'D?',
                'Possibly poor estimated viability': 'D?',
                'Verified extant (viability/ecological integrity not assessed)': 'E',
                'Verified extant (viability not assessed)': 'E',
                'Failed to find': 'F',
                'Possibly failed to find': 'F?',
                'Historical': 'H',
                'Possibly historical': 'H?',
                'Extirpated': 'X',
                'Possibly extirpated': 'X?',
                'Unrankable': 'U',
                'Not ranked': 'NR'}


# range scopes
scope_dict = {'G': 'Global',
              'N': 'Canadian',
              'A': 'North American',
              None: 'None'}


# jurisdiction ids for national (Canadian) range maps
national_jur_ids = '(1,2,3,4,5,6,7,8,9,10,11,12,13)'


# subnation codes for Canada
subnation_dict = {'Alberta': 'AB',
                  'British Columbia': 'BC',
                  'Labrador': 'LB',
                  'Manitoba': 'MB',
                  'New Brunswick': 'NB',
                  'Newfoundland': 'NF',
                  'Nova Scotia': 'NS',
                  'Northwest Territories': 'NT',
                  'Nunavut': 'NU',
                  'Ontario': 'ON',
                  'Prince Edward Island': 'PE',
                  'Quebec': 'QC',
                  'Saskatchewan': 'SK',
                  'Yukon Territory': 'YT'}


# breeding land use classes
breeding_land_use_classes = ['breeding',
                             'maternity colony',
                             'roost',
                             'nesting area',
                             'calving area',
                             'nursery area']


# for emailNoticeWithAttachment below
sender = 'ebar.kba.notices@gmail.com'
receivers = ['rgreene@natureserve.ca', 'sstefanoff@natureserve.ca', 'maggie_woo@natureserve.org']
password_file = 'C:/GIS/EBAR/email/email.txt'
server = 'smtp.gmail.com'
port = 587


def displayMessage(messages, msg):
    """Output message to arcpy message object or to Python standard output."""
    if messages:
        upper_msg = msg.upper()
        if 'WARNING' in upper_msg:
            messages.addWarningMessage(msg)
        elif 'ERROR' in upper_msg or 'EXCEPTION' in upper_msg:
            messages.addErrorMessage(msg)
        else:
            messages.addMessage(msg)
    else:
        print(msg)
    return


class MutableNamedTuple(collections.OrderedDict):
    """Used by enhanced cursor functions below"""

    def __init__(self, *args, **kwargs):
        super(MutableNamedTuple, self).__init__(*args, **kwargs)
        self._initialized = True

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if hasattr(self, '_initialized'):
            if hasattr(self, name):
                super(MutableNamedTuple, self).__setitem__(name, value)
            else:
                raise AttributeError(name)
        else:
            super(MutableNamedTuple, self).__setattr__(name, value)


def searchCursor(cursor):
    """Enables named fields in an arcpy.da.SearchCursor"""
    return _name_cursor(cursor)


def updateCursor(cursor):
    """Enables named fields in an arcpy.da.UpdateCursor"""
    return _name_cursor(cursor)


def insertCursor(cursor):
    """Enables named fields in an arcpy.da.InsertCursor"""
    if isinstance(cursor, arcpy.da.InsertCursor):
        return MutableNamedTuple(zip(cursor.fields, [None for field in cursor.fields]))


def _name_cursor(cursor):
    """Private generator to enable named fields in an arcpy.da cursor (search_cursor or update_cursor)"""
    if (isinstance(cursor, arcpy.da.SearchCursor) or
        isinstance(cursor, arcpy.da.UpdateCursor)):
        for row in cursor:
            yield MutableNamedTuple(zip(cursor.fields, row))


#def setNewID(table, id_field, where_clause):
#    """Set id_field to object_id"""
#    new_id = None
#    with arcpy.da.UpdateCursor(table, ['OID@', id_field], where_clause) as cursor:
#        row = None
#        for row in updateCursor(cursor):
#            # investigate more fool-proof method of assigning ID!!!
#            new_id = row['OID@']
#            cursor.updateRow([new_id, new_id])
#        if row:
#            del row
#    return new_id


def getUniqueID(table, id_field, object_id):
    """Retrieve the Unique ID based on the ObjectID"""
    unique_id = None
    with arcpy.da.SearchCursor(table, [id_field], 'OBJECTID = ' + str(object_id)) as search_cursor:
        row = None
        for row in searchCursor(search_cursor):
            unique_id = row[id_field]
        if row:
            del row
    return unique_id


def checkAddInputDataset(geodatabase, dataset_name, dataset_source_id, date_received):
                         #sensitive_ecoogical_data_cat): # restrictions):
    """If Dataset already exists (name, source, date), return id and true; otherwise, add and return id and false"""
    input_dataset_id = None

    # existing
    with arcpy.da.SearchCursor(geodatabase + '/InputDataset', ['InputDatasetID'],
                               "DatasetName = '" + dataset_name + "' AND DatasetSourceID = " + \
                               str(dataset_source_id) + " AND DateReceived = date '" + date_received + "'") as cursor:
        for row in searchCursor(cursor):
            input_dataset_id = row['InputDatasetID']
        if input_dataset_id:
            del row
            return input_dataset_id, True

    # new
    # dataset_fields = ['DatasetName', 'DatasetSourceID', 'DateReceived', 'Restrictions']
    dataset_fields = ['DatasetName', 'DatasetSourceID', 'DateReceived'] #, 'SensitiveEcologicalDataCat']
    with arcpy.da.InsertCursor(geodatabase + '/InputDataset', dataset_fields) as cursor:
        # object_id = cursor.insertRow([dataset_name, dataset_source_id, date_received, restrictions])
        object_id = cursor.insertRow([dataset_name, dataset_source_id, date_received])
                                      #sensitive_ecoogical_data_cat])
    input_dataset_id = getUniqueID(geodatabase + '/InputDataset', 'InputDatasetID', object_id)
    return input_dataset_id, False


def checkField(table, field_name):
    desc = arcpy.Describe(table)
    for field in desc.fields:
        if field.name == field_name:
            return True
    return False


def checkAddField(table, field_name, field_type):
    if checkField(table, field_name):
        return True
    arcpy.AddField_management(table, field_name, field_type)
    return False


def readSpecies(geodatabase):
    """read existing species names and IDs into dict and return"""
    species_dict = {}
    with arcpy.da.SearchCursor(geodatabase + '/BIOTICS_ELEMENT_NATIONAL',
                               ['NATIONAL_SCIENTIFIC_NAME', 'SpeciesID']) as cursor:
        for row in searchCursor(cursor):
            species_dict[row['NATIONAL_SCIENTIFIC_NAME'].lower()] = row['SpeciesID']
        if len(species_dict) > 0:
            del row
    return species_dict


def readEcosystems(geodatabase):
    """read existing ecosystem names and IDs into dict and return"""
    ecosystems_dict = {}
    with arcpy.da.SearchCursor(geodatabase + '/BIOTICS_ECOSYSTEM',
                               ['IVC_SCIENTIFIC_NAME', 'EcosystemID']) as cursor:
        for row in searchCursor(cursor):
            ecosystems_dict[row['IVC_SCIENTIFIC_NAME'].lower()] = row['EcosystemID']
        if len(ecosystems_dict) > 0:
            del row
    return ecosystems_dict


def readSynonyms(geodatabase):
    """read existing synonyms and IDS into dict and return"""
    synonym_id_dict = {}
    with arcpy.da.SearchCursor(geodatabase + '/Synonym', ['SynonymName', 'SynonymID']) as cursor:
        for row in searchCursor(cursor):
            synonym_id_dict[row['SynonymName'].lower()] = row['SynonymID']
    if len(synonym_id_dict) > 0:
        del row
    return synonym_id_dict


def readSynonymSpecies(geodatabase):
    """read existing synonyms and species IDs into dict return"""
    synonym_species_id_dict = {}
    with arcpy.da.SearchCursor(geodatabase + '/Synonym', ['SynonymName', 'SpeciesID']) as cursor:
        for row in searchCursor(cursor):
            synonym_species_id_dict[row['SynonymName'].lower()] = row['SpeciesID']
    if len(synonym_species_id_dict) > 0:
        del row
    return synonym_species_id_dict


def readElementSpecies(geodatabase):
    """read existing element and species IDs into dict and return"""
    element_species_dict = {}
    with arcpy.da.SearchCursor(geodatabase + '/BIOTICS_ELEMENT_NATIONAL',
                               ['ELEMENT_NATIONAL_ID', 'SpeciesID']) as cursor:
        for row in searchCursor(cursor):
            element_species_dict[row['ELEMENT_NATIONAL_ID']] = row['SpeciesID']
    if len(element_species_dict) > 0:
        del row
    return element_species_dict


def readElementEcosystem(geodatabase):
    """read existing element and ecosystem IDs into dict and return"""
    element_ecosystem_dict = {}
    with arcpy.da.SearchCursor(geodatabase + '/BIOTICS_ECOSYSTEM',
                               ['ELEMENT_GLOBAL_ID', 'EcosystemID']) as cursor:
        for row in searchCursor(cursor):
            element_ecosystem_dict[row['ELEMENT_GLOBAL_ID']] = row['EcosystemID']
    if len(element_ecosystem_dict) > 0:
        del row
    return element_ecosystem_dict


def checkSpecies(scientific_name, geodatabase):
    """if exists return SpeciesID and citation"""
    #species_id = None
    #short_citation = None
    #with arcpy.da.SearchCursor(geodatabase + '/BIOTICS_ELEMENT_NATIONAL', ['SpeciesID', 'SHORT_CITATION_AUTHOR',
    #                                                                       'SHORT_CITATION_YEAR'],
    #                           "LOWER(NATIONAL_SCIENTIFIC_NAME) = '" + scientific_name.lower() + "'",
    #                           None) as cursor:
    #    for row in searchCursor(cursor):
    #        species_id = row['SpeciesID']
    #        if row['SHORT_CITATION_AUTHOR']:
    #            short_citation = ' (' + row['SHORT_CITATION_AUTHOR']
    #            if row['SHORT_CITATION_YEAR']:
    #                short_citation += ', ' + str(int(row['SHORT_CITATION_YEAR']))
    #            short_citation += ')'
    #    if species_id:
    #        # found
    #        del row
    #return species_id, short_citation
    species_id = None
    author_name = ''
    with arcpy.da.SearchCursor(geodatabase + '/BIOTICS_ELEMENT_NATIONAL', ['SpeciesID', 'AUTHOR_NAME'],
                               "LOWER(NATIONAL_SCIENTIFIC_NAME) = '" + scientific_name.lower() + "'",
                               None) as cursor:
        for row in searchCursor(cursor):
            species_id = row['SpeciesID']
            if row['AUTHOR_NAME']:
                author_name = row['AUTHOR_NAME']
        if species_id:
            # found
            del row
    return species_id, author_name


def readDatasetSourceUniqueIDs(geodatabase, table_name_prefix, dataset_source_id, feature_class_type, bad):
    """read existing unique ids for dataset source into dict and return"""
    # different feature class for each type
    if feature_class_type in ('Polygon', 'MultiPatch'):
        feature_class = 'InputPolygon'
    elif feature_class_type in ('Point', 'Multipoint'):
        feature_class = 'InputPoint'
    else: # Polyline
        feature_class = 'InputLine'
    id_field = feature_class + 'ID'
    feature_layer = 'feature_layer'
    # also used to load bad records
    if bad:
        feature_layer += 'bad_' + feature_layer
        feature_class = 'Bad' + feature_class
    arcpy.MakeFeatureLayer_management(geodatabase + '/' + feature_class, feature_layer)
    spatial_id_field = table_name_prefix + feature_class + '.' + id_field
    source_id_field = table_name_prefix + feature_class + '.DatasetSourceUniqueID'
    species_id_field = table_name_prefix + feature_class + '.SpeciesID'
    # join to Dataset and read IDs
    arcpy.AddJoin_management(feature_layer, 'InputDatasetID', geodatabase + '/InputDataset', 'InputDatasetID')
    unique_ids_dict = {}
    with arcpy.da.SearchCursor(feature_layer,
                               [spatial_id_field, source_id_field, species_id_field],
                               'InputDataset.DatasetSourceID = ' + str(dataset_source_id)) as cursor:
        for row in searchCursor(cursor):
            #unique_ids_dict[row[source_id_field] + ' - ' + str(row[species_id_field])] = row[spatial_id_field]
            unique_ids_dict[row[source_id_field]] = row[spatial_id_field]
    if len(unique_ids_dict) > 0:
        del row
    return unique_ids_dict


def extractDate(date_str):
    """attempt to extract a date from the passed string"""
    ret_date = None
    # accept yyyy?mm?dd, yyyy?mm or yyyy
    if date_str not in ('NA', '', 'Unknown', 'unknown', 'No Date', 'ND', 'N.D.', None):
        if len(date_str) >= 4:
            at_least_year = False
            try:
                year = int(date_str[0:4])
                at_least_year = True
                month = 1
                day = 1
                if len(date_str) >= 7:
                    month = int(date_str[5:7])
                    if month > 12 or month == 0:
                        month = 1
                    else:
                        # only process day if month is sensible
                        if len(date_str) >= 10:
                            day = int(date_str[8:10])
                            if day > 31 or day == 0:
                                day = 1
            except:
                # bury any errors
                pass
            finally:
                if at_least_year:
                    try:
                        if year > 0:
                            ret_date = datetime.datetime(year, month, day)
                    except ValueError:
                        # handle rare cases such as month with less than 31 days and day of 31
                        try:
                            ret_date = datetime.datetime(year, month, 1)
                        except ValueError:
                            ret_date = datetime.datetime(year, 1, 1)
    return ret_date


def estimateAccuracy(latitude, degrees):
    """calculate the diagonal in metres of a square sized input_degrees x input_degrees at the provided latitude"""
    # create diagonal line input_degrees x input_degrees
    # start with lat/lon points
    pta_wgs84 = arcpy.PointGeometry(arcpy.Point(-96.0 + (degrees / 2.0),
                                                latitude + (degrees / 2.0)),
                                    arcpy.SpatialReference(srs_dict['WGS84']))
    ptb_wgs84 = arcpy.PointGeometry(arcpy.Point(-96.0 - (degrees / 2.0),
                                                latitude - (degrees / 2.0)),
                                    arcpy.SpatialReference(srs_dict['WGS84']))
    # project to metres
    pta_albers = pta_wgs84.projectAs(arcpy.SpatialReference(srs_dict['North America Albers Equal Area Conic']))
    ptb_albers = ptb_wgs84.projectAs(arcpy.SpatialReference(srs_dict['North America Albers Equal Area Conic']))
    # form line
    line_albers = arcpy.Polyline(arcpy.Array([pta_albers.lastPoint, ptb_albers.lastPoint]),
                                 arcpy.SpatialReference(srs_dict['North America Albers Equal Area Conic']))
    return int(line_albers.length)


def createFieldMap(input_table, input_field, output_field, data_type):
    """create one-to-one field map for use with the Append tool"""
    field_map = arcpy.FieldMap()
    field_map.addInputField(input_table, input_field)
    field = field_map.outputField
    field.name = output_field
    field.aliasName = output_field
    field.type = data_type
    field_map.outputField = field
    return field_map


def readDatasetSources(param_geodatabase, dataset_source_type):
    """return a list of dataset source names for the given type"""
    source_list = []
    with arcpy.da.SearchCursor(param_geodatabase + '/DatasetSource', ['DatasetSourceName'],
                                "DatasetSourceType IN " + dataset_source_type,
                                sql_clause=(None, 'ORDER BY DatasetSourceName')) as cursor:
        for row in searchCursor(cursor):
            source_list.append(row['DatasetSourceName'])
        if len(source_list) > 0:
            del row
    return source_list


# def encodeRestriction(geodatabase, restriction):
#     """encode restriction using domain"""
#     domains = arcpy.da.ListDomains(geodatabase)
#     for domain in domains:
#         if domain.name == 'Restriction':
#             for key in domain.codedValues.keys():
#                 if domain.codedValues[key] == restriction:
#                     restriction = key
#     return restriction


def getTableNamePrefix(geodatabase):
    """get table name prefix (needed for joined tables and feature classes in enterprise geodatabases)"""
    table_name_prefix = ''
    desc = arcpy.Describe(geodatabase)
    if desc.workspaceType == 'RemoteDatabase':
        table_name_prefix = desc.connectionProperties.database + '.' + desc.connectionProperties.user + '.'
    return table_name_prefix


def createReplaceFolder(folder):
    """create the passed folder, first removing it if it already exists"""
    if os.path.exists(folder):
        shutil.rmtree(folder)
        # pause before trying to make the dir
        time.sleep(1)
    os.mkdir(folder)
    # attempt to overcome GP service holding a hook into the folder
    del folder


def createZip(zip_folder, zip_output_file, only_include_extension):
    """create zip file, optionally with just files """
    path = pathlib.Path(zip_folder)
    os.chdir(path.parent)
    zip_folder_name = os.path.basename(zip_folder)
    zipf = zipfile.ZipFile(zip_output_file, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(zip_folder):
        for file in files:
            include = True
            # check optional include extension
            if only_include_extension:
                if file[-len(only_include_extension):] != only_include_extension:
                    include = False
            # always exclude lock files
            if file[-5:] == '.lock':
                include = False
            if include:
                zipf.write(zip_folder_name + '/' + file)
    zipf.close()
    # attempt to overcome GP service holding a hook into the folder
    del zip_folder


def addToZip(zip_output_file, new_file):
    """add a file to an existing zip"""
    zipf = zipfile.ZipFile(zip_output_file,'a')
    zipf.write(new_file, os.path.basename(new_file))
    zipf.close()


def ExportRangeMapToCSV(range_map_view, range_map_ids, attributes_dict, output_folder, output_csv, metadata):
    """create csv for range map, with appropriate joined data"""
    where_clause = 'RangeMapID IN (' + ','.join(range_map_ids) + ')'
    arcpy.MakeTableView_management(ebar_feature_service + '/11', range_map_view, where_clause)
    arcpy.AddJoin_management(range_map_view, 'SpeciesID', ebar_feature_service + '/4', 'SpeciesID', 'KEEP_COMMON')
    arcpy.AddJoin_management(range_map_view, 'SpeciesID', ebar_feature_service + '/19', 'SpeciesID', 'KEEP_COMMON')
    field_mappings = arcpy.FieldMappings()
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L11RangeMap.RangeMapID', 'RangeMapID', 'LONG'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L11RangeMap.RangeVersion', 'RangeVersion', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L11RangeMap.RangeStage', 'RangeStage', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L11RangeMap.RangeDate', 'RangeDate', 'DATE'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L11RangeMap.RangeMapScope', 'RangeMapScope', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L11RangeMap.RangeMetadata', 'RangeMetadata', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L11RangeMap.RangeMapNotes', 'RangeMapNotes', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L11RangeMap.RangeMapComments', 'RangeMapComments',
                                              'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L11RangeMap.ReviewerComments', 'ReviewerComments',
                                              'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L11RangeMap.SynonymsUsed', 'SynonymsUsed', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L11RangeMap.DifferentiateUsageType',
                                              'DifferentiateUsageType', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L4BIOTICS_ELEMENT_NATIONAL.ELEMENT_NATIONAL_ID',
                                              'ELEMENT_NATIONAL_ID', 'LONG'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L4BIOTICS_ELEMENT_NATIONAL.ELEMENT_GLOBAL_ID',
                                              'ELEMENT_GLOBAL_ID', 'LONG'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L4BIOTICS_ELEMENT_NATIONAL.ELEMENT_CODE',
                                              'ELEMENT_CODE', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L4BIOTICS_ELEMENT_NATIONAL.CATEGORY',
                                              'CATEGORY', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L4BIOTICS_ELEMENT_NATIONAL.TAX_GROUP',
                                              'TAX_GROUP', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L4BIOTICS_ELEMENT_NATIONAL.FAMILY_COM',
                                              'FAMILY_COM', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L4BIOTICS_ELEMENT_NATIONAL.GENUS',
                                              'GENUS', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L4BIOTICS_ELEMENT_NATIONAL.PHYLUM',
                                              'PHYLUM', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L4BIOTICS_ELEMENT_NATIONAL.CA_NNAME_LEVEL',
                                              'CA_NNAME_LEVEL', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_SCIENTIFIC_NAME',
                                              'NATIONAL_SCIENTIFIC_NAME', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_ENGL_NAME',
                                              'NATIONAL_ENGL_NAME', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_FR_NAME',
                                              'NATIONAL_FR_NAME', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L4BIOTICS_ELEMENT_NATIONAL.COSEWIC_NAME',
                                              'COSEWIC_NAME', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_view, 'L19Species.ENDEMISM', 'ENDEMISM_TYPE', 'TEXT'))
    arcpy.TableToTable_conversion(range_map_view, output_folder, 'temp.csv', field_mapping=field_mappings)

    # add taxon attributes
    with open(output_folder + '/temp.csv','r') as csv_input:
        with open(output_folder + '/' + output_csv, 'w') as csv_output:
            writer = csv.writer(csv_output, lineterminator='\n')
            reader = csv.reader(csv_input)
            all = []
            row = next(reader)
            row[0] = 'objectid'
            row.append('GRANK')
            row.append('NRANK_CA')
            row.append('SRANKS_CA')
            row.append('NRANK_US')
            row.append('SRANKS_US')
            row.append('NRANK_MX')
            row.append('SRANKS_MX')
            row.append('SARA_STATUS')
            row.append('COSEWIC_STATUS')
            row.append('ESA_STATUS')
            all.append(row)
            for row in reader:
                # row[1] is the RangeMapID
                row[0] = row[1]
                row.append(attributes_dict[row[1]]['g_rank'])
                row.append(attributes_dict[row[1]]['ca_rank'])
                row.append(attributes_dict[row[1]]['ca_subnational_ranks'])
                row.append(attributes_dict[row[1]]['us_rank'])
                row.append(attributes_dict[row[1]]['us_subnational_ranks'])
                row.append(attributes_dict[row[1]]['mx_rank'])
                row.append(attributes_dict[row[1]]['mx_subnational_ranks'])
                row.append(attributes_dict[row[1]]['sara_status'])
                row.append(attributes_dict[row[1]]['cosewic_status'])
                row.append(attributes_dict[row[1]]['esa_status'])
                all.append(row)
            writer.writerows(all)
    arcpy.Delete_management(output_folder + '/temp.csv')
    range_map_md = arcpy.metadata.Metadata(output_folder + '/' + output_csv)
    metadata.title = 'EBAR RangeMap.csv'
    metadata.summary = 'Table of species and range attributes for EBAR for selected species'
    range_map_md.copy(metadata)
    range_map_md.save()


def ExportRangeMapEcoshapesToCSV(range_map_ecoshape_view, range_map_ids, output_folder, output_csv, metadata):
    """create csv for range map ecoshape"""
    where_clause = None
    if range_map_ids:
        where_clause = 'RangeMapID IN (' + ','.join(range_map_ids) + ')'
    arcpy.MakeTableView_management(ebar_feature_service + '/12', range_map_ecoshape_view, where_clause)
    field_mappings = arcpy.FieldMappings()
    field_mappings.addFieldMap(createFieldMap(range_map_ecoshape_view, 'RangeMapID', 'RangeMapID', 'LONG'))
    field_mappings.addFieldMap(createFieldMap(range_map_ecoshape_view, 'EcoshapeID', 'EcoshapeID', 'LONG'))
    field_mappings.addFieldMap(createFieldMap(range_map_ecoshape_view, 'Presence', 'Presence', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_ecoshape_view, 'UsageType', 'UsageType', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(range_map_ecoshape_view, 'RangeMapEcoshapeNotes',
                                              'RangeMapEcoshapeNotes', 'TEXT'))
    arcpy.TableToTable_conversion(range_map_ecoshape_view, output_folder, 'RangeMapEcoshape.csv',
                                  field_mapping=field_mappings)
    arcpy.Delete_management(output_folder + '/RangeMapEcoshape.csv.xml')
    arcpy.Delete_management(output_folder + '/schema.ini')
    arcpy.Delete_management(output_folder + '/info')
    range_map_ecoshape_md = arcpy.metadata.Metadata(output_folder + '/RangeMapEcoshape.csv')
    metadata.title = 'EBAR RangeMapEcoshape.csv'
    metadata.summary = 'Table of per-ecoshape attributes for EBAR for selected species'
    range_map_ecoshape_md.copy(metadata)
    range_map_ecoshape_md.save()


def ExportEcoshapesToShapefile(ecoshape_layer, range_map_ecoshape_view, output_folder, output_shapefile, metadata,
                               export_all):
    """create shapefile for ecoshapes"""
    arcpy.MakeFeatureLayer_management(ebar_feature_service + '/3', ecoshape_layer)
    prefix = ''
    if not export_all:
        arcpy.AddJoin_management(ecoshape_layer, 'EcoshapeID', range_map_ecoshape_view, 'EcoshapeID')
        prefix = 'L3Ecoshape.'
    field_mappings = arcpy.FieldMappings()
    field_mappings.addFieldMap(createFieldMap(ecoshape_layer, prefix + 'EcoshapeID', 'EcoshapeID', 'LONG'))
    field_mappings.addFieldMap(createFieldMap(ecoshape_layer, prefix + 'JurisdictionID', 'JurisID', 'LONG'))
    field_mappings.addFieldMap(createFieldMap(ecoshape_layer, prefix + 'EcoshapeName', 'EcoName', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(ecoshape_layer, prefix + 'ParentEcoregion', 'ParentEco', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(ecoshape_layer, prefix + 'ParentEcoregionFR', 'ParentEcoF', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(ecoshape_layer, prefix + 'Ecozone', 'Ecozone', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(ecoshape_layer, prefix + 'EcozoneFR', 'EcozoneFR', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(ecoshape_layer, prefix + 'MosaicVersion', 'MosaicVer', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(ecoshape_layer, prefix + 'TerrestrialArea', 'TerrArea', 'DOUBLE'))
    field_mappings.addFieldMap(createFieldMap(ecoshape_layer, prefix + 'TotalArea', 'TotalArea', 'DOUBLE'))
    arcpy.FeatureClassToFeatureClass_conversion(ecoshape_layer, output_folder, output_shapefile,
                                                field_mapping=field_mappings)
    ecoshape_md = arcpy.metadata.Metadata(output_folder + '/' + output_shapefile)
    metadata.title = 'EBAR Ecoshape.shp'
    metadata.summary = 'Polygons shapefile of original ecoshapes for EBAR for selected species'
    ecoshape_md.copy(metadata)
    ecoshape_md.save()


def ExportEcoshapeOverviewsToShapefile(ecoshape_overview_layer, range_map_ecoshape_view, output_folder,
                                       output_shapefile, metadata, export_all):
    """create shapefile for overview ecoshapes"""
    arcpy.MakeFeatureLayer_management(ebar_feature_service + '/22', ecoshape_overview_layer)
    prefix = ''
    if not export_all:
        arcpy.AddJoin_management(ecoshape_overview_layer, 'EcoshapeID', range_map_ecoshape_view, 'EcoshapeID')
        prefix = 'L22EcoshapeOverview.'
    field_mappings = arcpy.FieldMappings()
    field_mappings.addFieldMap(createFieldMap(ecoshape_overview_layer, prefix + 'EcoshapeID',
                                              'EcoshapeID', 'LONG'))
    field_mappings.addFieldMap(createFieldMap(ecoshape_overview_layer, prefix + 'JurisdictionID',
                                              'JurisID', 'LONG'))
    field_mappings.addFieldMap(createFieldMap(ecoshape_overview_layer, prefix + 'EcoshapeName',
                                              'EcoName', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(ecoshape_overview_layer, prefix + 'ParentEcoregion',
                                              'ParentEco', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(ecoshape_overview_layer, prefix + 'ParentEcoregionFR',
                                              'ParentEcoF', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(ecoshape_overview_layer, prefix + 'Ecozone',
                                              'Ecozone', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(ecoshape_overview_layer, prefix + 'EcozoneFR',
                                              'EcozoneFR', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(ecoshape_overview_layer, prefix + 'MosaicVersion',
                                              'MosaicVer', 'TEXT'))
    field_mappings.addFieldMap(createFieldMap(ecoshape_overview_layer, prefix + 'TerrestrialArea',
                                              'TerrArea', 'DOUBLE'))
    field_mappings.addFieldMap(createFieldMap(ecoshape_overview_layer, prefix + 'TotalArea',
                                              'TotalArea', 'DOUBLE'))
    arcpy.FeatureClassToFeatureClass_conversion(ecoshape_overview_layer, output_folder, output_shapefile,
                                                field_mapping=field_mappings)
    ecoshape_overview_md = arcpy.metadata.Metadata(output_folder + '/' + output_shapefile)
    metadata.title = 'EBAR EcoshapeOverview.shp'
    metadata.summary = 'Polygons shapefile of generalized ecoshapes for EBAR for selected species'
    ecoshape_overview_md.copy(metadata)
    ecoshape_overview_md.save()


def getTaxonAttributes(global_unique_id, element_global_id, range_map_id, messages):
    """retrieve latest taxon attribues from NatureServe Explorer if possible, otherwise use EBAR-KBA database"""
    # default return values
    attributes_dict = {}
    attributes_dict['reviewed_grank'] = ''
    attributes_dict['ca_rank'] = 'None'
    attributes_dict['us_rank'] = 'None'
    attributes_dict['mx_rank'] = 'None'
    attributes_dict['ca_subnational_list'] = []
    attributes_dict['us_subnational_list'] = []
    attributes_dict['mx_subnational_list'] = []
    attributes_dict['ca_subnational_ranks'] = 'None'
    attributes_dict['us_subnational_ranks'] = 'None'
    attributes_dict['mx_subnational_ranks'] = 'None'
    attributes_dict['sara_status'] = 'None'
    attributes_dict['cosewic_status'] = 'None'
    attributes_dict['esa_status'] = 'None'

    # get attributes from NSE Species Search API
    #displayMessage(messages, 'Getting attributes from NatureServe Explorer Species Search API')
    #headers = {'Accept': 'application/json', 'Content-Type': 'application/json; charset=UTF-8'}
    #params = {'criteriaType': 'combined',
    #          'textCriteria': [{'paramType': 'textSearch',
    #                            'searchToken': element_code,
    #                            'matchAgainst': 'code',
    #                            'operator': 'equals'}]}
    #payload = json.dumps(params)
    #r = requests.post(nsx_species_search_url, data=payload, headers=headers)
    #content = json.loads(r.content)
    #results = content['results']

    # try NSX
    results = None
    try:
        result = requests.get(nsx_taxon_search_url + global_unique_id)
        results = json.loads(result.content)
    except:
        displayMessage(messages, 'WARNING: could not find ELEMENT_GLOBAL_ID ' + element_global_id + \
            ' or other NSX Taxon API issue for RangeMapID ' + str(range_map_id))
    if results:
        # get from NSX Taxon API
        attributes_dict['g_rank'] = results['grank']
        if results['grankReviewDate']:
            attributes_dict['reviewed_grank'] = ' (reviewed ' + \
                extractDate(results['grankReviewDate']).strftime('%B %d, %Y') + ')'
        for key in results:
            if key == 'elementNationals':
                for en in results[key]:
                    if en['nation']['isoCode'] == 'CA':
                        reviewed = ''
                        if en['nrankReviewYear']:
                            reviewed = ' (reviewed ' + str(en['nrankReviewYear']) + ')'
                        attributes_dict['ca_rank'] = en['nrank'] + reviewed
                        for esn in en['elementSubnationals']:
                            attributes_dict['ca_subnational_list'].append(esn['subnation']['subnationCode'] + \
                                '=' + esn['srank'])
                    if en['nation']['isoCode'] == 'US':
                        reviewed = ''
                        if en['nrankReviewYear']:
                            reviewed = ' (reviewed ' + str(en['nrankReviewYear']) + ')'
                        attributes_dict['us_rank'] = en['nrank'] + reviewed
                        for esn in en['elementSubnationals']:
                            attributes_dict['us_subnational_list'].append(esn['subnation']['subnationCode'] + \
                                '=' + esn['srank'])
                    if en['nation']['isoCode'] == 'MX':
                        reviewed = ''
                        if en['nrankReviewYear']:
                            reviewed = ' (reviewed ' + str(en['nrankReviewYear']) + ')'
                        attributes_dict['mx_rank'] = en['nrank'] + reviewed
                        for esn in en['elementSubnationals']:
                            attributes_dict['mx_subnational_list'].append(esn['subnation']['subnationCode'] + \
                                '=' + esn['srank'])
        if results['speciesGlobal']['saraStatus']:
            attributes_dict['sara_status'] = results['speciesGlobal']['saraStatus']
            if results['speciesGlobal']['saraStatusDate']:
                attributes_dict['sara_status'] += ' (' + \
                    extractDate(results['speciesGlobal']['saraStatusDate']).strftime('%B %d, %Y') + ')'
        if results['speciesGlobal']['cosewic']:
            if results['speciesGlobal']['cosewic']['cosewicDescEn']:
                attributes_dict['cosewic_status'] = results['speciesGlobal']['cosewic']['cosewicDescEn']
                if results['speciesGlobal']['cosewicDate']:
                    attributes_dict['cosewic_status'] += ' (' + \
                        extractDate(results['speciesGlobal']['cosewicDate']).strftime('%B %d, %Y') + ')'
        if results['speciesGlobal']['interpretedUsesa']:
            attributes_dict['esa_status'] = results['speciesGlobal']['interpretedUsesa']
            if results['speciesGlobal']['usesaDate']:
                attributes_dict['esa_status'] += ' (' + \
                    extractDate(results['speciesGlobal']['usesaDate']).strftime('%B %d, %Y') + ')'

    else:
        # get from BIOTICS table
        attributes_dict['us_rank'] = 'Cannot access'
        attributes_dict['mx_rank'] = 'Cannot access'
        attributes_dict['ca_subnational_ranks'] = 'Cannot access'
        attributes_dict['us_subnational_ranks'] = 'Cannot access'
        attributes_dict['mx_subnational_ranks'] = 'Cannot access'
        attributes_dict['esa_status'] = 'Cannot access'
        with arcpy.da.SearchCursor('biotics_view', 
                                   ['G_RANK', 'G_RANK_REVIEW_DATE', 'N_RANK', 'N_RANK_REVIEW_DATE', 
                                   'COSEWIC_STATUS', 'SARA_STATUS']) as cursor:
            for row in searchCursor(cursor):
                attributes_dict['g_rank'] = row['G_RANK']
                if row['G_RANK_REVIEW_DATE']:
                    attributes_dict['reviewed_grank'] = ' (reviewed ' + \
                        row['G_RANK_REVIEW_DATE'].strftime('%B %d, %Y') + ')'
                attributes_dict['ca_rank'] = row['N_RANK']
                if row['N_RANK_REVIEW_DATE']:
                    attributes_dict['ca_rank'] += ' (reviewed ' + \
                        row['N_RANK_REVIEW_DATE'].strftime('%B %d, %Y') + ')'
                if row['COSEWIC_STATUS']:
                    attributes_dict['cosewic_status'] = row['COSEWIC_STATUS']
                if row['SARA_STATUS']:
                    attributes_dict['sara_status'] = row['SARA_STATUS']

    return attributes_dict


def updateArcGISProTemplate(zip_folder, element_global_id, metadata, range_map_id, differentiate_usage_type):
    """update ArcGIS Pro template for passed element_global_id"""
    # copy template and set project and map properties
    shutil.copyfile(resources_folder + '/EBARTemplate.aprx', zip_folder + '/EBAR' + element_global_id + '.aprx')
    aprx = arcpy.mp.ArcGISProject(zip_folder + '/EBAR' + element_global_id + '.aprx')
    aprx.homeFolder = zip_folder
    #aprx.updateConnectionProperties(zip_folder, '.')
    map = aprx.listMaps('EBARTemplate')[0]
    map.name = 'EBAR' + element_global_id
    # set layer metadata and properties, saving each to a layer file
    usage_type_layer = map.listLayers('EBARTemplateUsageType')[0]
    if differentiate_usage_type:
        usage_type_layer_md = usage_type_layer.metadata
        metadata.title = 'EBAR UsageType.shp'
        metadata.summary = 'Polygons shapefile of usage type for generalized ecoshapes for EBAR for selected species'
        usage_type_layer_md.copy(metadata)
        usage_type_layer_md.save()
        usage_type_layer.name = 'EBAR' + element_global_id + 'UsageType'
        usage_type_layer.definitionQuery = '"RangeMapID" = ' + str(range_map_id)
        usage_type_layer.saveACopy(zip_folder + '/EBAR' + element_global_id + 'UsageType.lyrx')
    else:
        map.removeLayer(usage_type_layer)
    ecoshape_overview_layer =  map.listLayers('EBARTemplateEcoshapeOverview')[0]
    ecoshape_overview_layer_md = ecoshape_overview_layer.metadata
    metadata.title = 'EBAR EcoshapeOverview.shp'
    metadata.summary = 'Polygons shapefile of generalized ecoshapes for EBAR for selected species'
    ecoshape_overview_layer_md.copy(metadata)
    ecoshape_overview_layer_md.save()
    ecoshape_overview_layer.name = 'EBAR' + element_global_id + 'EcoshapeOverview'
    ecoshape_overview_layer.definitionQuery = '"RangeMapID" = ' + str(range_map_id)
    ecoshape_overview_layer.saveACopy(zip_folder + '/EBAR' + element_global_id + 'EcoshapeOverview.lyrx')
    ecoshape_layer =  map.listLayers('EBARTemplateEcoshape')[0]
    ecoshape_layer_md = ecoshape_overview_layer.metadata
    metadata.title = 'EBAR Ecoshape.shp'
    metadata.summary = 'Polygons shapefile of original ecoshapes for EBAR for selected species'
    ecoshape_layer_md.copy(metadata)
    ecoshape_layer_md.save()
    ecoshape_layer.name = 'EBAR' + element_global_id + 'Ecoshape'
    ecoshape_layer.definitionQuery = '"RangeMapID" = ' + str(range_map_id)
    ecoshape_layer.saveACopy(zip_folder + '/EBAR' + element_global_id + 'Ecoshape.lyrx')
    range_map_table = map.listTables('EBARTemplateRangeMap')[0]
    range_map_table.name = 'EBAR' + element_global_id + 'RangeMap'
    range_map_table.definitionQuery = '"RangeMapID" = ' + str(range_map_id)
    range_map_ecoshape_table = map.listTables('EBARTemplateRangeMapEcoshape')[0]
    range_map_ecoshape_table.name = 'EBAR' + element_global_id + 'RangeMapEcoshape'
    range_map_ecoshape_table.definitionQuery = '"RangeMapID" = ' + str(range_map_id)
    # save project
    aprx.save()
    # also save map file
    mapx_path = zip_folder + '/EBAR' + element_global_id + '.mapx'
    map.exportToMAPX(mapx_path)
    # kludge to get around embedding of path, which is inconsistent with interactive save to map file
    mapx_file = open(mapx_path)
    mapx_text = mapx_file.read()
    mapx_file.close()
    os.remove(mapx_path)
    conn_string = aprx.homeFolder[2:].replace('\\', '\\\\')
    mapx_text = mapx_text.replace(conn_string, '.')
    mapx_file = open(mapx_path, 'w')
    mapx_file.write(mapx_text)
    mapx_file.close()


def buildJurisdictionList(geodatabase, jurisdictions_list):
    """Build a comma-separated list of Jurisdiction IDs from the list of Jurisdiction Names"""
    jur_name_dict = {}
    with arcpy.da.SearchCursor(geodatabase + '/Jurisdiction',
                                ['JurisdictionID', 'JurisdictionName']) as cursor:
        jur_not_provided = (len(jurisdictions_list) == 0)
        for row in searchCursor(cursor):
            jur_name_dict[row['JurisdictionName']] = row['JurisdictionID']
            if jur_not_provided:
                # if not passed in, set to all jurisdictions
                jurisdictions_list.append(row['JurisdictionName'])
        if len(jur_name_dict) > 0:
            del row
    # convert names to comma-separated list of ids
    jur_ids_comma = '('
    for jur_name in jurisdictions_list:
        if len(jur_ids_comma) > 1:
            jur_ids_comma += ','
        jur_ids_comma += str(jur_name_dict[jur_name])
    jur_ids_comma += ')'
    return jur_ids_comma


def getJurisidictionAbbreviation(geodatabase, jurisdiction_name):
    """Look up and return abbreviation that corresponds to name"""
    abbrev = None
    with arcpy.da.SearchCursor(geodatabase + '/Jurisdiction', ['JurisdictionAbbreviation'],
                               "JurisdictionName = '" + jurisdiction_name + "'") as cursor:
        for row in searchCursor(cursor):
            abbrev = row['JurisdictionAbbreviation']
        if abbrev:
            del row
    return abbrev


def getSpeciesAndScopeForRangeMap(geodatabase, range_map_id):
    """Get primary and seconday species ids for range map"""
    species_id = None
    species_ids = None
    scope = None

    # primary
    with arcpy.da.SearchCursor(geodatabase + '/RangeMap', ['SpeciesID', 'RangeMapScope'],
                               'RangeMapID = ' + str(range_map_id), None) as cursor:
        for row in searchCursor(cursor):
            species_id = row['SpeciesID']
            scope = row['RangeMapScope']
        if species_id:
            # found
            del row

    # primary and secondary in comma-separated list
    if species_id:
        species_ids = str(species_id)
        with arcpy.da.SearchCursor(geodatabase + '/SecondarySpecies', ['SpeciesID'],
                                   'RangeMapID = ' + str(range_map_id), None) as cursor:
            for row in searchCursor(cursor):
                species_ids += ',' + str(row['SpeciesID'])
            if species_ids != str(species_id):
                # found at least one
                del row

    return species_id, species_ids, scope


def inputSelectAndBuffer(geodatabase, input_features, range_map_id, table_name_prefix, species_ids, species_id,
                         start_time):
    """Select relevant input features and (for points and lines) buffer them"""
    # determine input type and make layer
    desc = arcpy.Describe(input_features)
    arcpy.MakeFeatureLayer_management(geodatabase + '/' + input_features, input_features + '_layer')

    # select any from secondary inputs (chicken and egg - RangeMapID must already exist!)
    arcpy.AddJoin_management(input_features + '_layer', input_features + 'ID', geodatabase + '/SecondaryInput',
                             input_features + 'ID')
    arcpy.SelectLayerByAttribute_management(input_features + '_layer', 'NEW_SELECTION',
                                            table_name_prefix + 'SecondaryInput.RangeMapID = ' + str(range_map_id))
    arcpy.RemoveJoin_management(input_features + '_layer', table_name_prefix + 'SecondaryInput')

    # add primary inputs to selection based on type
    arcpy.AddJoin_management(input_features + '_layer', 'InputDatasetID',
                             geodatabase + '/InputDataset', 'InputDatasetID', 'KEEP_COMMON')
    arcpy.AddJoin_management(input_features + '_layer', 'DatasetSourceID',
                             geodatabase + '/DatasetSource', 'DatasetSourceID', 'KEEP_COMMON')
    where_clause = table_name_prefix + input_features + '.SpeciesID IN (' + species_ids + ') AND (' + \
                   table_name_prefix + input_features + '.Accuracy IS NULL OR ' + table_name_prefix + \
                   input_features + '.Accuracy <= ' + str(worst_accuracy) + ') AND ((' + table_name_prefix + \
                   "DatasetSource.DatasetType IN ('Element Occurrences', " + \
                   "'Source Features', 'Species Observations') AND " + table_name_prefix + input_features + \
                   '.MaxDate IS NOT NULL) OR (' + table_name_prefix + 'DatasetSource.DatasetType IN ' + \
                   "('Critical Habitat', 'Range Estimate', 'Habitat Suitabilty')"
    if desc.shapeType == 'Polygon':
        where_clause += ' OR (' + table_name_prefix + 'DatasetSource.DatasetType = ' + \
                        "'Element Occurrences' AND " + table_name_prefix + input_features + \
                        '.EORank IS NOT NULL) OR ' + table_name_prefix + "DatasetSource.DatasetType = 'Range'"
    where_clause += '))'
    arcpy.SelectLayerByAttribute_management(input_features + '_layer', 'ADD_TO_SELECTION', where_clause)
    arcpy.RemoveJoin_management(input_features + '_layer', table_name_prefix + 'DatasetSource')
    arcpy.RemoveJoin_management(input_features + '_layer', table_name_prefix + 'InputDataset')

    # remove excluded points from selection
    arcpy.AddJoin_management(input_features + '_layer', input_features + 'ID', geodatabase + '/InputFeedback',
                             input_features + 'ID')
    #arcpy.SelectLayerByAttribute_management(input_features + '_layer', 'REMOVE_FROM_SELECTION', table_name_prefix +
    #                                        'InputFeedback.ExcludeFromRangeMapID = ' + str(range_map_id) +
    #                                        ' OR ' + table_name_prefix + 'InputFeedback.ExcludeFromAllRangeMaps = 1')
    # line above does not always behave as expected against enterprise gdb, probably due to outer join!
    # build list of excluded records
    excluded_ids = ''
    with arcpy.da.SearchCursor(input_features + '_layer',
                               [table_name_prefix + input_features + '.' + input_features + 'ID',
                                table_name_prefix + 'InputFeedback.ExcludeFromRangeMapID',
                                table_name_prefix + 'InputFeedback.ExcludeFromAllRangeMaps']) as cursor:
        row = None
        for row in searchCursor(cursor):
            exclude = False
            if row[table_name_prefix + 'InputFeedback.ExcludeFromRangeMapID']:
                if row[table_name_prefix + 'InputFeedback.ExcludeFromRangeMapID'] == range_map_id:
                    exclude = True
            if row[table_name_prefix + 'InputFeedback.ExcludeFromAllRangeMaps']:
                if row[table_name_prefix + 'InputFeedback.ExcludeFromAllRangeMaps'] == 1:
                    exclude = True
            if exclude:
                if len(excluded_ids) > 0:
                    excluded_ids += ','
                excluded_ids += str(row[table_name_prefix + input_features + '.' + input_features + 'ID'])
    if row:
        del row
    del cursor
    arcpy.RemoveJoin_management(input_features + '_layer', table_name_prefix + 'InputFeedback')
    if len(excluded_ids) > 0:
        arcpy.SelectLayerByAttribute_management(input_features + '_layer', 'REMOVE_FROM_SELECTION',
                                                table_name_prefix + input_features + '.' + input_features + 'ID IN (' +
                                                excluded_ids + ')')

    # buffer
    if desc.shapeType == 'Point':
        temp_points = 'TempPoints' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        # add and calculate field based on accuracy
        #checkAddField(input_features + '_layer', 'buffer', 'LONG')
        arcpy.CopyFeatures_management(input_features + '_layer', temp_points)
        checkAddField(temp_points, 'buffer', 'LONG')
        code_block = '''
def GetBuffer(accuracy):
    ret = accuracy
    if not ret:
        ret = ''' + str(default_buffer_size) + '''
    elif ret <= 0:
        ret = ''' + str(default_buffer_size) + '''
    return ret'''
        # arcpy.CalculateField_management(input_features + '_layer', 'buffer', 'GetBuffer(!Accuracy!)', 'PYTHON3', code_block)
        arcpy.CalculateField_management(temp_points, 'buffer', 'GetBuffer(!Accuracy!)', 'PYTHON3', code_block)
        buffered_polygons = 'TempPointBuffer' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        # arcpy.Buffer_analysis(input_features + '_layer', buffered_polygons, 'buffer')
        arcpy.Buffer_analysis(temp_points, buffered_polygons, 'buffer')
        if arcpy.Exists(temp_points):
            arcpy.Delete_management(temp_points)
    elif desc.shapeType == 'Polyline':
        buffered_polygons = 'TempLineBuffer' + str(start_time.year) + str(start_time.month) + \
            str(start_time.day) + str(start_time.hour) + str(start_time.minute) + str(start_time.second)
        arcpy.Buffer_analysis(input_features + '_layer', buffered_polygons, default_buffer_size)
    else:
        # no buffering applied to polygons
        buffered_polygons = input_features + '_layer'
    return buffered_polygons


def deleteRows(table_name, view_name, where_clause):
    """delete rows matching where clause"""
    arcpy.MakeTableView_management(table_name, view_name)
    result = arcpy.SelectLayerByAttribute_management(view_name, 'NEW_SELECTION', where_clause)
    select_count = int(result[1])
    if select_count > 0:
        arcpy.DeleteRows_management(view_name)
    return select_count


def checkReview(range_map_view, table_name_prefix):
    """check for reviews completed or in progress"""
    review_found = False
    review_completed = False
    ecoshape_review = False
    # join to review
    arcpy.AddJoin_management(range_map_view, 'RangeMapID', 'Review', 'RangeMapID', 'KEEP_COMMON')
    # check for completed reviews
    with arcpy.da.SearchCursor(range_map_view, [table_name_prefix + 'Review.DateCompleted']) as cursor:
        for row in searchCursor(cursor):
            review_found = True
            if row[table_name_prefix + 'Review.DateCompleted']:
                review_completed = True
                break
        if review_found:
            del row
    # check for reviews in progress
    if review_found:
        arcpy.AddJoin_management(range_map_view, table_name_prefix + 'Review.ReviewID', 'EcoshapeReview', 'ReviewID',
                                 'KEEP_COMMON')
        with arcpy.da.SearchCursor(range_map_view,
                                   [table_name_prefix + 'EcoshapeReview.ReviewID']) as cursor:
            for row in searchCursor(cursor):
                ecoshape_review = True
                break
            if ecoshape_review:
                del row
        arcpy.RemoveJoin_management(range_map_view, table_name_prefix + 'EcoshapeReview')
    arcpy.RemoveJoin_management(range_map_view, table_name_prefix + 'Review')
    # return
    return review_completed, ecoshape_review


def checkPublished(range_map_view):
    """check if view has any published range maps"""
    published = False
    row = None
    with arcpy.da.SearchCursor(range_map_view, ['Publish']) as cursor:
        for row in searchCursor(cursor):
            if row['Publish']:
                if row['Publish'] == 1:
                    published = True
        if row:
            del row
    return published


def checkMarkedForDelete(range_map_view):
    """check if view has a range map marked for deletion"""
    marked = False
    row = None
    with arcpy.da.SearchCursor(range_map_view, ['RangeStage']) as cursor:
        for row in searchCursor(cursor):
            if row['RangeStage']:
                if row['RangeStage'].lower() == 'delete':
                    marked = True
        if row:
            del row
    return marked


def readSubnationalSpeciesFields(geodatabase, subnation_code):
    """retrieve in subnational species field values into dict within dict"""
    subnational_species_dict = {}
    with arcpy.da.SearchCursor(geodatabase + '/BIOTICS_ELEMENT_NATIONAL',
                               ['SpeciesID', subnation_code + '_S_RANK', subnation_code + '_ROUNDED_S_RANK',
                                subnation_code + '_DATASEN', subnation_code + '_DATASEN_CAT']) as cursor:
        row = None
        for row in searchCursor(cursor):
            values_dict = {}
            values_dict['S_RANK'] = row[subnation_code + '_S_RANK']
            values_dict['ROUNDED_S_RANK'] = row[subnation_code + '_ROUNDED_S_RANK']
            values_dict['EST_DATA_SENS'] = row[subnation_code + '_DATASEN']
            values_dict['EST_DATASEN_CAT'] = row[subnation_code + '_DATASEN_CAT']
            values_dict['changed'] = False
            subnational_species_dict[row['SpeciesID']] = values_dict
        if row:
            del row
    return subnational_species_dict


def updateSubnationalSpeciesFields(geodatabase, subnation_code, subnational_species_dict):
    """update subnational species fields based on passed dict within dict"""
    with arcpy.da.UpdateCursor(geodatabase + '/BIOTICS_ELEMENT_NATIONAL',
                               ['SpeciesID', subnation_code + '_S_RANK', subnation_code + '_ROUNDED_S_RANK',
                                subnation_code + '_DATASEN', subnation_code + '_DATASEN_CAT']) as cursor:
        count = 0
        for row in updateCursor(cursor):
            if subnational_species_dict[row['SpeciesID']]['changed']:
                count += 1
                cursor.updateRow([row['SpeciesID'],
                                  subnational_species_dict[row['SpeciesID']]['S_RANK'],
                                  subnational_species_dict[row['SpeciesID']]['ROUNDED_S_RANK'],
                                  subnational_species_dict[row['SpeciesID']]['EST_DATA_SENS'],
                                  subnational_species_dict[row['SpeciesID']]['EST_DATASEN_CAT']])
        if count > 0:
            del row
    return count


def appendUsingCursor(append_from, append_to, field_dict=None, skip_fields_lower=None):
    """imitate arcpy.Append using insert cursor for better performance"""
    if not skip_fields_lower:
        skip_fields_lower = []
    # always exclude fields automatically set by ArcGIS
    skip_fields_lower.append('objectid')
    skip_fields_lower.append('globalid')
    skip_fields_lower.append('globalid_1')
    skip_fields_lower.append('created_user')
    skip_fields_lower.append('created_date')
    skip_fields_lower.append('last_edited_user')
    skip_fields_lower.append('last_edited_date')
    # build list of fields
    from_fields = []
    to_fields = []
    if field_dict:
        # use dict to map source fields to destination fields
        for key in field_dict:
            if not key.lower() in skip_fields_lower:
                if field_dict[key]:
                    from_fields.append(field_dict[key])
                    to_fields.append(key)
    else:
        # same fields in source and destination
        desc = arcpy.Describe(append_from)
        for field in desc.fields:
            if field.name.lower() not in skip_fields_lower:
                if field.name.lower() == 'shape':
                    from_fields.append('SHAPE@')
                else:
                    from_fields.append(field.name)
        to_fields = from_fields
    # insert
    with arcpy.da.SearchCursor(append_from, from_fields) as cursor:
        for row in searchCursor(cursor):
            # build list of values
            values = []
            for field in from_fields:
                values.append(row[field])
            with arcpy.da.InsertCursor(append_to, to_fields) as insert_cursor:
                insert_cursor.insertRow(values)
            del insert_cursor
    del row, cursor


def checkInputRelatedRecords(table, where_clause):
    """check for input related records in Visit, InputFeedback and SecondaryInput tables"""
    arcpy.MakeTableView_management(table, 'check_view', where_clause)
    result = arcpy.GetCount_management('check_view')
    arcpy.Delete_management('check_view')
    if int(result[0]) > 0:
        return True
    return False
    

def checkSFEO(geodatabase, input_table, id_field, id_value):
    """check if the record is an SF or EO"""
    where_clause = 'DatasetSourceID = (SELECT DatasetSourceID FROM InputDataset WHERE InputDatasetID = ' + \
        '(SELECT InputDatasetID FROM ' + input_table + ' WHERE ' + id_field + ' = ' + id_value + '))'
    ret = False
    with arcpy.da.SearchCursor(geodatabase + '/DatasetSource', ['DatasetType'], where_clause) as cursor:
        for row in searchCursor(cursor):
            if row['DatasetType'] in ('Element Occurrences', 'Source Features'):
                ret = True
    del row, cursor
    return ret


# def emailNoticeWithAttachment(subject, folder, filename):
#     import smtplib
#     from email.mime.text import MIMEText
#     from email.mime.multipart import MIMEMultipart

#     # set up message and attachment
#     msg = MIMEMultipart()
#     msg['From'] = sender
#     msg['To'] = ','.join(receivers)
#     msg['Subject'] = subject
#     if filename:
#         attachment = open(folder + filename)
#         message = MIMEText(attachment.read())
#         attachment.close()
#         message.add_header('Content-Disposition', 'attachment', filename=filename)
#         msg.attach(message)

#     # get password from file
#     pfile = open(password_file)
#     password = pfile.read()
#     pfile.close()

#     # send
#     smtp = smtplib.SMTP(server, port)
#     smtp.starttls()
#     smtp.login(sender, password)
#     smtp.sendmail(sender, receivers, msg.as_string())
#     smtp.quit()
