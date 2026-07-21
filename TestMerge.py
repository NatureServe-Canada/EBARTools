import arcpy


print('TEST begin')
temp_point_buffer = r'C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempPointBuffer202611993629'
temp_line_buffer = r'C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempLineBuffer202611993629'
input_polygon_layer = 'input_polygon_layer'
arcpy.MakeFeatureLayer_management(r'C:\GIS\EBAR\nsc-gis-ebarkba.sde\InputPolygon', input_polygon_layer, '0=1')
temp_all_inputs = r'C:\GIS\EBAR\nsc-gis-ebarkba.sde\TempMerge'
arcpy.env.overwriteOutput = True
# 1. ERROR 002948: The shape type of InputPolygon is not the same as that of previously entered datasets
arcpy.Merge_management([temp_point_buffer, temp_line_buffer, input_polygon_layer], temp_all_inputs,
                        add_source='ADD_SOURCE_INFO')
# # 2. removed temp_line_buffer - succeeds but creates table not polygons
# # 2b. added explicit field_match_mode
# arcpy.Merge_management([temp_point_buffer, input_polygon_layer], temp_all_inputs, add_source='ADD_SOURCE_INFO', field_match_mode='AUTOMATIC')
# # 3. reordered inputs - no error but empty/incorrect results
# arcpy.Merge_management([input_polygon_layer, temp_point_buffer, temp_line_buffer], temp_all_inputs,
#                         add_source='ADD_SOURCE_INFO')
print('TEST end')
