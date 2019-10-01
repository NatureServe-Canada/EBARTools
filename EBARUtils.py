import collections
import arcpy


datum_dict = {'North America Albers Equal Area Conic': 102008,
              'WGS84': 4326,
              'World Geodetic System 1984': 4326,
              'NAD27': 4267,
              'North American Datum 1927': 4267}


def displayMessage(messages, msg):
    """Output message to arcpy message object or to Python standard output."""
    if messages:
        if 'WARNING' in msg.upper():
            messages.addWarningMessage(msg)
        elif 'ERROR' in msg.upper() or 'EXCEPTION' in msg.upper():
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


def setNewID(table, id_field, object_id):
    """Set id_field to object_id"""
    with arcpy.da.UpdateCursor(table, [id_field], "OBJECTID = " + str(object_id)) as cursor:
        for row in updateCursor(cursor):
            # investigate more fool-proof method of assigning ID!!!
            cursor.updateRow([object_id])
        del row


def checkAddSpecies(species_dict, geodatabase, scientific_name):
    """If Scientific Name already in Species table, return id and true; otherwise, add and return id and false"""
    ret_val = None

    # existing
    if scientific_name in species_dict:
        return species_dict[scientific_name], True
    #with arcpy.da.SearchCursor(geodatabase + '/Species', ['SpeciesID'],
    #                           "ScientificName = '" + scientific_name + "'") as cursor:
    #    for row in searchCursor(cursor):
    #        ret_val = row['SpeciesID']
    #    if ret_val:
    #        del row
    #        return ret_val

    # new
    with arcpy.da.InsertCursor(geodatabase + '/Species', ['ScientificName']) as cursor:
        species_id = cursor.insertRow([scientific_name])

    # id of new
    setNewID(geodatabase + '/Species', 'SpeciesID', species_id)
    species_dict[scientific_name] = species_id
    return species_id, False
