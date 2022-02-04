# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Gabrielle Miller
# © NatureServe Canada 2022 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: DeleteInputFeedbackTool.py
# ArcGIS Python tool for deleting an existing record from the InputFeedback table

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
from pytest import param
import EBARUtils
import arcpy
import datetime


class DeleteInputFeedbackTool:
    """Delete an existing record from the InputFeedback table"""
    def __init__(self):
        pass

    def runDeleteInputFeedbackTool(self, parameters, messages):
        # check out any needed extension licenses
        #arcpy.CheckOutExtension('Spatial')

        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        param_geodatabase = parameters[0].valueAsText
        param_input_feedback_id = parameters[1].valueAsText

        # check for record
        where_clause = 'InputFeedbackID = ' + str(param_input_feedback_id)
        arcpy.MakeTableView_management(param_geodatabase + '/InputFeedback', 'feedback_view',
                                       where_clause=where_clause)
        result = arcpy.GetCount_management('feedback_view')
        if int(result[0]) == 0:
            EBARUtils.displayMessage(messages, 'ERROR: InputFeedback record with specified ID not found')
            # terminate with error
            return

        # delete
        delete_count = EBARUtils.deleteRows(param_geodatabase + '/InputFeedback', 'if_view', where_clause)
        if delete_count == 0:
            EBARUtils.displayMessage(messages, 'ERROR: InputFeedback record failed unexpectedly')
            # terminate with error
            return
        EBARUtils.displayMessage(messages, str(delete_count) + ' InputFeedback record deleted')
        

        # end time
        end_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'End time: ' + str(end_time))
        elapsed_time = end_time - start_time
        EBARUtils.displayMessage(messages, 'Elapsed time: ' + str(elapsed_time))
        return


# controlling process
if __name__ == '__main__':
    dif = DeleteInputFeedbackTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:/GIS/EBAR/EBAR-KBA-Dev.gdb'
    param_input_feedback_id = arcpy.Parameter()
    param_input_feedback_id.value = 58213
    parameters = [param_geodatabase, param_input_feedback_id]
    dif.runDeleteInputFeedbackTool(parameters, None)
