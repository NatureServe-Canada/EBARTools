# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: EBAR Tools.pyt
# ArcGIS Python toolbox for importing species datasets and generating EBAR maps

# Notes:
# - following 120 maximum line length "convention"
# - tested with ArcGIS Pro 2.4.2 and ArcMap 10.4.1


# import python packages
import arcpy
import ImportPointsTool
import ImportPolygonsTool
import GenerateRangeMapTool
import datetime
import locale


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = 'EBAR Tools'
        self.alias = ''

        # List of tool classes associated with this toolbox
        self.tools = [ImportPoints, ImportPolygons, GenerateRangeMap]


class ImportPoints(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Import Points'
        self.description = 'Imports point data into the InputDataset and InputPoint tables of the EBAR geodatabase'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Geodatabase
        param_geodatabase = arcpy.Parameter(
            displayName ='Geodatabase',
            name ='geodatabase',
            datatype ='DEWorkspace',
            parameterType ='Required',
            direction ='Input')
        param_geodatabase.filter.list = ['Local Database', 'Remote Database']

        # Raw Data File
        param_raw_data_file = arcpy.Parameter(
            displayName ='Raw Data File',
            name ='raw_data_file',
            datatype ='DEFile',
            parameterType ='Required',
            direction ='Input')
        param_raw_data_file.filter.list = ['txt', 'csv']

        # Dataset Name
        param_dataset_name = arcpy.Parameter(
            displayName ='Dataset Name',
            name ='dataset_name',
            datatype ='GPString',
            parameterType ='Required',
            direction ='Input')
        
        # Dataset Organization
        param_dataset_organization = arcpy.Parameter(
            displayName ='Dataset Organization',
            name ='dataset_organization',
            datatype ='GPString',
            parameterType ='Required',
            direction ='Input')
        
        # Dataset Contact
        param_dataset_contact = arcpy.Parameter(
            displayName ='Dataset Contact',
            name ='dataset_contact',
            datatype ='GPString',
            parameterType ='Required',
            direction ='Input')
        
        # Dataset Source
        param_dataset_source = arcpy.Parameter(
            displayName ='Dataset Source',
            name ='dataset_source',
            datatype ='GPString',
            parameterType ='Required',
            direction ='Input')
        param_dataset_source.filter.list = ['GBIF',
                                            'NCC_GBIF',
                                            'VertNet',
                                            'Ecoengine',
                                            'iNaturalist',
                                            'BISON',
                                            'Canadensys',
                                            'NCCEndemics',
                                            'iDigBio']

        # Dataset Type
        param_dataset_type = arcpy.Parameter(
            displayName ='Dataset Type',
            name ='dataset_type',
            datatype ='GPString',
            parameterType ='Required',
            direction ='Input')
        param_dataset_type.filter.list = ['CSV']

        # Date Received
        param_date_received = arcpy.Parameter(
            displayName ='Date Received',
            name ='date_received',
            datatype ='GPDate',
            parameterType ='Required',
            direction ='Input')
        locale.setlocale(locale.LC_ALL, '')
        param_date_received.value = datetime.datetime.now().strftime('%x')

        # Dataset Restrictions
        param_dataset_restrictions = arcpy.Parameter(
            displayName ='Dataset Restrictions',
            name ='dataset_restrictions',
            datatype ='GPString',
            parameterType ='Optional',
            direction ='Input')
        
        params = [param_geodatabase, param_raw_data_file, param_dataset_name, param_dataset_organization,
                  param_dataset_contact, param_dataset_source, param_dataset_type, param_date_received,
                  param_dataset_restrictions]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is " + \
        "called whenever a parameter has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called " " \
        "after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        ipt = ImportPointsTool.ImportPointsTool()
        ipt.RunImportPointsTool(parameters, messages)
        return


class ImportPolygons(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Import Polygons'
        self.description = 'Imports polygon data into the InputDataset and InputPolygon tables of the EBAR geodatabase'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Geodatabase
        param_geodatabase = arcpy.Parameter(
            displayName ='Geodatabase',
            name ='geodatabase',
            datatype ='DEWorkspace',
            parameterType ='Required',
            direction ='Input')
        param_geodatabase.filter.list = ['Local Database', 'Remote Database']

        # Feature Class to Import
        param_import_feature_class = arcpy.Parameter(
            displayName ='Import Feature Class',
            name ='import_feature_class',
            datatype ='GPFeatureLayer',
            parameterType ='Required',
            direction ='Input')
        param_import_feature_class.filter.list = ['Polygon']

        # Dataset Name
        param_dataset_name = arcpy.Parameter(
            displayName ='Dataset Name',
            name ='dataset_name',
            datatype ='GPString',
            parameterType ='Required',
            direction ='Input')
        
        # Dataset Organization
        param_dataset_organization = arcpy.Parameter(
            displayName ='Dataset Organization',
            name ='dataset_organization',
            datatype ='GPString',
            parameterType ='Required',
            direction ='Input')
        
        # Dataset Contact
        param_dataset_contact = arcpy.Parameter(
            displayName ='Dataset Contact',
            name ='dataset_contact',
            datatype ='GPString',
            parameterType ='Required',
            direction ='Input')
        
        # Dataset Source
        param_dataset_source = arcpy.Parameter(
            displayName ='Dataset Source',
            name ='dataset_source',
            datatype ='GPString',
            parameterType ='Required',
            direction ='Input')
        param_dataset_source.filter.list = ['ECCC Critical Habitat',
                                            'NCC Literature']

        # Dataset Type
        param_dataset_type = arcpy.Parameter(
            displayName ='Dataset Type',
            name ='dataset_type',
            datatype ='GPString',
            parameterType ='Required',
            direction ='Input')
        param_dataset_type.filter.list = ['Critical Habitat',
                                          'Element Occurrence',
                                          'Range Estimate']

        # Date Received
        param_date_received = arcpy.Parameter(
            displayName ='Date Received',
            name ='date_received',
            datatype ='GPDate',
            parameterType ='Required',
            direction ='Input')
        locale.setlocale(locale.LC_ALL, '')
        param_date_received.value = datetime.datetime.now().strftime('%x')

        # Dataset Restrictions
        param_dataset_restrictions = arcpy.Parameter(
            displayName ='Dataset Restrictions',
            name ='dataset_restrictions',
            datatype ='GPString',
            parameterType ='Optional',
            direction ='Input')
        
        params = [param_geodatabase, param_import_feature_class, param_dataset_name, param_dataset_organization,
                  param_dataset_contact, param_dataset_source, param_dataset_type, param_date_received,
                  param_dataset_restrictions]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is " + \
        "called whenever a parameter has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called " " \
        "after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        ipt = ImportPolygonsTool.ImportPolygonsTool()
        ipt.RunImportPolygonsTool(parameters, messages)
        return


class GenerateRangeMap(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Generate Range Map'
        self.description = 'Generate Range Map for a species from available spatial data'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Geodatabase
        param_geodatabase = arcpy.Parameter(
            displayName ='Geodatabase',
            name ='geodatabase',
            datatype ='DEWorkspace',
            parameterType ='Required',
            direction ='Input')
        param_geodatabase.filter.list = ['Local Database', 'Remote Database']

        # Species
        param_species = arcpy.Parameter(
            displayName ='Species Scientific Name',
            name ='species',
            datatype ='GPString',
            parameterType ='Required',
            direction ='Input')

        # Range Version
        param_version = arcpy.Parameter(
            displayName ='Range Version',
            name ='range_version',
            datatype ='GPString',
            parameterType ='Required',
            direction ='Input')
        param_version.value = '1.0'

        # Range Stage
        param_stage = arcpy.Parameter(
            displayName ='Range Stage',
            name ='range_stage',
            datatype ='GPString',
            parameterType ='Required',
            direction ='Input')
        param_stage.filter.list = ['Auto-generated', 'Expert reviewed', 'Published']
        param_stage.value = 'Auto-generated'

        params = [param_geodatabase, param_species, param_version, param_stage]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is " + \
        "called whenever a parameter has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called " " \
        "after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        grm = GenerateRangeMapTool.GenerateRangeMapTool()
        grm.RunGenerateRangeMapTool(parameters, messages)
        return
