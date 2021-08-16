import arcpy


# controlling process
if __name__ == '__main__':
    arcpy.AddMessage('TEST0')

    with arcpy.da.InsertCursor('C:/GIS/EBAR/EBAR-KBA-Dev.gdb/RangeMapEcoshape',
                               ['RangeMapID', 'EcoshapeID', 'Presence']) as insert_cursor:
        insert_cursor.insertRow([80, 1000, 'P'])
        arcpy.AddMessage('TEST1')
    del insert_cursor
        
    with arcpy.da.UpdateCursor('C:/GIS/EBAR/EBAR-KBA-Dev.gdb/RangeMapEcoshape',
                               ['EcoshapeID'], 'RangeMapID = 80 AND EcoshapeID = 1000') as update_cursor:
        for update_row in update_cursor:
            update_cursor.deleteRow()
            arcpy.AddMessage('TEST2')
    del update_cursor
