# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: ListElementNationalIDsTool.py
# ArcGIS Python tool for list existing ELEMENT_NATIONAL_ID values

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import arcpy
import EBARUtils


class ListElementNationalIDsTool:
    """List existing ELEMENT_NATIONAL_ID values"""
    def __init__(self):
        pass

    def runListElementNationalIDsTool(self, parameters, messages):
        # make variables for parms
        param_geodatabase = parameters[0].valueAsText
        #param_folder = parameters[1].valueAsText

        # get table name prefix (needed for joined tables and feature classes in enterprise geodatabases)
        table_name_prefix = EBARUtils.getTableNamePrefix(param_geodatabase)

        # join to allow selecting on ActiveEBAR flag
        arcpy.MakeTableView_management(param_geodatabase + '/BIOTICS_ELEMENT_NATIONAL', 'biotics_view')
        arcpy.AddJoin_management('biotics_view', 'SpeciesID', param_geodatabase + '/Species', 'SpeciesID',
                                 'KEEP_COMMON')

        # process active rows
        with arcpy.da.SearchCursor('biotics_view',
                                   [table_name_prefix + 'BIOTICS_ELEMENT_NATIONAL.ELEMENT_NATIONAL_ID'],
                                   table_name_prefix + 'Species.ActiveEBAR = 1') as cursor:
            IDs = []
            count = 0
            row = None
            for row in EBARUtils.searchCursor(cursor):
                IDs.append(row[table_name_prefix + 'BIOTICS_ELEMENT_NATIONAL.ELEMENT_NATIONAL_ID'])
                count += 1
                if count % 1000 == 0:
                    EBARUtils.displayMessage(messages, str(count) + ':')
                    EBARUtils.displayMessage(messages, ','.join(map(str, IDs)))
                    IDs = []
            if row:
                del row
            EBARUtils.displayMessage(messages, str(count) + ':')
            EBARUtils.displayMessage(messages, ','.join(map(str, IDs)))
            EBARUtils.displayMessage(messages, 'Listed ' + str(count) + ' ELEMENT_NATIONAL_ID values')
        return


# controlling process
if __name__ == '__main__':
    leni = ListElementNationalIDsTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value='D:/GIS/EBAR/EBAR-KBA-Dev.gdb'
    #param_folder = arcpy.Parameter()
    #param_folder.value='C:/GIS/EBAR'
    parameters = [param_geodatabase]
    leni.runListElementNationalIDsTool(parameters, None)
