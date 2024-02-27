import arcpy
import EBARUtils


# controlling process
if __name__ == '__main__':
    # overwrite
    arcpy.env.overwriteOutput = True

    # load all EBAR species
    species_dict = EBARUtils.readSpecies('C:/GIS/EBAR/Default.gdb')
    EBARUtils.displayMessage(None, 'Species list loaded')

    # make layer for grid squares
    arcpy.MakeFeatureLayer_management('C:/GIS/EBAR/Birds Canada/National_Atlas_Squares.gdb/NationalSquares_FINAL',
                                      'grid_squares')

    # loop Nature Counts species
    with arcpy.da.SearchCursor('C:/GIS/EBAR/Default.gdb/NatureCountsforEBAR_species', ['speciesName'], #) as spec_cursor:
                               "speciesName in ('Luscinia svecica', 'Columba livia')") as spec_cursor:
        spec_fcs = []
        index = 374
        # first = True
        for spec_row in EBARUtils.searchCursor(spec_cursor):
            index += 1
            # if spec_row['speciesName'].lower() not in species_dict.keys():
            #     EBARUtils.displayMessage(None, 'Missing ' + spec_row['speciesName'])
            # else:
            EBARUtils.displayMessage(None, 'Found ' + spec_row['speciesName'])
            # get Nature Counts records and save to temp
            arcpy.MakeTableView_management(
                'C:/GIS/EBAR/Birds Canada/NatureCountsData_forRandal.gdb/NatureCountsforEBAR_ExportTable',
                'nc_records', "speciesName = '" + spec_row['speciesName'] + "'")
            #result = arcpy.GetCount_management('nc_records')
            #EBARUtils.displayMessage(None, 'nc_records count ' + result[0])
            arcpy.CopyRows_management('nc_records', 'C:/GIS/EBAR/Default.gdb/nc_temp')

            # join to grid squares and save to temp
            arcpy.AddJoin_management('grid_squares', 'SQUARE_ID_ext', 'C:/GIS/EBAR/Default.gdb/nc_temp',
                                        'utm_square', 'KEEP_COMMON')
            #result = arcpy.GetCount_management('grid_squares')
            #EBARUtils.displayMessage(None, 'grid_squares count ' + result[0])
            arcpy.CopyFeatures_management('grid_squares',
                                            'C:/GIS/EBAR/Default.gdb/nc_temp_' + str(index))
            spec_fcs.append('C:/GIS/EBAR/Default.gdb/nc_temp_' + str(index))

            # # append to output
            # # if first:
            # #     arcpy.CopyFeatures_management(
            # #         'grid_squares',
            # #         'C:/GIS/EBAR/Birds Canada/NatureCountsData_forRandal.gdb/NatureCountsforEBAR_Polygons')
            # #     first = False
            # #     #EBARUtils.displayMessage(None, 'Created ' + spec_row['speciesName'])
            # # else:
            # field_mappings = arcpy.FieldMappings()
            # field_mappings.addFieldMap(
            #     EBARUtils.createFieldMap('grid_squares', 'NationalSquares_FINAL.SQUARE_ID_ext', 'SQUARE_ID_ext',
            #                              'TEXT'))
            # field_mappings.addFieldMap(
            #     EBARUtils.createFieldMap('grid_squares', 'nc_temp.min_year', 'min_year', 'LONG'))
            # field_mappings.addFieldMap(
            #     EBARUtils.createFieldMap('grid_squares', 'nc_temp.max_year', 'max_year', 'LONG'))
            # field_mappings.addFieldMap(
            #     EBARUtils.createFieldMap('grid_squares', 'nc_temp.breeding_code', 'breeding_code', 'TEXT'))
            # field_mappings.addFieldMap(
            #     EBARUtils.createFieldMap('grid_squares', 'nc_temp.speciesName', 'speciesName', 'TEXT'))
            # EBARUtils.displayMessage(None, field_mappings.exportToString())
            # arcpy.Append_management(
            #     'grid_squares',
            #     'C:/GIS/EBAR/Birds Canada/NatureCountsData_forRandal.gdb/NatureCountsforEBAR_ExportPolygons',
            #     'NO_TEST', field_mappings)
            # #EBARUtils.displayMessage(None, 'Appended ' + spec_row['speciesName'])

            # clean up
            arcpy.RemoveJoin_management('grid_squares', 'nc_temp')
            arcpy.Delete_management('nc_records')
        if index > 0:
            del spec_row
    del spec_cursor

    # # merge to output
    # arcpy.Merge_management(
    #     spec_fcs, 'C:/GIS/EBAR/Birds Canada/NatureCountsData_forRandal.gdb/NatureCountsforEBAR_ExportPolygons')
