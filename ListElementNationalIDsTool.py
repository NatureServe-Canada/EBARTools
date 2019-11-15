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

    def RunListElementNationalIDsTool(self, parameters, messages):
        param_geodatabase = parameters[0].valueAsText
        param_folder = parameters[1].valueAsText
        with arcpy.da.SearchCursor(param_geodatabase + '/BIOTICS_ELEMENT_NATIONAL', ['ELEMENT_NATIONAL_ID']) as cursor:
            IDs = []
            count = 0
            for row in EBARUtils.searchCursor(cursor):
                IDs.append(row['ELEMENT_NATIONAL_ID'])
                count += 1
                if count % 1000 == 0:
                    text_file = open(param_folder + '/ELEMENT_NATIONAL_IDs' + str(count) + '.txt', 'w')
                    text_file.write(','.join(map(str, IDs)))
                    text_file.close()
                    IDs = []
            del row
            text_file = open(param_folder + '/ELEMENT_NATIONAL_IDs' + str(count) + '.txt', 'w')
            text_file.write(','.join(map(str, IDs)))
            text_file.close()
            EBARUtils.displayMessage(messages, 'Listed ' + str(count) + ' ELEMENT_NATIONAL_ID values')
        return


# controlling process
if __name__ == '__main__':
    leni = ListElementNationalIDsTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value='C:/GIS/EBAR/EBAR_test.gdb'
    param_folder = arcpy.Parameter()
    param_folder.value='C:/GIS/EBAR'
    parameters = [param_geodatabase, param_folder]
    leni.RunListElementNationalIDsTool(parameters, None)
