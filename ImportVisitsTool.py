# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: ImportVisitsTool.py
# ArcGIS Python tool for importing visits into the EBAR geodatabase and relating them to the appropriate
# InputPoint/Line/Polygon based on SFID and Subnation

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import sys
import traceback
import arcpy
import io
import csv
import datetime
import locale
import EBARUtils
import TabularFieldMapping


class ImportVisitsTool:
    """Import point data into the InputDataset and InputPoint tables of the EBAR geodatabase"""
    def __init__(self):
        pass

    def runImportVisitsTool(self, parameters, messages):
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
        param_raw_data_file = parameters[1].valueAsText
        param_subnation = parameters[2].valueAsText

        # use passed geodatabase as workspace (still seems to go to default geodatabase)
        arcpy.env.workspace = param_geodatabase

        # get table name prefix (needed for joined tables and feature classes in enterprise geodatabases)
        table_name_prefix = EBARUtils.getTableNamePrefix(param_geodatabase)

        # convert subnation to code
        if len(param_subnation) > 2:
            param_subnation = EBARUtils.getJurisidictionAbbreviation(param_geodatabase, param_subnation)
        
        # try to open data file as a csv
        infile = io.open(param_raw_data_file, 'r', encoding='mbcs') # mbcs encoding is Windows ANSI
        reader = csv.DictReader(infile)

        # process all file lines
        EBARUtils.displayMessage(messages, 'Processing file lines')
        count = 0
        sf_missings = 0
        duplicates = 0
        date_missings = 0
        id_missings = 0
        max_date_updates = 0
        min_date_updates = 0
        try:
            for file_line in reader:
                # check/add visit for current line
                sf_missing, duplicate, date_missing, id_missing, max_date_update, min_date_update = \
                    self.CheckAddVisit(param_geodatabase, file_line, param_subnation)
                # increment/report counts
                count += 1
                if count % 100 == 0:
                    EBARUtils.displayMessage(messages, 'Processed ' + str(count))
                if sf_missing:
                    sf_missings += 1
                if duplicate:
                    duplicates += 1
                if date_missing:
                    date_missings += 1
                if id_missing:
                    id_missings += 1
                if max_date_update:
                    max_date_updates += 1
                if min_date_update:
                    min_date_updates += 1
        except:
            # output error messages in exception so that summary of processing thus far gets displayed in finally
            EBARUtils.displayMessage(messages, '\nERROR processing file row ' + str(count + 1))
            tb = sys.exc_info()[2]
            tbinfo = ''
            for tbitem in traceback.format_tb(tb):
                tbinfo += tbitem
            pymsgs = 'Python ERROR:\nTraceback info:\n' + tbinfo + 'Error Info:\n' + str(sys.exc_info()[1])
            EBARUtils.displayMessage(messages, pymsgs)
            arcmsgs = 'ArcPy ERROR:\n' + arcpy.GetMessages(2)
            EBARUtils.displayMessage(messages, arcmsgs)
            EBARUtils.displayMessage(messages, '')

        finally:
            # summary and end time
            EBARUtils.displayMessage(messages, 'Summary:')
            EBARUtils.displayMessage(messages, 'Processed - ' + str(count))
            EBARUtils.displayMessage(messages, 'Missing SFID ignored - ' + str(sf_missings))
            EBARUtils.displayMessage(messages, 'Duplicate ignored - ' + str(duplicates))
            EBARUtils.displayMessage(messages, 'Imported without VisitDate - ' + str(date_missings))
            EBARUtils.displayMessage(messages, 'Imported without InputPoint/Line/PolygonID - ' + str(id_missings))
            EBARUtils.displayMessage(messages, 'InputPoint/Line/Polygon MaxDate updated - ' + str(max_date_updates))
            EBARUtils.displayMessage(messages, 'InputPoint/Line/Polygon MinDate updated - ' + str(min_date_updates))
            end_time = datetime.datetime.now()
            EBARUtils.displayMessage(messages, 'End time: ' + str(end_time))
            elapsed_time = end_time - start_time
            EBARUtils.displayMessage(messages, 'Elapsed time: ' + str(elapsed_time))

        infile.close()
        return

    def CheckAddVisit(self, geodatabase, file_line, subnation):
        """Add visit if it doesn't already exist and related feature dates if needed"""

        # return flag defaults
        duplicate = False
        date_missing = False
        id_missing = True
        max_date_update = False
        min_date_update = False

        # read from file_line (fields must match exactly in input - no mapping mechanism)
        sf_id = file_line['SOURCE_FEATURE_ID']
        if not sf_id:
            return True, duplicate, date_missing, id_missing, max_date_update, min_date_update
        visit_date = EBARUtils.extractDate(file_line['VISIT_DATE'])
        if not visit_date:
            date_missing = True
        visit_notes = file_line['VISIT_NOTES']
        visited_by = file_line['VISITED_BY']
        detected = file_line['DETECTED_IND']

        # check for duplicate visit
        if sf_id:
            where_clause = 'SFID = ' + str(sf_id) + " AND Subnation = '" + subnation + "'"
            if visit_date:
                where_clause += " AND VisitDate = date '" + visit_date.strftime('%Y-%m-%d') + "'"
            if visit_notes:
                visit_notes = visit_notes.replace("'", '')
                where_clause += " AND VisitNotes = '" + visit_notes.replace("'", "''") + "'"
            if visited_by:
                visited_by = visited_by.replace("'", '')
                where_clause += " AND VisitedBy = '" + visited_by + "'"
            with arcpy.da.SearchCursor(geodatabase + '/Visit', ['VisitedBy'], where_clause) as cursor:
                row = None
                for row in EBARUtils.searchCursor(cursor):
                    # existing - skip
                    duplicate = True
                if row:
                    del row

        # check InputPoint/Line/Polygon with same sf_id and subnation for dates and get ID
        input_point_id = None
        input_line_id = None
        input_polygon_id = None
        for input_table in ('/InputPoint', '/InputLine', '/InputPolygon'):
            fields = ['MaxDate', 'MinDate']
            if input_table == '/InputPoint':
                fields.append('InputPointID')
            elif input_table == '/InputLine':
                fields.append('InputLineID')
            elif input_table == '/InputPolygon':
                fields.append('InputPolygonID')
            with arcpy.da.UpdateCursor(geodatabase + input_table, fields,
                                        'SFID = ' + str(sf_id) + " AND Subnation = '" + subnation + "'") as cursor:
                row = None
                for row in EBARUtils.updateCursor(cursor):
                    id_missing = False
                    # get ID
                    if input_table == '/InputPoint':
                        input_point_id = row['InputPointID']
                    elif input_table == '/InputLine':
                        input_line_id = row['InputLineID']
                    elif input_table == '/InputPolygon':
                        input_polygon_id = row['InputPolygonID']
                    # check dates
                    if visit_date:
                        max_date = row['MaxDate']
                        min_date = row['MinDate']
                        # only update max_date if visit_date is greater
                        if not max_date or visit_date > max_date:
                            max_date_update = True
                            max_date = visit_date
                        # only update min_date if visit_date is less, and different than max_date
                        if not min_date or visit_date < min_date:
                            if visit_date < max_date:
                                min_date_update = True
                                min_date = visit_date
                        if max_date_update or min_date_update:
                            values = [max_date, min_date]
                            if input_table == '/InputPoint':
                                values.append(input_point_id)
                            elif input_table == '/InputLine':
                                values.append(input_line_id)
                            elif input_table == '/InputPolygon':
                                values.append(input_polygon_id)
                            cursor.updateRow(values)
                if row:
                    del row

        if not duplicate:
            # add
            with arcpy.da.InsertCursor(geodatabase + '/Visit', ['SFID', 'Subnation', 'VisitDate', 'VisitNotes',
                                                                'VisitedBy', 'Detected', 'InputPointId',
                                                                'InputLineID', 'InputPolygonID']) as cursor:
                object_id = cursor.insertRow([sf_id, subnation, visit_date, visit_notes, visited_by, detected,
                                              input_point_id, input_line_id, input_polygon_id])

        return False, duplicate, date_missing, id_missing, max_date_update, min_date_update


# controlling process
if __name__ == '__main__':
    iv = ImportVisitsTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:/GIS/EBAR/EBAR-KBA-Dev.gdb'
    param_raw_data_file = arcpy.Parameter()
    param_raw_data_file.value = 'C:/Users/rgree/OneDrive/EBAR_Sensitive_Material/CDN_CDC_Data/Saskatchewan/DataCut_2022/Visits/rgreene_1658852892837.csv'
    param_subnation = arcpy.Parameter()
    param_subnation.value = 'SK'
    parameters = [param_geodatabase, param_raw_data_file, param_subnation]
    iv.runImportVisitsTool(parameters, None)
