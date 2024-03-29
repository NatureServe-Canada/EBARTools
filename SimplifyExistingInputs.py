# encoding: utf-8
# simplify polygons in batches

import arcpy
import datetime


# controlling process
if __name__ == '__main__':
    # settings
    arcpy.env.overwriteOutput = True

    # parameters
    folder = 'C:/GIS/EBAR/'
    input_gdb = folder + 'EBAR4.gdb/'
    input_fc = 'RangeMapInputCopy'
    output_name = 'EBAR4.gdb'
    output_gdb = folder + output_name
    min_objectid = 0
    max_objectid = 10000
    batch_size = 10000
    min_accuracy = 1
    max_accuracy = 5
    tolerance = '0.1'

    # create output gdb
    if not arcpy.Exists(output_gdb):
        arcpy.CreateFileGDB_management(folder, output_name)

    # layer to allow selections
    arcpy.MakeFeatureLayer_management(input_gdb + input_fc, 'rmi_lyr')
    current_min = min_objectid
    # batch loop
    print(datetime.datetime.now())
    while current_min < max_objectid:
        print(current_min)
        # selection for current batch
        arcpy.SelectLayerByAttribute_management('rmi_lyr', 'NEW_SELECTION',
                                                'objectid >= ' + str(current_min) +
                                                ' AND objectid < ' + str(current_min + batch_size) +
                                                ' AND Accuracy >= ' + str(min_accuracy) +
                                                ' AND Accuracy < ' + str(max_accuracy) +
                                                " AND OriginalGeometryType = 'P'")
        # default to 10 meter accuracy (1 meter toloerance) if not provided
        if tolerance == '1 meters':
            arcpy.SelectLayerByAttribute_management('rmi_lyr', 'ADD_TO_SELECTION',
                                                    'objectid >= ' + str(current_min) +
                                                    ' AND objectid < ' + str(current_min + batch_size) +
                                                    ' AND Accuracy IS NULL'
                                                    " AND OriginalGeometryType = 'P'")
            arcpy.SelectLayerByAttribute_management('rmi_lyr', 'ADD_TO_SELECTION',
                                                    'objectid >= ' + str(current_min) +
                                                    ' AND objectid < ' + str(current_min + batch_size) +
                                                    ' AND Accuracy <= 0'
                                                    " AND OriginalGeometryType = 'P'")
        result = arcpy.GetCount_management('rmi_lyr')
        print(result[0])
        if int(result[0]) > 0:
            arcpy.SimplifyPolygon_cartography('rmi_lyr', output_gdb + '/' + input_fc + str(current_min), 'POINT_REMOVE',
                                            tolerance, collapsed_point_option='NO_KEEP', error_option='RESOLVE_ERRORS')
        print(datetime.datetime.now())
        current_min += batch_size

    # input = 'C:\GIS\EBAR\EBAR-KBA-Dev.gdb\RangeMapInput'
    # temp = 'C:\GIS\EBAR\EBAR-KBA-Dev.gdb\TempRangeMapInputX'
    # output = 'C:\GIS\EBAR\EBAR-KBA-Dev.gdb\TempRangeMapInput'
    # # input = 'C:/GIS/EBAR/nsc-gis-ebarkba.sde/RangeMapInput'
    # # temp = 'C:/GIS/EBAR/EBAR4.gdb/TempRangeMapInput'
    # # output = 'C:/GIS/EBAR/nsc-gis-ebarkba.sde/TestRangeMapInputY'
    # # arcpy.env.workspace = 'C:/GIS/EBAR/EBAR4.gdb'
    # # arcpy.env.scratchWorkspace = 'C:/GIS/EBAR/EBAR4.gdb'

    # arcpy.MakeFeatureLayer_management(input, 'rmi_lyr') #, 'OBJECTID > 1281') #, "OriginalGeometryType NOT IN ('Y')")
    # with arcpy.da.SearchCursor('rmi_lyr', ['OBJECTID', 'Accuracy', 'OriginalGeometryType'], sql_clause=(None,'ORDER BY OBJECTID')) as search_cursor:
    #     for row in search_cursor:
    #         print(row[0])
    #         arcpy.SelectLayerByAttribute_management('rmi_lyr', 'NEW_SELECTION', 'OBJECTID = ' + str(row[0]))
    #         if row[2] == 'P':
    #             # simplify
    #             accuracy = 10
    #             if row[1]:
    #                 if row[1] > 0:
    #                     accuracy = row[1]
    #             tolerance = '100 Meters'
    #             if accuracy < 500:
    #                 tolerance = '10 Meters'
    #             if accuracy < 50:
    #                 tolerance = '1 Meters'
    #             if accuracy < 5:
    #                 tolerance = '10 Centimeters'
    #             arcpy.SimplifyPolygon_cartography('rmi_lyr', temp, 'POINT_REMOVE', tolerance, collapsed_point_option='NO_KEEP')
    #             arcpy.AddGlobalIDs_management(temp)
    #             # append simplified
    #             field_mapping = 'GlobalID "GlobalID" false false true 38 GlobalID 0 0,First,#,' + temp + \
    #                 ',GlobalID,-1,-1;RangeMapID "RangeMapID" true true false 4 Long 0 0,First,#,' + temp + \
    #                 ',RangeMapID,-1,-1;DatasetSourceName "DatasetSourceName" true true false 255 Text 0 0,First,#,' + temp + \
    #                 ',DatasetSourceName,0,255;DatasetType "DatasetType" true true false 255 Text 0 0,First,#,' + temp + \
    #                 ',DatasetType,0,255;Accuracy "Accuracy" true true false 4 Long 0 0,First,#,' + temp + \
    #                 ',Accuracy,-1,-1;MaxDate "MaxDate" true true false 8 Date 0 0,First,#,' + temp + \
    #                 ',MaxDate,-1,-1;CoordinatesObscured "CoordinatesObscured" true true false 2 Short 0 0,First,#,' + temp + \
    #                 ',CoordinatesObscured,-1,-1;OriginalGeometryType "OriginalGeometryType" true true false 1 Text 0 0,First,#,' + temp + \
    #                 ',OriginalGeometryType,0,1;NationalScientificName "NationalScientificName" true true false 255 Text 0 0,First,#,' + temp + \
    #                 ',NationalScientificName,0,255;SynonymName "SynonymName" true true false 255 Text 0 0,First,#,' + temp + \
    #                 ',SynonymName,0,255;URI "URI" true true false 1000 Text 0 0,First,#,' + temp + \
    #                 ',URI,0,1000;EORank "EORank" true true false 2 Text 0 0,First,#,' + temp + \
    #                 ',EORank,0,2;DatasetSourceUniqueID "DatasetSourceUniqueID" true true false 255 Text 0 0,First,#,' + temp + \
    #                 ',DatasetSourceUniqueID,0,255'
    #             arcpy.Append_management(temp, output, 'NO_TEST', field_mapping)
    #         else:
    #             # append original
    #             arcpy.Append_management('rmi_lyr', output, 'TEST')
