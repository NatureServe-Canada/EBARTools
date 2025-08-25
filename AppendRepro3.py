import arcpy
#import EBARUtils


#import_features_path = r'C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures202572494110'
import_features_path = r'C:\GIS\EBAR\AppendRepro.gdb\TempImportFeatures202572494110'
arcpy.MakeFeatureLayer_management(import_features_path, 'import_features')
arcpy.SelectLayerByAttribute_management('import_features', where_clause='ignore_imp = 0')

#destination = r'C:\GIS\EBAR\nsc-gis-ebarkba.sde\InputPolygon'
destination = r'C:\GIS\EBAR\AppendRepro.gdb\InputPolygon'

field_mappings = arcpy.FieldMappings()

# these work
#str_mappings = r'InputDatasetID "InputDatasetID" true true false 0 Long 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,InDSID,-1,-1;SpeciesID "SpeciesID" true true false 0 Long 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,SpeciesID,-1,-1;SynonymID "SynonymID" true true false 0 Long 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,SynonymID,-1,-1;MinDate "MinDate" true true false 0 Date 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,MinDate,-1,-1;MaxDate "MaxDate" true true false 0 Date 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,MaxDate,-1,-1;DatasetSourceUniqueID "DatasetSourceUniqueID" true true false 50 Text 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,organization_local_ident,0,49;Accuracy "Accuracy" true true false 8 Long 8 38,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,uncertainty_distance,-1,-1;Subnation "Subnation" true true false 255 Text 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,subnation,0,254;DataSensitivity "DataSensitivity" true true false 255 Text 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,sf_data_sens,0,254;DataSensitivityCat "DataSensitivityCat" true true false 255 Text 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,sf_datasen_cat,0,254;DataQCStatus "DataQCStatus" true true false 255 Text 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,data_qc_status,0,254;MapQCStatus "MapQCStatus" true true false 255 Text 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,map_qc_status,0,254;QCComments "QCComments" true true false 1000 Text 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,qc_com,0,999;EOID "EOID" true true false 8 Long 8 38,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,eo_id,-1,-1;SFID "SFID" true true false 8 Long 8 38,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,source_feature_id,-1,-1;Descriptor "Descriptor" true true false 255 Text 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,source_feature_descriptor,0,254;Locator "Locator" true true false 255 Text 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,source_feature_locator,0,254;MappingComments "MappingComments" true true false 1000 Text 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,mapping_com,0,999;DigitizingComments "DigitizingComments" true true false 1000 Text 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,digitizing_com,0,999;LocUncertaintyType "LocUncertaintyType" true true false 255 Text 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,loc_uncertainty_type,0,254;LocUncertaintyDistCls "LocUncertaintyDistCls" true true false 255 Text 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,loc_uncertainty_distance_cl,0,254;LocUncertaintyDistUnit "LocUncertaintyDistUnit" true true false 255 Text 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,loc_uncertainty_unit,0,254;LocUseClass "LocUseClass" true true false 255 Text 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,location_use_class,0,254;IndependentSF "IndependentSF" true true false 255 Text 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,independent_source_feature_in,0,254;UnsuitableHabExcluded "UnsuitableHabExcluded" true true false 255 Text 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,exclude_unsuitable_habitat,0,254;PartialDate "PartialDate" true true false 0 Text 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,PartialDate,0,254'
#str_mappings = r'InputDatasetID "InputDatasetID" true true false 0 Long 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,InDSID,-1,-1;SpeciesID "SpeciesID" true true false 0 Long 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,SpeciesID,-1,-1;DatasetSourceUniqueID "DatasetSourceUniqueID" true true false 50 Text 0 0,First,#,C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempImportFeatures20257289138,organization_local_ident,0,49'
#field_mappings.loadFromString(str_mappings)

# this one doesn't! no error, just no records appended
field_mappings = arcpy.FieldMappings()
#field_mappings.addFieldMap(EBARUtils.createFieldMap('import_features', 'InDSID', 'InputDatasetID', 'Long'))
field_map = arcpy.FieldMap()
field_map.addInputField('import_features', 'InDSID')
field = field_map.outputField
field.name = 'InputDatasetID'
field.aliasName = 'InputDatasetID'
field.type = 'Long'
field_map.outputField = field
field_mappings.addFieldMap(field_map)
#field_mappings.addFieldMap(EBARUtils.createFieldMap('import_features', 'SpeciesID', 'SpeciesID', 'Long'))
field_map = arcpy.FieldMap()
field_map.addInputField('import_features', 'SpeciesID')
field = field_map.outputField
field.name = 'SpeciesID'
field.aliasName = 'SpeciesID'
field.type = 'Long'
field_map.outputField = field
field_mappings.addFieldMap(field_map)
#field_mappings.addFieldMap(EBARUtils.createFieldMap('import_features', 'organization_local_ident', 'DatasetSourceUniqueID', 'Text'))
field_map = arcpy.FieldMap()
field_map.addInputField('import_features', 'organization_local_ident')
field = field_map.outputField
field.name = 'DatasetSourceUniqueID'
field.aliasName = 'DatasetSourceUniqueID'
field.type = 'Text'
field_map.outputField = field
field_mappings.addFieldMap(field_map)

# this is our workaround
# if you comment this out, we get different incorrect outcomes depending on the destination:
# - if it is an Enterprise gdb, we get no records
# - if it is a File gdb, we get records but with NULL in fields where the source and destination field names don't match
field_mappings.loadFromString(field_mappings.exportToString())

arcpy.Append_management('import_features', destination, 'NO_TEST', field_mappings)
