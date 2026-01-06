# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Samantha Stefanoff
# © NatureServe Canada 2026 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: ExportHBJBLData.py
# Upublished ArcGIS Python tool for exporting InputPoint/Line/Polygon records for HBJBL
# Restricted records

# Notes:
# - Relies on views in server geodatabase, so not possible to use/debug with local file gdb???

# import Python packages
import EBARUtils
import arcpy
import datetime


class ExportHBJBLDataTool:
    """Export InputPoint/Line/Polygon records for HBJBL"""
    def __init__(self):
        pass

    def runExportHBJBLDataTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        param_geodatabase = parameters[0].valueAsText
        param_custom_polygon = parameters[1].valueAsText
        param_output_zip = parameters[2].valueAsText
        if param_output_zip[-4:] != '.zip':
            param_output_zip += '.zip'

        # check for existing output
        if arcpy.Exists(EBARUtils.download_folder + '/' + param_output_zip):
            EBARUtils.displayMessage(messages,
                                     'ERROR: output file already exists')
            # terminate with error
            return
            #raise arcpy.ExecuteError

        # create output_gdb
        output_gdb = 'EBARExport' + str(start_time.year) + str(start_time.month) + str(start_time.day) + \
            str(start_time.hour) + str(start_time.minute) + str(start_time.second) + '.gdb'
        arcpy.CreateFileGDB_management(EBARUtils.temp_folder, output_gdb)
        output_gdb = EBARUtils.temp_folder + '/' + output_gdb

        # select custom polygon
        EBARUtils.displayMessage(messages, 'Selecting custom polygon')
        arcpy.MakeFeatureLayer_management(param_custom_polygon, 'jurs')

        # generate metadata
        EBARUtils.displayMessage(messages, 'Generating metadata')
        md = arcpy.metadata.Metadata()
        md.tags = 'Species Data, NatureServe Canada'
        md.description = 'Export of Species data from EBAR-KBA database. ' + \
            'Please see EBAR_HBJBLExportReadme.txt for field descriptions.'
        md.credits = 'Please credit original providers as per DatasetSourceCitation field.'
        md.accessConstraints = 'Please credit original providers as per DatasetSourceCitation field.'

        # process points, lines and polygons
        EBARUtils.displayMessage(messages, 'Processing points')
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/hx_InputPoint', 'points')
        self.processFeatureClass('points', 'jurs', output_gdb, 'EBARPoints', md)
        EBARUtils.displayMessage(messages, 'Processing lines')
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/hx_InputLine', 'lines')
        self.processFeatureClass('lines', 'jurs', output_gdb, 'EBARLines', md)
        EBARUtils.displayMessage(messages, 'Processing polygons')
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/hx_InputPolygon', 'ebar_polygons')
        self.processFeatureClass('ebar_polygons', 'jurs', output_gdb, 'EBARPolygons', md)
        #EBARUtils.displayMessage(messages, 'Processing Other polygons')
        #arcpy.MakeFeatureLayer_management(param_geodatabase + '/x_InputPolygon', 'other_polygons')
        #self.processFeatureClass('other_polygons', 'jurs', param_include_cdc, param_include_restricted, output_gdb,
        #                         'OtherPolygons', md)

        # process species/synonyms
        EBARUtils.displayMessage(messages, 'Processing Species/Synonyms')
        fieldinfo = arcpy.FieldInfo()
        fieldinfo.addField('SpeciesID', 'SpeciesID', 'VISIBLE', '')
        fieldinfo.addField('ELEMENT_NATIONAL_ID', 'ELEMENT_NATIONAL_ID', 'VISIBLE', '')
        fieldinfo.addField('ELEMENT_GLOBAL_ID', 'ELEMENT_GLOBAL_ID', 'VISIBLE', '')
        fieldinfo.addField('ELEMENT_CODE', 'ELEMENT_CODE', 'VISIBLE', '')
        fieldinfo.addField('NATIONAL_SCIENTIFIC_NAME', 'NATIONAL_SCIENTIFIC_NAME', 'VISIBLE', '')
        fieldinfo.addField('NATIONAL_ENGL_NAME', 'NATIONAL_ENGL_NAME', 'VISIBLE', '')
        fieldinfo.addField('NATIONAL_FR_NAME', 'NATIONAL_FR_NAME', 'VISIBLE', '')
        fieldinfo.addField('GLOBAL_SCIENTIFIC_NAME', 'GLOBAL_SCIENTIFIC_NAME', 'VISIBLE', '')
        fieldinfo.addField('GLOBAL_SYNONYMS', 'GLOBAL_SYNONYMS', 'VISIBLE', '')
        fieldinfo.addField('GLOBAL_ENGL_NAME', 'GLOBAL_ENGL_NAME', 'VISIBLE', '')
        fieldinfo.addField('GLOB_FR_NAME', 'GLOB_FR_NAME', 'VISIBLE', '')
        fieldinfo.addField('COSEWIC_NAME', 'COSEWIC_NAME', 'VISIBLE', '')
        fieldinfo.addField('ENGLISH_COSEWIC_COM_NAME', 'ENGLISH_COSEWIC_COM_NAME', 'VISIBLE', '')
        fieldinfo.addField('FRENCH_COSEWIC_COM_NAME', 'FRENCH_COSEWIC_COM_NAME', 'VISIBLE', '')
        fieldinfo.addField('COSEWIC_ID', 'COSEWIC_ID', 'VISIBLE', '')
        fieldinfo.addField('CA_NNAME_LEVEL', 'CA_NNAME_LEVEL', 'VISIBLE', '')
        fieldinfo.addField('CATEGORY', 'CATEGORY', 'VISIBLE', '')
        fieldinfo.addField('TAX_GROUP', 'TAX_GROUP', 'VISIBLE', '')
        fieldinfo.addField('FAMILY_COM', 'FAMILY_COM', 'VISIBLE', '')
        fieldinfo.addField('GENUS', 'GENUS', 'VISIBLE', '')
        fieldinfo.addField('PHYLUM', 'PHYLUM', 'VISIBLE', '')
        fieldinfo.addField('CLASSIFICATION_STATUS', 'CLASSIFICATION_STATUS', 'VISIBLE', '')
        fieldinfo.addField('SHORT_CITATION_AUTHOR', 'SHORT_CITATION_AUTHOR', 'VISIBLE', '')
        fieldinfo.addField('SHORT_CITATION_YEAR', 'SHORT_CITATION_YEAR', 'VISIBLE', '')
        fieldinfo.addField('FORMATTED_FULL_CITATION', 'FORMATTED_FULL_CITATION', 'VISIBLE', '')
        fieldinfo.addField('AUTHOR_NAME', 'AUTHOR_NAME', 'VISIBLE', '')
        fieldinfo.addField('NSX_URL', 'NSX_URL', 'VISIBLE', '')
        arcpy.MakeTableView_management(param_geodatabase + '/BIOTICS_ELEMENT_NATIONAL', 'biotics',
                                       #"SpeciesID IN (SELECT SpeciesID FROM Species WHERE HBJBLPriority = 'Y')",
                                       field_info=fieldinfo)
        arcpy.TableToTable_conversion('biotics', output_gdb, 'BIOTICS_ELEMENT_NATIONAL')
        arcpy.MakeTableView_management(param_geodatabase + '/Synonym', 'synonym')
                                       #"SpeciesID IN (SELECT SpeciesID FROM Species WHERE HBJBLPriority = 'Y')")
        arcpy.TableToTable_conversion('synonym', output_gdb, 'Synonym')

        # create relationships
        arcpy.management.CreateRelationshipClass(output_gdb + '/BIOTICS_ELEMENT_NATIONAL', output_gdb + '/Synonym',
                                                 output_gdb + '/BIOTICS_ELEMENT_NATIONAL_Synonym', 'SIMPLE',
                                                 'Synonym', 'BIOTICS_ELEMENT_NATIONAL', 'NONE', 'ONE_TO_MANY', 'NONE',
                                                 'SpeciesID', 'SpeciesID')
        arcpy.management.CreateRelationshipClass(output_gdb + '/BIOTICS_ELEMENT_NATIONAL', output_gdb + '/EBARPoints',
                                                 output_gdb + '/BIOTICS_ELEMENT_NATIONAL_EBARPoints', 'SIMPLE',
                                                 'EBARPoints', 'BIOTICS_ELEMENT_NATIONAL', 'NONE', 'ONE_TO_MANY',
                                                 'NONE', 'SpeciesID', 'SpeciesID')
        arcpy.management.CreateRelationshipClass(output_gdb + '/BIOTICS_ELEMENT_NATIONAL', output_gdb + '/EBARLines',
                                                 output_gdb + '/BIOTICS_ELEMENT_NATIONAL_EBARLiness', 'SIMPLE',
                                                 'EBARLines', 'BIOTICS_ELEMENT_NATIONAL', 'NONE', 'ONE_TO_MANY',
                                                 'NONE', 'SpeciesID', 'SpeciesID')
        arcpy.management.CreateRelationshipClass(output_gdb + '/BIOTICS_ELEMENT_NATIONAL', output_gdb + '/EBARPolygons',
                                                 output_gdb + '/BIOTICS_ELEMENT_NATIONAL_EBARPolygons', 'SIMPLE',
                                                 'EBARPolygons', 'BIOTICS_ELEMENT_NATIONAL', 'NONE', 'ONE_TO_MANY',
                                                 'NONE', 'SpeciesID', 'SpeciesID')

        # zip gdb into single file for download
        EBARUtils.displayMessage(messages, 'Zipping output')
        EBARUtils.createZip(output_gdb, EBARUtils.download_folder + '/' + param_output_zip, None)
        EBARUtils.addToZip(EBARUtils.download_folder + '/' + param_output_zip,
                           EBARUtils.resources_folder + '/EBAR_HBJBLExportReadme.txt')

        # download message
        EBARUtils.displayMessage(messages,
                                 'Please download output from https://gis.natureserve.ca/download/' + param_output_zip)

    #def processFeatureClass(self, fclyr, jurs, include_cdc, include_restricted, output_gdb, output_fc, md):
    def processFeatureClass(self, fclyr, jurs, output_gdb, output_fc, md):
        # select features using non-spatial criteria
        where_clause = None
        if fclyr == 'ebar_polygons':
            if not where_clause:
                where_clause = ''
            else:
                where_clause += ' AND '
            # these types go to other polygons
            where_clause += "DatasetType NOT IN ('Critical Habitat', 'Range Estimate', 'Habitat Suitability', " + \
                "'Area of Occupancy', 'Other', 'Other Observations', 'Other Range')"
        if fclyr == 'other_polygons':
            if not where_clause:
                where_clause = ''
            else:
                where_clause += ' AND '
            where_clause += "DatasetType IN ('Critical Habitat', 'Range Estimate', 'Habitat Suitability'"
            #if include_other == 'true':
            #    where_clause += ", 'Area of Occupancy', 'Other', 'Other Observations', 'Other Range'"
            where_clause += ')'
        arcpy.SelectLayerByAttribute_management(fclyr, 'NEW_SELECTION', where_clause)
        # sub-select features using spatial criteria
        arcpy.SelectLayerByLocation_management(fclyr, 'INTERSECT', jurs, selection_type='SUBSET_SELECTION')
        # map fields
        field_mappings = arcpy.FieldMappings()
        if EBARUtils.checkField(fclyr, 'inputpointid'):
            field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'inputpointid', 'InputPointID', 'Long'))
        if EBARUtils.checkField(fclyr, 'inputlineid'):
            field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'inputlineid', 'InputLineID', 'Long'))
        if EBARUtils.checkField(fclyr, 'inputpolygonid'):
            field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'inputpolygonid', 'InputPolygonID', 'Long'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'originalinstitutioncode', 'OrginalInstitutionCode',
                                                            'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'rightsholder', 'RightsHolder', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'mindate', 'MinDate', 'Date'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'maxdate', 'MaxDate', 'Date'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'partialdate', 'PartialDate', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'accuracy', 'Accuracy', 'Long'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'individualcount', 'IndividualCount', 'Long'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'datasetsourceuniqueid', 'DatasetSourceUniqueID',
                                                            'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'uri', 'URI', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'license', 'License', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'coordinatesobscured', 'CoordinatesObscured',
                                                            'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'representationaccuracy', 'RepresentationAccuracy',
                                                            'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'speciesid', 'SpeciesID', 'Long'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'element_national_id', 'ELEMENT_NATIONAL_ID',
                                                            'Long'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'element_global_id', 'ELEMENT_GLOBAL_ID', 'Long'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'element_code', 'ELEMENT_CODE', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'national_scientific_name',
                                                            'NATIONAL_SCIENTIFIC_NAME', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'national_engl_name', 'NATIONAL_ENGL_NAME', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'national_fr_name', 'NATIONAL_FR_NAME', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'synonymname', 'SynonymName', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'datereceived', 'DateReceived', 'Date'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'sensitiveecologicaldatacat',
                                                            'SensitiveEcologicalDataCat', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'datasetname', 'DatasetName', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'datasetsourcename', 'DatasetSourceName', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'datasetsourcecitation', 'DatasetSourceCitation',
                                                            'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'datasettype', 'DatasetType', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'dataqcstatus', 'DataQCStatus', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'datasensitivity', 'DataSensitivity', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'datasensitivitycat', 'DataSensitivityCat', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'descriptor', 'Descriptor', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'digitizingcomments', 'DigitizingComments', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'independentsf', 'IndependentSF', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'locuncertaintydistcls','LocUncertaintyDistCls',
                                                            'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'locuncertaintydistunit', 'LocUncertaintyDistUnit',
                                                            'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'locuncertaintytype', 'LocUncertaintyType', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'locuseclass', 'LocUseClass', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'mappingcomments', 'MappingComments', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'mapqcstatus', 'MapQCStatus', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'qccomments', 'QCComments', 'Text'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'unsuitablehabexcluded', 'UnsuitableHabExcluded', 'Text'))
        # export features
        arcpy.FeatureClassToFeatureClass_conversion(fclyr, output_gdb, output_fc, field_mapping=field_mappings)
        # embed metadata
        fc_md = arcpy.metadata.Metadata(output_gdb + '/' + output_fc)
        fc_md.copy(md)
        fc_md.save()


# controlling process
if __name__ == '__main__':
    ehd = ExportHBJBLDataTool()
    parameters = []
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:/GIS/EBAR/nsc-gis-ebarkba.sde'
    param_custom_polygon = arcpy.Parameter()
    param_custom_polygon.value = 'C:/GIS/EBAR/HBJBL_Seal_Buffer_10.gdb/HBJBL_Seal_Buffer_10_Dissolve'
    param_output_zip = arcpy.Parameter()
    param_output_zip.value = 'EBAR_HBJBLExport_July2025.zip'
    parameters = [param_geodatabase, param_custom_polygon, param_output_zip]
    ehd.runExportHBJBLDataTool(parameters, None)
