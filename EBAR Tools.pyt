# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen, Meg Southee
# © NatureServe Canada 2020 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: EBAR Tools.pyt
# ArcGIS Python toolbox for importing species datasets and generating EBAR maps

# Notes:
# - following 120 maximum line length "convention"
# - tested with ArcGIS Pro 2.4.2 and ArcMap 10.4.1


# import python packages
import arcpy
import ImportTabularDataTool
import ImportSpatialDataTool
import GenerateRangeMapTool
import ListElementNationalIDsTool
import SyncSpeciesListBioticsTool
import AddSynonymsTool
import ImportExternalRangeReviewTool
import SyncSpeciesListKBATool
import BuildEBARDownloadTableTool
import BuildBulkDownloadTableTool
import ExportInputDataTool
import EBARUtils
import datetime
import locale


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = 'EBAR Tools'
        self.alias = ''

        # List of tool classes associated with this toolbox
        self.tools = [ImportTabularData, ImportSpatialData, GenerateRangeMap, ListElementNationalIDs,
                      SyncSpeciesListBiotics, AddSynonyms, ImportExternalRangeReview, SyncSpeciesListKBA,
                      BuildEBARDownloadTable, BuildBulkDownloadTable, ExportInputData]


class ImportTabularData(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Import Tabular Data'
        self.description = 'Imports tabular data into the InputDataset and InputPoint tables of the EBAR geodatabase'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Geodatabase
        param_geodatabase = arcpy.Parameter(
            displayName='Geodatabase',
            name='geodatabase',
            datatype='DEWorkspace',
            parameterType='Required',
            direction='Input')
        param_geodatabase.filter.list = ['Local Database', 'Remote Database']

        # Raw Data File
        param_raw_data_file = arcpy.Parameter(
            displayName='Raw Data File',
            name='raw_data_file',
            datatype='DEFile',
            parameterType='Required',
            direction='Input')
        param_raw_data_file.filter.list = ['txt', 'csv']

        # Dataset Name
        param_dataset_name = arcpy.Parameter(
            displayName='Dataset Name',
            name='dataset_name',
            datatype='GPString',
            parameterType='Required',
            direction='Input')
        
        # Dataset Source
        param_dataset_source = arcpy.Parameter(
            displayName='Dataset Source',
            name='dataset_source',
            datatype='GPString',
            parameterType='Required',
            direction='Input')

        # Date Received
        param_date_received = arcpy.Parameter(
            displayName='Date Received',
            name='date_received',
            datatype='GPDate',
            parameterType='Required',
            direction='Input')
        locale.setlocale(locale.LC_ALL, '')
        param_date_received.value = datetime.datetime.now().strftime('%x')

        # Dataset Restrictions
        param_dataset_restrictions = arcpy.Parameter(
            displayName='Dataset Restrictions',
            name='dataset_restrictions',
            datatype='GPString',
            parameterType='Required',
            direction='Input')
        param_dataset_restrictions.value = 'Non-restricted'
        
        params = [param_geodatabase, param_raw_data_file, param_dataset_name, param_dataset_source,
                  param_date_received, param_dataset_restrictions]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is 
        called whenever a parameter has been changed."""
        ## Dataset Source needs to be a textbox, not a filtered picklist,
        ## because filtered picklists cannot be dynamic when published to a geoprocessing service
        #if parameters[0].altered and parameters[0].value:
        #    parameters[3].filter.list = EBARUtils.readDatasetSources(parameters[0].valueAsText, "('T')")
        domains = arcpy.da.ListDomains(parameters[0].valueAsText)
        restrictions_list = []
        for domain in domains:
            if domain.name == 'Restriction':
                restrictions_list = list(domain.codedValues.values())
        parameters[5].filter.list = sorted(restrictions_list)
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called "
        "after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        itd = ImportTabularDataTool.ImportTabularDataTool()
        itd.runImportTabularDataTool(parameters, messages)
        return


class ImportSpatialData(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Import Spatial Data'
        self.description = 'Imports spatial data from a shapefile or feature class into the InputDataset table of ' + \
            'the EBAR geodatabase and one of the InputPolygon, InputPoint or InputLine feature classes'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Geodatabase
        param_geodatabase = arcpy.Parameter(
            displayName='Geodatabase',
            name='geodatabase',
            datatype='DEWorkspace',
            parameterType='Required',
            direction='Input')
        param_geodatabase.filter.list = ['Local Database', 'Remote Database']

        # Feature Class to Import
        param_import_feature_class = arcpy.Parameter(
            displayName='Import Feature Class',
            name='import_feature_class',
            datatype='GPFeatureLayer',
            parameterType='Required',
            direction='Input')
        param_import_feature_class.filter.list = ['Point', 'Multipoint', 'Polyline', 'Polygon', 'MultiPatch']

        # Dataset Name
        param_dataset_name = arcpy.Parameter(
            displayName='Dataset Name',
            name='dataset_name',
            datatype='GPString',
            parameterType='Required',
            direction='Input')
        
        # Dataset Source
        # - used to check for uniqueness of records using provided IDs
        # - one field map can be shared among multiple sources
        param_dataset_source = arcpy.Parameter(
            displayName='Dataset Source',
            name='dataset_source',
            datatype='GPString',
            parameterType='Required',
            direction='Input')

        # Date Received
        param_date_received = arcpy.Parameter(
            displayName='Date Received',
            name='date_received',
            datatype='GPDate',
            parameterType='Required',
            direction='Input')
        locale.setlocale(locale.LC_ALL, '')
        param_date_received.value = datetime.datetime.now().strftime('%x')

        # Dataset Restrictions
        param_dataset_restrictions = arcpy.Parameter(
            displayName='Dataset Restrictions',
            name='dataset_restrictions',
            datatype='GPString',
            parameterType='Required',
            direction='Input')
        param_dataset_restrictions.value = 'Non-restricted'
        
        params = [param_geodatabase, param_import_feature_class, param_dataset_name, param_dataset_source,
                  param_date_received, param_dataset_restrictions]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is 
        called whenever a parameter has been changed."""
        ## Dataset Source needs to be a textbox, not a filtered picklist,
        ## because filtered picklists cannot be dynamic when published to a geoprocessing service
        #if parameters[0].altered and parameters[0].value:
        #    parameters[3].filter.list = EBARUtils.readDatasetSources(parameters[0].valueAsText, "('S', 'L', 'P')")
        domains = arcpy.da.ListDomains(parameters[0].valueAsText)
        restrictions_list = []
        for domain in domains:
            if domain.name == 'Restriction':
                restrictions_list = list(domain.codedValues.values())
        parameters[5].filter.list = sorted(restrictions_list)
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called 
        after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        isd = ImportSpatialDataTool.ImportSpatialDataTool()
        isd.runImportSpatialDataTool(parameters, messages)
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
            displayName='Geodatabase',
            name='geodatabase',
            datatype='DEWorkspace',
            parameterType='Required',
            direction='Input')
        param_geodatabase.filter.list = ['Local Database', 'Remote Database']

        # Species
        param_species = arcpy.Parameter(
            displayName='Species Scientific Name',
            name='species',
            datatype='GPString',
            parameterType='Required',
            direction='Input')

        # Secondary Species
        param_secondary = arcpy.Parameter(
            displayName='Secondary Species',
            name='secondary_species',
            datatype='GPString',
            parameterType='Optional',
            direction='Input',
            multiValue=True)

        # Range Version
        param_version = arcpy.Parameter(
            displayName='Range Version',
            name='range_version',
            datatype='GPString',
            parameterType='Required',
            direction='Input')
        param_version.value = '1.0'

        # Range Stage
        param_stage = arcpy.Parameter(
            displayName='Range Stage',
            name='range_stage',
            datatype='GPString',
            parameterType='Required',
            direction='Input')
        # cannot pre-specify the list if you want to allow a value not in the list
        #param_stage.filter.list = ['Auto-generated', 'Expert reviewed', 'Published']
        param_stage.value = 'Auto-generated'

        # Scope
        param_scope = arcpy.Parameter(
            displayName='Scope',
            name='scope',
            datatype='GPString',
            parameterType='Optional',
            direction='Input')
        param_scope.filter.list = ['Canadian', 'Global', 'North American']

        params = [param_geodatabase, param_species, param_secondary, param_version, param_stage, param_scope]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is 
        called whenever a parameter has been changed."""
        # filter list of species
        # make sure there is a geodatabase specified
        ## species need to be textboxes, not filtered picklists,
        ## because filtered picklists cannot be dynamic when published to a geoprocessing service
        #if parameters[0].altered and parameters[0].value:
        #    param_geodatabase = parameters[0].valueAsText
        #    spec_list = []
        #    with arcpy.da.SearchCursor(param_geodatabase + '/BIOTICS_ELEMENT_NATIONAL', ['NATIONAL_SCIENTIFIC_NAME'],
        #                               sql_clause=(None,'ORDER BY NATIONAL_SCIENTIFIC_NAME')) as cursor:
        #        for row in EBARUtils.searchCursor(cursor):
        #            spec_list.append(row['NATIONAL_SCIENTIFIC_NAME'])
        #        if len(spec_list) > 0:
        #            del row
        #    parameters[1].filter.list = spec_list
        #    parameters[2].filter.list = spec_list
        # allow a stage value in addition to the ones in the standard list
        ## only works for optional field when published to geoprocessing service
        ##if parameters[4].altered:
        #stage_list = ['Auto-generated', 'Expert reviewed', 'Published']
        #if parameters[4].value:
        #    if parameters[4].valueAsText not in stage_list:
        #        stage_list.append(parameters[4].valueAsText)
        #parameters[4].filter.list = stage_list
        return


    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called 
        after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        grm = GenerateRangeMapTool.GenerateRangeMapTool()
        grm.runGenerateRangeMapTool(parameters, messages)
        return


class ListElementNationalIDs(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'List Element National IDs'
        self.description = 'Generate a comma-separated list of ELEMENT_NATIONAL_ID values from existing ' + \
                           'BIOTICS_ELEMENT_NATIONAL table'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Geodatabase
        param_geodatabase = arcpy.Parameter(
            displayName='Geodatabase',
            name='geodatabase',
            datatype='DEWorkspace',
            parameterType='Required',
            direction='Input')
        param_geodatabase.filter.list = ['Local Database', 'Remote Database']

        ## Output folder
        #param_folder = arcpy.Parameter(
        #    displayName='Output Folder',
        #    name='output_folder',
        #    datatype='DEFolder',
        #    parameterType='Required',
        #    direction='Input')

        params = [param_geodatabase]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is 
        called whenever a parameter has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called 
        after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        leni = ListElementNationalIDsTool.ListElementNationalIDsTool()
        leni.runListElementNationalIDsTool(parameters, messages)
        return


class SyncSpeciesListBiotics(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Sync Species List Biotics'
        self.description = 'Synchronize the BIOTICS_NATIONAL_ELEMENT and Species tables with Biotics'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Geodatabase
        param_geodatabase = arcpy.Parameter(
            displayName='Geodatabase',
            name='geodatabase',
            datatype='DEWorkspace',
            parameterType='Required',
            direction='Input')
        param_geodatabase.filter.list = ['Local Database', 'Remote Database']

        # CSV
        param_csv = arcpy.Parameter(
            displayName='CSV File',
            name='csv_file',
            datatype='DEFile',
            parameterType='Required',
            direction='Input')
        param_csv.filter.list = ['txt', 'csv']

        params = [param_geodatabase, param_csv]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is
        called whenever a parameter has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called
        after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        ssl = SyncSpeciesListBioticsTool.SyncSpeciesListBioticsTool()
        ssl.runSyncSpeciesListBioticsTool(parameters, messages)
        return


class AddSynonyms(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Add Synonyms'
        self.description = 'Add BIOTICS Synonyms not already in the Species or Synonym tables'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Geodatabase
        param_geodatabase = arcpy.Parameter(
            displayName='Geodatabase',
            name='geodatabase',
            datatype='DEWorkspace',
            parameterType='Required',
            direction='Input')
        param_geodatabase.filter.list = ['Local Database', 'Remote Database']

        # CSV
        param_csv = arcpy.Parameter(
            displayName='CSV File',
            name='csv_file',
            datatype='DEFile',
            parameterType='Required',
            direction='Input')
        param_csv.filter.list = ['txt', 'csv']

        params = [param_geodatabase, param_csv]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is 
        called whenever a parameter has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called 
        after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        ast = AddSynonymsTool.AddSynonymsTool()
        ast.runAddSynonymsTool(parameters, messages)
        return


class ImportExternalRangeReview(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Import External Range Review'
        self.description = 'Create review records for an existing range map based on third-party polygons'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Geodatabase
        param_geodatabase = arcpy.Parameter(
            displayName='Geodatabase',
            name='geodatabase',
            datatype='DEWorkspace',
            parameterType='Required',
            direction='Input')
        param_geodatabase.filter.list = ['Local Database', 'Remote Database']

        # Species
        param_species = arcpy.Parameter(
            displayName='Species Scientific Name',
            name='species',
            datatype='GPString',
            parameterType='Required',
            direction='Input')

        # Secondary Species
        param_secondary = arcpy.Parameter(
            displayName='Secondary Species',
            name='secondary_species',
            datatype='GPString',
            parameterType='Optional',
            direction='Input',
            multiValue=True)

        # Range Version
        param_version = arcpy.Parameter(
            displayName='Range Version',
            name='range_version',
            datatype='GPString',
            parameterType='Required',
            direction='Input')
        param_version.value = '1.0'

        # Range Stage
        param_stage = arcpy.Parameter(
            displayName='Range Stage',
            name='range_stage',
            datatype='GPString',
            parameterType='Required',
            direction='Input')
        param_stage.value = 'Auto-generated'

        # External Range Polygons
        param_external_range_table = arcpy.Parameter(
            displayName='External Range Table',
            name='external_range_table',
            datatype='GPTableView',
            parameterType='Required',
            direction='Input')

        # Presence Field
        param_presence_field = arcpy.Parameter(
            displayName='Presence Field',
            name='presence_field',
            datatype='GPString',
            parameterType='Optional',
            direction='Input')

        # Review Label
        param_review_label = arcpy.Parameter(
            displayName='Review Label',
            name='review_label',
            datatype='GPString',
            parameterType='Required',
            direction='Input')

        # Jurisdictions Covered
        param_jurisdictions_covered = arcpy.Parameter(
            displayName='Jurisdictions Covered',
            name='jurisdictions_covered',
            datatype='GPString',
            parameterType='Optional',
            direction='Input',
            multiValue=True)

        # Username
        param_username = arcpy.Parameter(
            displayName='Username',
            name='username',
            datatype='GPString',
            parameterType='Required',
            direction='Input')

        params = [param_geodatabase, param_species, param_secondary, param_version, param_stage,
                  param_external_range_table, param_presence_field, param_review_label, param_jurisdictions_covered,
                  param_username]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is 
        called whenever a parameter has been changed."""
        # build list of jurisdictions (exclude AC because it is used for data only, not ecoshapes)
        if parameters[0].altered and parameters[0].value:
            param_geodatabase = parameters[0].valueAsText
            jur_list = []
            with arcpy.da.SearchCursor(param_geodatabase + '/Jurisdiction', ['JurisdictionName'],
                                       "JurisdictionAbbreviation <> 'AC'",
                                       sql_clause=(None,'ORDER BY JurisdictionName')) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    jur_list.append(row['JurisdictionName'])
                if len(jur_list) > 0:
                    del row
            parameters[8].filter.list = jur_list
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called 
        after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        ierr = ImportExternalRangeReviewTool.ImportExternalRangeReviewTool()
        ierr.runImportExternalRangeReviewTool(parameters, messages)
        return


class SyncSpeciesListKBA(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Sync Species List KBA'
        self.description = 'Synchronize the Species tables with WCS KBA updates'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Geodatabase
        param_geodatabase = arcpy.Parameter(
            displayName='Geodatabase',
            name='geodatabase',
            datatype='DEWorkspace',
            parameterType='Required',
            direction='Input')
        param_geodatabase.filter.list = ['Local Database', 'Remote Database']

        # CSV
        param_csv = arcpy.Parameter(
            displayName='CSV File',
            name='csv_file',
            datatype='DEFile',
            parameterType='Required',
            direction='Input')
        param_csv.filter.list = ['txt', 'csv']

        params = [param_geodatabase, param_csv]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is
        called whenever a parameter has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called
        after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        sslkba = SyncSpeciesListKBATool.SyncSpeciesListKBATool()
        sslkba.runSyncSpeciesListKBATool(parameters, messages)
        return


class BuildEBARDownloadTable(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Build EBAR Download Table'
        self.description = 'Build html table of all Range Maps available for download'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is
        called whenever a parameter has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called
        after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        bedt = BuildEBARDownloadTableTool.BuildEBARDownloadTableTool()
        bedt.runBuildEBARDownloadTableTool(parameters, messages)
        return


class BuildBulkDownloadTable(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Build Bulk Download Table'
        self.description = 'Build html table of all Category - Taxa Groups available for bulk download'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is
        called whenever a parameter has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called
        after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        bbdt = BuildBulkDownloadTableTool.BuildBulkDownloadTableTool()
        bbdt.runBuildBulkDownloadTableTool(parameters, messages)
        return


class ExportInputData(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Export Input Data'
        self.description = 'Export InputPoint/Line/Polygon records'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Geodatabase
        param_geodatabase = arcpy.Parameter(
            displayName='Geodatabase',
            name='geodatabase',
            datatype='DEWorkspace',
            parameterType='Required',
            direction='Input')
        param_geodatabase.filter.list = ['Local Database', 'Remote Database']

        # Jurisdictions Covered
        param_jurisdictions_covered = arcpy.Parameter(
            displayName='Jurisdictions Covered',
            name='jurisdictions_covered',
            datatype='GPString',
            parameterType='Required',
            direction='Input',
            multiValue=True)

        # Include CDC Data
        param_include_cdc = arcpy.Parameter(
            displayName='Include CDC Data',
            name='include_cdc',
            datatype='GPBoolean',
            parameterType='Required',
            direction='Input')
        param_include_cdc.value = 'false'

        # Include Restricted Data
        param_include_restricted = arcpy.Parameter(
            displayName='Include Restricted Data',
            name='include_restricted',
            datatype='GPBoolean',
            parameterType='Required',
            direction='Input')
        param_include_restricted.value = 'false'

        ## Include Other Dataset Types
        #param_include_other = arcpy.Parameter(
        #    displayName='Include Other Dataset Types',
        #    name='include_other',
        #    datatype='GPBoolean',
        #    parameterType='Required',
        #    direction='Input')
        #param_include_other.value = 'false'

        # Output Zip File Name
        param_output_zip = arcpy.Parameter(
            displayName='Output Zip File Name',
            name='output_zip',
            datatype='GPString',
            parameterType='Required',
            direction='Output')

        params = [param_geodatabase, param_jurisdictions_covered, param_include_cdc, param_include_restricted,
                  param_output_zip] # param_include_other, 
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is 
        called whenever a parameter has been changed."""
        # build list of jurisdictions (exclude AC because it is used for data only, not ecoshapes)
        if parameters[0].altered and parameters[0].value:
            param_geodatabase = parameters[0].valueAsText
            jur_list = []
            with arcpy.da.SearchCursor(param_geodatabase + '/Jurisdiction', ['JurisdictionName'],
                                       "JurisdictionAbbreviation NOT IN ('NL', 'NS', 'NB', 'PE')",
                                       sql_clause=(None,'ORDER BY JurisdictionName')) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    jur_list.append(row['JurisdictionName'])
                if len(jur_list) > 0:
                    del row
            parameters[1].filter.list = jur_list
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called 
        after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        ied = ExportInputDataTool.ExportInputDataTool()
        ied.runExportInputDataTool(parameters, messages)
        return


#class PublishRangeMap(object):
#    def __init__(self):
#        """Define the tool (tool name is the name of the class)."""
#        self.label = 'Publish Range Map'
#        self.description = 'Publish one Range Map as JPG, PDF and GIS Data Zip'
#        self.canRunInBackground = True

#    def getParameterInfo(self):
#        """Define parameter definitions"""
#        param_range_map_id = arcpy.Parameter(
#            displayName='Range Map ID',
#            name='range_map_id',
#            datatype='GPString',
#            parameterType='Required',
#            direction='Input')
#        param_spatial = arcpy.Parameter(
#            displayName='Output GIS Data Zip',
#            name='spatial',
#            datatype='GPBoolean',
#            parameterType='Required',
#            direction='Input')
#        param_spatial.value = 'true'
#        params = [param_range_map_id, param_spatial]
#        return params

#    def isLicensed(self):
#        """Set whether tool is licensed to execute."""
#        return True

#    def updateParameters(self, parameters):
#        """Modify the values and properties of parameters before internal validation is performed.  This method is
#        called whenever a parameter has been changed."""
#        return

#    def updateMessages(self, parameters):
#        """Modify the messages created by internal validation for each tool parameter.  This method is called
#        after internal validation."""
#        return

#    def execute(self, parameters, messages):
#        """The source code of the tool."""
#        prm = PublishRangeMapTool.PublishRangeMapTool()
#        prm.runPublishRangeMapTool(parameters, messages)
#        return
