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


# lowest accuracy data added to database (metres, based on diagonal of 0.2 degrees square at equator)
worst_accuracy = 32000


# WKIDs for datums/SRSs
srs_dict = {'North America Albers Equal Area Conic': 102008,
            'WGS84': 4326,
            'World Geodetic System 1984': 4326,
            'NAD83': 4269,
            'North American Datum 1983': 4269,
            'NAD27': 4267,
            'North American Datum 1927': 4267}


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


def setNewID(table, id_field, where_clause):
    """Set id_field to object_id"""
    with arcpy.da.UpdateCursor(table, ['OID@', id_field], where_clause) as cursor:
        for row in updateCursor(cursor):
            # investigate more fool-proof method of assigning ID!!!
            cursor.updateRow([row['OID@'], row['OID@']])
        del row


def checkAddInputDataset(geodatabase, dataset_name, dataset_organization, dataset_contact, dataset_source_id,
                         date_received, restrictions):
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
    dataset_fields = ['DatasetName', 'DatasetOrganization', 'DatasetContact', 'DatasetSourceID', 'DateReceived',
                      'Restrictions']
    with arcpy.da.InsertCursor(geodatabase + '/InputDataset', dataset_fields) as cursor:
        input_dataset_id = cursor.insertRow([dataset_name, dataset_organization, dataset_contact, dataset_source_id,
                                             date_received, restrictions])
    return input_dataset_id, False


def checkAddField(table, field_name, field_type):
    desc = arcpy.Describe(table)
    for field in desc.fields:
        if field.name == field_name:
            return True
    arcpy.AddField_management(table, field_name, field_type)
    return False


def readSpecies(geodatabase):
    """read existing species into dict and return"""
    species_dict = {}
    arcpy.MakeTableView_management(geodatabase + '/Species', 'species_view')
    arcpy.AddJoin_management('species_view', 'ELEMENT_NATIONAL_ID', geodatabase + '/BIOTICS_ELEMENT_NATIONAL',
                             'ELEMENT_NATIONAL_ID')
    with arcpy.da.SearchCursor('species_view', ['BIOTICS_ELEMENT_NATIONAL.NATIONAL_SCIENTIFIC_NAME',
                                                'Species.SpeciesID']) as cursor:
        for row in searchCursor(cursor):
            species_dict[row['BIOTICS_ELEMENT_NATIONAL.NATIONAL_SCIENTIFIC_NAME']] = row['Species.SpeciesID']
    if len(species_dict) > 0:
        del row
    arcpy.RemoveJoin_management('species_view', 'BIOTICS_ELEMENT_NATIONAL')
    return species_dict


def readSynonymIDs(geodatabase):
    """read existing synonyms and IDS into dict and return"""
    synonym_id_dict = {}
    with arcpy.da.SearchCursor(geodatabase + '/Synonym', ['SynonymName', 'SynonymID']) as cursor:
        for row in searchCursor(cursor):
            synonym_id_dict[row['SynonymName']] = row['SynonymID']
    if len(synonym_id_dict) > 0:
        del row
    return synonym_dict


def readSynonymSpeciesID(geodatabase):
    """read existing synonyms and species IDs into dict return"""
    synonym_species_id_dict = {}
    with arcpy.da.SearchCursor(geodatabase + '/Synonym', ['SynonymName', 'SpeciesID']) as cursor:
        for row in searchCursor(cursor):
            synonym_species_id_dict[row['SynonymName']] = row['SpeciesID']
    if len(synonym_species_id_dict) > 0:
        del row
    return synonym_species_id_dict


#def checkAddSpecies(species_dict, geodatabase, scientific_name):
#    """If Scientific Name already in Species table, return id and true; otherwise, add and return id and false"""
#    ret_val = None

#    # capitalize first letter only
#    cap_name = scientific_name.capitalize()

#    # existing
#    if cap_name in species_dict:
#        return species_dict[cap_name], True

#    # new
#    with arcpy.da.InsertCursor(geodatabase + '/Species', ['ScientificName']) as cursor:
#        species_id = cursor.insertRow([cap_name])

#    # id of new
#    setNewID(geodatabase + '/Species', 'SpeciesID', 'OBJECTID = ' + str(species_id))
#    species_dict[cap_name] = species_id
#    return species_id, False


def checkSpecies(scientific_name, geodatabase):
    """if exists return SpeciesID"""
    species_id = None
    arcpy.MakeTableView_management(geodatabase + '/Species', 'species_view')
    arcpy.AddJoin_management('species_view', 'ELEMENT_NATIONAL_ID', geodatabase + '/BIOTICS_ELEMENT_NATIONAL',
                             'ELEMENT_NATIONAL_ID')
    with arcpy.da.SearchCursor('species_view', ['Species.SpeciesID'],
                               "BIOTICS_ELEMENT_NATIONAL.NATIONAL_SCIENTIFIC_NAME = '" + scientific_name + "'",
                               None) as cursor:
        for row in searchCursor(cursor):
            species_id = row['Species.SpeciesID']
        if species_id:
            # found
            del row
    arcpy.RemoveJoin_management('species_view', 'BIOTICS_ELEMENT_NATIONAL')
    return species_id


def readDatasetSourceUniqueIDs(geodatabase, dataset_source_id, feature_class_type):
    """read existing unique ids for dataset source into dict and return"""
    # different feature class for each type
    if feature_class_type in ('Polygon', 'MultiPatch'):
        feature_class = 'InputPolygon'
    elif feature_class_type in ('Point', 'Multipoint'):
        feature_class = 'InputPoint'
    else: # Polyline
        feature_class = 'InputLine'
    arcpy.MakeFeatureLayer_management(geodatabase + '/' + feature_class, 'feature_layer')
    spatial_id_field = feature_class + '.' + feature_class + 'ID'
    source_id_field = feature_class + '.DatasetSourceUniqueID'
    # join to Dataset and read IDs
    arcpy.AddJoin_management('feature_layer', 'InputDatasetID', geodatabase + '/InputDataset', 'InputDatasetID')
    unique_ids_dict = {}
    with arcpy.da.SearchCursor('feature_layer',
                               [spatial_id_field, source_id_field],
                               'InputDataset.DatasetSourceID = ' + str(dataset_source_id)) as cursor:
        for row in searchCursor(cursor):
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
                    ret_date = datetime.datetime(year, month, day)
    return ret_date


def estimateAccuracy(latitude):
    """calculate the diagonal of a square 0.2 x 0.2 degrees at the provided latitude"""
    # create diagonal line 0.2 degrees x 0.2 degrees
    # start with lat/lon points
    pta_wgs84 = arcpy.PointGeometry(arcpy.Point(-95.9, latitude + 0.1), arcpy.SpatialReference(srs_dict['WGS84']))
    ptb_wgs84 = arcpy.PointGeometry(arcpy.Point(-96.1, latitude - 0.1), arcpy.SpatialReference(srs_dict['WGS84']))
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
                                "DatasetSourceType = '" + dataset_source_type + "'",
                                sql_clause=(None,'ORDER BY DatasetSourceName')) as cursor:
        for row in searchCursor(cursor):
            source_list.append(row['DatasetSourceName'])
        if len(source_list) > 0:
            del row
    return source_list
