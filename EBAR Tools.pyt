# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen, Meg Southee
# © NatureServe Canada 2020 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: EBAR Tools.pyt
# ArcGIS Python toolbox for importing species datasets and generating EBAR maps

# Notes:
# - following 120 maximum line length "convention"
# - tested with ArcGIS Pro 2.8.1


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
#import FlagBadDataUsingRangeTool
import DeleteRangeMapTool
import ImportVisitsTool
import SummarizeDownloadsTool
import PublishRangeMapTool
import PublishRangeMapSetsTool
import FlagBadDataUsingIDTool
import RecordInputFeedbackTool
import DeleteInputFeedbackTool
import PrepareNSXProTransferTool
import EBARUtils
import datetime
import locale


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = 'EBAR Tools'
        self.alias = 'EBARTools'

        # List of tool classes associated with this toolbox
        self.tools = [ImportTabularData, ImportSpatialData, GenerateRangeMap, ListElementNationalIDs,
                      SyncSpeciesListBiotics, AddSynonyms, ImportExternalRangeReview, SyncSpeciesListKBA,
                      BuildEBARDownloadTable, BuildBulkDownloadTable, ExportInputData, #FlagBadDataUsingRange,
                      DeleteRangeMap, ImportVisits, SummarizeDownloads, PublishRangeMap, PublishRangeMapSets,
                      FlagBadDataUsingID, RecordInputFeedback, DeleteInputFeedback, PrepareNSXProTransfer]


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

        # # Dataset Restrictions
        # param_dataset_restrictions = arcpy.Parameter(
        #     displayName='Dataset Restrictions',
        #     name='dataset_restrictions',
        #     datatype='GPString',
        #     parameterType='Required',
        #     direction='Input')
        # param_dataset_restrictions.value = 'Non-restricted'
        
        # Sensitivity/Restriction Reason
        param_senstivity_restriction_reason = arcpy.Parameter(
            displayName='Sensitivity/Restriction Reason',
            name='sensitivity_restriction_reason',
            datatype='GPString',
            parameterType='Optional',
            direction='Input')
        
        params = [param_geodatabase, param_raw_data_file, param_dataset_name, param_dataset_source,
                  param_date_received, param_senstivity_restriction_reason] # param_dataset_restrictions]
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

        # domains = arcpy.da.ListDomains(parameters[0].valueAsText)
        # restrictions_list = []
        # for domain in domains:
        #     if domain.name == 'Restriction':
        #         restrictions_list = list(domain.codedValues.values())
        # parameters[5].filter.list = sorted(restrictions_list)
        # return

        domains = arcpy.da.ListDomains(parameters[0].valueAsText)
        sensitivity_restriction_reason_list = []
        for domain in domains:
            if domain.name == 'SensitivityRestrictionReason':
                sensitivity_restriction_reason_list = list(domain.codedValues.values())
        parameters[5].filter.list = sorted(sensitivity_restriction_reason_list)
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

        # # Dataset Restrictions
        # param_dataset_restrictions = arcpy.Parameter(
        #     displayName='Dataset Restrictions',
        #     name='dataset_restrictions',
        #     datatype='GPString',
        #     parameterType='Required',
        #     direction='Input')
        # param_dataset_restrictions.value = 'Non-restricted'
        
        # Sensitivity/Restriction Reason
        param_senstivity_restriction_reason = arcpy.Parameter(
            displayName='Sensitivity/Restriction Reason',
            name='sensitivity_restriction_reason',
            datatype='GPString',
            parameterType='Optional',
            direction='Input')

        params = [param_geodatabase, param_import_feature_class, param_dataset_name, param_dataset_source,
                  param_date_received, param_senstivity_restriction_reason] #param_dataset_restrictions]
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

        # domains = arcpy.da.ListDomains(parameters[0].valueAsText)
        # restrictions_list = []
        # for domain in domains:
        #     if domain.name == 'Restriction':
        #         restrictions_list = list(domain.codedValues.values())
        # parameters[5].filter.list = sorted(restrictions_list)
        # return

        domains = arcpy.da.ListDomains(parameters[0].valueAsText)
        sensitivity_restriction_reason_list = []
        for domain in domains:
            if domain.name == 'SensitivityRestrictionReason':
                sensitivity_restriction_reason_list = list(domain.codedValues.values())
        parameters[5].filter.list = sorted(sensitivity_restriction_reason_list)
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

        # Jurisdictions Covered
        param_jurisdictions_covered = arcpy.Parameter(
            displayName='Jurisdictions Covered',
            name='jurisdictions_covered',
            datatype='GPString',
            parameterType='Optional',
            direction='Input',
            multiValue=True)

        # Custom Polygons Covered
        param_custom_polygons_covered = arcpy.Parameter(
            displayName='Custom Polygons Covered',
            name='custom_polygons_covered',
            datatype='GPFeatureLayer',
            parameterType='Optional',
            direction='Input')
        param_custom_polygons_covered.filter.list = ['Polygon', 'MultiPatch']

        # Differentiate Usage Type
        param_differentiate_usage_type = arcpy.Parameter(
            displayName='Differentiate Usage Type',
            name='differentiate_usage_type',
            datatype='GPBoolean',
            parameterType='Required',
            direction='Input')
        param_differentiate_usage_type.value = 'false'

        params = [param_geodatabase, param_species, param_secondary, param_version, param_stage, param_scope,
                  param_jurisdictions_covered, param_custom_polygons_covered, param_differentiate_usage_type]
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

        # build list of jurisdictions (exclude AC, NF, LB because they are used for data only, not ecoshapes)
        if parameters[0].altered and parameters[0].value:
            param_geodatabase = parameters[0].valueAsText
            jur_list = []
            with arcpy.da.SearchCursor(param_geodatabase + '/Jurisdiction', ['JurisdictionName'],
                                       "JurisdictionAbbreviation NOT IN ('AC', 'NF', 'LB')",
                                       sql_clause=(None,'ORDER BY JurisdictionName')) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    jur_list.append(row['JurisdictionName'])
                if len(jur_list) > 0:
                    del row
            parameters[6].filter.list = jur_list
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

        # External Range Table
        param_external_range_table = arcpy.Parameter(
            displayName='External Range Table',
            name='external_range_table',
            datatype=['GPTableView', 'GPFeatureLayer'],
            parameterType='Required',
            direction='Input')

        # Presence Field
        param_presence_field = arcpy.Parameter(
            displayName='Presence Field',
            name='presence_field',
            datatype='GPString',
            parameterType='Optional',
            direction='Input')

        # UsageType Field
        param_usagetype_field = arcpy.Parameter(
            displayName='UsageType Field',
            name='usagetype_field',
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

        # Overall Review Notes
        param_overall_review_notes = arcpy.Parameter(
            displayName='Overall Review Notes',
            name='overall_review_notes',
            datatype='GPString',
            parameterType='Optional',
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

        # Additions Only
        param_additions_only = arcpy.Parameter(
            displayName='Additions Only',
            name='additions_only',
            datatype='GPBoolean',
            parameterType='Required',
            direction='Input')
        param_additions_only.value = 'false'

        params = [param_geodatabase, param_species, param_secondary, param_version, param_stage,
                  param_external_range_table, param_presence_field, param_usagetype_field, param_review_label,
                  param_overall_review_notes, param_jurisdictions_covered, param_username, param_additions_only]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is 
        called whenever a parameter has been changed."""
        # build list of jurisdictions (exclude AC, NF, LB because they are used for data only, not ecoshapes)
        if parameters[0].altered and parameters[0].value:
            param_geodatabase = parameters[0].valueAsText
            jur_list = []
            with arcpy.da.SearchCursor(param_geodatabase + '/Jurisdiction', ['JurisdictionName'],
                                       "JurisdictionAbbreviation NOT IN ('AC', 'NF', 'LB')",
                                       sql_clause=(None,'ORDER BY JurisdictionName')) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    jur_list.append(row['JurisdictionName'])
                if len(jur_list) > 0:
                    del row
            parameters[10].filter.list = jur_list
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
        self.description = 'Export InputPoint/Line/Polygon records, excluding "other" DatasetTypes and EBAR Restricted records'
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

        # # Include Restricted Data
        # param_include_restricted = arcpy.Parameter(
        #     displayName='Include Restricted Data',
        #     name='include_restricted',
        #     datatype='GPBoolean',
        #     parameterType='Required',
        #     direction='Input')
        # param_include_restricted.value = 'false'

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
            direction='Input')

        params = [param_geodatabase, param_jurisdictions_covered, param_include_cdc, #param_include_restricted,
                  param_output_zip] # param_include_other, 
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is 
        called whenever a parameter has been changed."""
        # build list of jurisdictions
        # exclude Atlantic Canadian jurisdictions because they are lumped as AC
        # exclude Canada because it is a special juridiction that does have polygons in JurisdictionBufferFull
        if parameters[0].altered and parameters[0].value:
            param_geodatabase = parameters[0].valueAsText
            jur_list = []
            with arcpy.da.SearchCursor(param_geodatabase + '/Jurisdiction', ['JurisdictionName'],
                                       "JurisdictionAbbreviation NOT IN ('NL', 'NS', 'NB', 'PE', 'NF', 'LB')",
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


# class FlagBadDataUsingRange(object):
#     def __init__(self):
#         """Define the tool (tool name is the name of the class)."""
#         self.label = 'Flag Bad Data Using Range'
#         self.description = 'Use reviewed range to identify and flag bad input data'
#         self.canRunInBackground = True

#     def getParameterInfo(self):
#         """Define parameter definitions"""
#         # Geodatabase
#         param_geodatabase = arcpy.Parameter(
#             displayName='Geodatabase',
#             name='geodatabase',
#             datatype='DEWorkspace',
#             parameterType='Required',
#             direction='Input')
#         param_geodatabase.filter.list = ['Local Database', 'Remote Database']

#         # Range Map ID
#         param_range_map_id = arcpy.Parameter(
#             displayName='Range Map ID',
#             name='range_map_id',
#             datatype='GPLong',
#             parameterType='Required',
#             direction='Input')
#         params = [param_geodatabase, param_range_map_id]
#         return params

#     def isLicensed(self):
#         """Set whether tool is licensed to execute."""
#         return True

#     def updateParameters(self, parameters):
#         """Modify the values and properties of parameters before internal validation is performed.  This method is 
#         called whenever a parameter has been changed."""
#         return

#     def updateMessages(self, parameters):
#         """Modify the messages created by internal validation for each tool parameter.  This method is called 
#         after internal validation."""
#         return

#     def execute(self, parameters, messages):
#         """The source code of the tool."""
#         fbdur = FlagBadDataUsingRangeTool.FlagBadDataUsingRangeTool()
#         fbdur.runFlagBadDataUsingRangeTool(parameters, messages)
#         return


class DeleteRangeMap(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Delete Range Map'
        self.description = 'Delete Range Map and related records from the EBAR geodatabase'
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

        # Range Map ID
        param_range_map_id = arcpy.Parameter(
            displayName='Range Map ID',
            name='range_map_id',
            datatype='GPLong',
            parameterType='Required',
            direction='Input')
        params = [param_geodatabase, param_range_map_id]
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
        drm = DeleteRangeMapTool.DeleteRangeMapTool()
        drm.runDeleteRangeMapTool(parameters, messages)
        return


class ImportVisits(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Import Visits'
        self.description = 'Imports visits and relates them to the appropriate InputPoint/Line/Polygon based on ' + \
            'SFID and Subnation'
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

        # Subnation
        param_subnation = arcpy.Parameter(
            displayName='Subnation',
            name='subnation',
            datatype='GPString',
            parameterType='Required',
            direction='Input')

        params = [param_geodatabase, param_raw_data_file, param_subnation]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is 
        called whenever a parameter has been changed."""
        # build list of subnations (Canadian only, with NL split into NF and LB)
        if parameters[0].altered and parameters[0].value:
            param_geodatabase = parameters[0].valueAsText
            subnation_list = []
            with arcpy.da.SearchCursor(param_geodatabase + '/Jurisdiction', ['JurisdictionName'],
                                       "JurisdictionAbbreviation NOT IN ('AC', 'NL', 'US', 'MX')",
                                       sql_clause=(None,'ORDER BY JurisdictionName')) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    subnation_list.append(row['JurisdictionName'])
                if len(subnation_list) > 0:
                    del row
            parameters[2].filter.list = subnation_list
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called "
        "after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        iv = ImportVisitsTool.ImportVisitsTool()
        iv.runImportVisitsTool(parameters, messages)
        return


class SummarizeDownloads(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Summarize Downloads'
        self.description = 'Summarize downloads by month'
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
        sd = SummarizeDownloadsTool.SummarizeDownloadsTool()
        sd.runSummarizeDownloadsTool(parameters, messages)
        return


class PublishRangeMap(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Publish Range Map'
        self.description = 'Publish one Range Map as JPG, PDF and GIS Data Zip'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        param_range_map_id = arcpy.Parameter(
            displayName='Range Map ID',
            name='range_map_id',
            datatype='GPString',
            parameterType='Required',
            direction='Input')
        param_spatial = arcpy.Parameter(
            displayName='Output GIS Data Zip',
            name='spatial',
            datatype='GPBoolean',
            parameterType='Required',
            direction='Input')
        param_spatial.value = 'true'
        params = [param_range_map_id, param_spatial]
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
        prm = PublishRangeMapTool.PublishRangeMapTool()
        prm.runPublishRangeMapTool(parameters, messages)
        return


class PublishRangeMapSets(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Publish Range Map Sets'
        self.description = 'Create Zip sets of PDFs and Spatial Data per Category/Taxa'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        param_category = arcpy.Parameter(
            displayName='Category',
            name='category',
            datatype='GPString',
            parameterType='Optional',
            direction='Input')
        param_taxagroup = arcpy.Parameter(
            displayName='Taxa Group',
            name='taxagroup',
            datatype='GPString',
            parameterType='Optional',
            direction='Input')
        params = [param_category, param_taxagroup]
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
        prms = PublishRangeMapSetsTool.PublishRangeMapSetsTool()
        prms.runPublishRangeMapSetsTool(parameters, messages)
        return


class FlagBadDataUsingID(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Flag Bad Data Using ID'
        self.description = 'Flag bad input data using an InputPoint/Line/PolygonID'
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

        # Input Point ID
        param_input_point_id = arcpy.Parameter(
            displayName='Input Point ID',
            name='input_point_id',
            datatype='GPLong',
            parameterType='Optional',
            direction='Input')

        # Input Line ID
        param_input_line_id = arcpy.Parameter(
            displayName='Input Line ID',
            name='input_line_id',
            datatype='GPLong',
            parameterType='Optional',
            direction='Input')

        # Input Polygon ID
        param_input_polygon_id = arcpy.Parameter(
            displayName='Input Polygon ID',
            name='input_polygon_id',
            datatype='GPLong',
            parameterType='Optional',
            direction='Input')

        # Justification
        param_justification = arcpy.Parameter(
            displayName='Justification',
            name='justification',
            datatype='GPString',
            parameterType='Optional',
            direction='Input')

        # Undo
        param_undo = arcpy.Parameter(
            displayName='Undo',
            name='undo',
            datatype='GPBoolean',
            parameterType='Required',
            direction='Input')
        param_undo.value = 'false'

        params = [param_geodatabase, param_input_point_id, param_input_line_id, param_input_polygon_id,
                  param_justification, param_undo]
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
        fbdui = FlagBadDataUsingIDTool.FlagBadDataUsingIDTool()
        fbdui.runFlagBadDataUsingIDTool(parameters, messages)
        return


class RecordInputFeedback(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Record Input Feedback'
        self.description = 'Add a record to the InputFeedback table'
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

        # Input Point ID
        param_input_point_id = arcpy.Parameter(
            displayName='Input Point ID',
            name='input_point_id',
            datatype='GPLong',
            parameterType='Optional',
            direction='Input',
            multiValue=True)

        # Input Line ID
        param_input_line_id = arcpy.Parameter(
            displayName='Input Line ID',
            name='input_line_id',
            datatype='GPLong',
            parameterType='Optional',
            direction='Input',
            multiValue=True)

        # Input Polygon ID
        param_input_polygon_id = arcpy.Parameter(
            displayName='Input Polygon ID',
            name='input_polygon_id',
            datatype='GPLong',
            parameterType='Optional',
            direction='Input',
            multiValue=True)

        # Notes
        param_notes = arcpy.Parameter(
            displayName='Notes',
            name='notes',
            datatype='GPString',
            parameterType='Optional',
            direction='Input')

        # Exclude From Range Map ID
        param_exclude_from_range_map_id = arcpy.Parameter(
            displayName='Exclude From Range Map ID',
            name='exclude_from_range_map_id',
            datatype='GPLong',
            parameterType='Optional',
            direction='Input')

        # Exclude From All Range Maps
        param_exclude_from_all_range_maps = arcpy.Parameter(
            displayName='Exclude From All Range Maps',
            name='exclude_from_all_range_maps',
            datatype='GPBoolean',
            parameterType='Required',
            direction='Input')
        param_exclude_from_all_range_maps.value = 'false'

        # Justification
        param_justification = arcpy.Parameter(
            displayName='Justification',
            name='justification',
            datatype='GPString',
            parameterType='Optional',
            direction='Input')

        params = [param_geodatabase, param_input_point_id, param_input_line_id, param_input_polygon_id, param_notes,
                  param_exclude_from_range_map_id, param_exclude_from_all_range_maps, param_justification]
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
        rif = RecordInputFeedbackTool.RecordInputFeedbackTool()
        rif.runRecordInputFeedbackTool(parameters, messages)
        return


class DeleteInputFeedback(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Delete Input Feedback'
        self.description = 'Delete an existing record from the InputFeedback table'
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

        # Input Feedback ID
        param_input_feedback_id = arcpy.Parameter(
            displayName='Input Feedback ID',
            name='input_feedback_id',
            datatype='GPLong',
            parameterType='Required',
            direction='Input',
            multiValue=True)

        params = [param_geodatabase, param_input_feedback_id]
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
        dif = DeleteInputFeedbackTool.DeleteInputFeedbackTool()
        dif.runDeleteInputFeedbackTool(parameters, messages)
        return


class PrepareNSXProTransfer(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Prepare NSX Pro Transfer'
        self.description = 'Set InputPoint/Polygon fields used by the NSXProTransfer service'
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
        pnpt = PrepareNSXProTransferTool.PrepareNSXProTransferTool()
        pnpt.runPrepareNSXProTransferTool(parameters, messages)
        return
