# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Samantha Stefanoff
# © NatureServe Canada 2024 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: ExportECCCData.py
# Upublished ArcGIS Python tool for exporting InputPoint/Line/Polygon records for ECCC
# Restricted records

# Notes:
# - Relies on views in server geodatabase, so not possible to use/debug with local file gdb???

# import Python packages
import EBARUtils
import arcpy
import datetime


class ExportECCCDataTool:
    """Export InputPoint/Line/Polygon records for ECCC"""
    def __init__(self):
        pass

    def runExportECCCDataTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        param_geodatabase = parameters[0].valueAsText
        param_jurisdictions_covered = parameters[1].valueAsText
        # convert to Python list
        param_jurisdictions_list = []
        param_jurisdictions_list = param_jurisdictions_covered.replace("'", '')
        param_jurisdictions_list = param_jurisdictions_list.split(';')
        jur_ids_comma = EBARUtils.buildJurisdictionList(param_geodatabase, param_jurisdictions_list)
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

        # select jurisdiction(s)
        EBARUtils.displayMessage(messages, 'Selecting jurisdiction(s)')
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/JurisdictionBufferFull', 'jurs')
        arcpy.SelectLayerByAttribute_management('jurs', 'NEW_SELECTION', 'JurisdictionID IN ' + jur_ids_comma)

        # generate metadata
        EBARUtils.displayMessage(messages, 'Generating metadata')
        md = arcpy.metadata.Metadata()
        md.tags = 'Species Data, NatureServe Canada'
        md.description = 'Export of Species data from EBAR-KBA database. ' + \
            'Please see EBAR_ECCCExportReadme.txt for field descriptions.'
        md.credits = 'Please credit original providers as per DatasetSourceCitation field.'
        # if param_include_restricted  == 'true' or param_include_cdc == 'true':
        #     md.accessConstraints = 'Some data has restrictions. ' + \
        #         'Please check with EBAR-KBA@natureserve.ca before sharing.'
        # else:
        #     md.accessConstraints = 'Please credit original providers as per DatasetSourceCitation field.'
        md.accessConstraints = 'Please credit original providers as per DatasetSourceCitation field.'

        # process points, lines and polygons
        EBARUtils.displayMessage(messages, 'Processing points')
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/ex_InputPoint', 'points')
        # self.processFeatureClass('points', 'jurs', param_include_cdc, param_include_restricted, output_gdb,
        #                          'EBARPoints', md)
        self.processFeatureClass('points', 'jurs', output_gdb, 'EBARPoints', md)
        EBARUtils.displayMessage(messages, 'Processing lines')
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/ex_InputLine', 'lines')
        # self.processFeatureClass('lines', 'jurs', param_include_cdc, param_include_restricted, output_gdb,
        #                          'EBARLines', md)
        self.processFeatureClass('lines', 'jurs', output_gdb, 'EBARLines', md)
        EBARUtils.displayMessage(messages, 'Processing polygons')
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/ex_InputPolygon', 'ebar_polygons')
        # self.processFeatureClass('ebar_polygons', 'jurs', param_include_cdc, param_include_restricted, output_gdb,
        #                          'EBARPolygons', md)
        self.processFeatureClass('ebar_polygons', 'jurs', output_gdb, 'EBARPolygons', md)
        #EBARUtils.displayMessage(messages, 'Processing Other polygons')
        #arcpy.MakeFeatureLayer_management(param_geodatabase + '/x_InputPolygon', 'other_polygons')
        #self.processFeatureClass('other_polygons', 'jurs', param_include_cdc, param_include_restricted, output_gdb,
        #                         'OtherPolygons', md)

        # zip gdb into single file for download
        EBARUtils.displayMessage(messages, 'Zipping output')
        EBARUtils.createZip(output_gdb, EBARUtils.download_folder + '/' + param_output_zip, None)
        EBARUtils.addToZip(EBARUtils.download_folder + '/' + param_output_zip,
                           EBARUtils.resources_folder + '/EBAR_ECCCExportReadme.txt')

        # download message
        EBARUtils.displayMessage(messages,
                                 'Please download output from https://gis.natureserve.ca/download/' + param_output_zip)

    #def processFeatureClass(self, fclyr, jurs, include_cdc, include_restricted, output_gdb, output_fc, md):
    def processFeatureClass(self, fclyr, jurs, output_gdb, output_fc, md):
        # select features using non-spatial criteria
        where_clause = None
        # if include_cdc == 'false':
        # potentially not needed due to permissions, but provides extra fallback
        #where_clause = 'CDCJurisdictionID IS NULL'
        # if not where_clause:
        #     where_clause = ''
        # else:
        #     where_clause += ' AND '
        # now uses data provider permissions (handled in cx_* and cxb_* views)
        # if include_restricted == 'false':
        #     if not where_clause:
        #        where_clause = ''
        #     else:
        #         where_clause += ' AND '
        #     where_clause += "Restrictions != 'R'"
        if fclyr == 'ebar_polygons':
            if not where_clause:
                where_clause = ''
            else:
                where_clause += ' AND '
            # these types go to other polygons
            where_clause += "DatasetType NOT IN ('Critical Habitat', 'Range Estimate', 'Habitat Suitability', " + \
                "'Area of Occupancy', 'Other', 'Other Observations', 'Other Range')"
        if fclyr == 'other_polygons' or fclyr == 'bad_other_polygons':
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
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'mindate', 'MinDate', 'Date'))
        field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'maxdate', 'MaxDate', 'Date'))
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
        # field_mappings.addFieldMap(EBARUtils.createFieldMap(fclyr, 'restrictions', 'Restrictions', 'Text'))
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
        #arcpy.CopyFeatures_management(fclyr, output_gdb + '/' + output_fc)
        arcpy.FeatureClassToFeatureClass_conversion(fclyr, output_gdb, output_fc, field_mapping=field_mappings)
        # embed metadata
        fc_md = arcpy.metadata.Metadata(output_gdb + '/' + output_fc)
        fc_md.copy(md)
        fc_md.save()


# controlling process
if __name__ == '__main__':
    eed = ExportECCCDataTool()
    parameters = []
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:/GIS/EBAR/nsc-gis-ebarkba.sde'
    param_jurisdictions_covered = arcpy.Parameter()
    # Canadian, but no YT or NU
    param_jurisdictions_covered.value = "'British Columbia';'Alberta';'Saskatchewan';'Manitoba';'Ontario';'Quebec';'Atlantic Canada';'Northwest Territories'"
    param_output_zip = arcpy.Parameter()
    param_output_zip.value = 'EBAR_ECCCExport_QC.zip'
    parameters = [param_geodatabase, param_jurisdictions_covered, param_output_zip]
    eed.runExportECCCDataTool(parameters, None)
