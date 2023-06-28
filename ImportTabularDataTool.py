# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: ImportTabularDataTool.py
# ArcGIS Python tool for importing tabular data into the
# InputDataset and InputPoint tables of the EBAR geodatabase

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


class ImportTabularDataTool:
    """Import point data into the InputDataset and InputPoint tables of the EBAR geodatabase"""
    def __init__(self):
        pass

    def runImportTabularDataTool(self, parameters, messages):
        ## debugging/testing
        #print(locale.getpreferredencoding())
        #print(str(EBARUtils.estimateAccuracy(48.0, 0.0003)))
        #print(str(EBARUtils.estimateAccuracy(48.0, 0.002)))
        #print(str(EBARUtils.estimateAccuracy(48.0, 0.001)))
        #print(str(EBARUtils.estimateAccuracy(80.0, 0.2)))
        #print(str(EBARUtils.estimateAccuracy(40.0, 0.2)))
        #return

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
        param_dataset_name = parameters[2].valueAsText
        param_dataset_source = parameters[3].valueAsText
        param_date_received = parameters[4].valueAsText
        #param_restrictions = parameters[5].valueAsText
        param_sensitivity_restriction_reason = parameters[5].valueAsText

        # check dataset source
        if param_dataset_source not in EBARUtils.readDatasetSources(param_geodatabase, "('T')"):
            EBARUtils.displayMessage(messages, 'ERROR: Dataset Source is not valid')
            return

        # use passed geodatabase as workspace (still seems to go to default geodatabase)
        arcpy.env.workspace = param_geodatabase

        # get table name prefix (needed for joined tables and feature classes in enterprise geodatabases)
        table_name_prefix = EBARUtils.getTableNamePrefix(param_geodatabase)

        # get dataset source id
        with arcpy.da.SearchCursor(param_geodatabase + '/DatasetSource', ['DatasetSourceID'],
                                   "DatasetSourceName = '" + param_dataset_source + "'") as cursor:
            row = None
            for row in EBARUtils.searchCursor(cursor):
                dataset_source_id = row['DatasetSourceID']
            if row:
                del row

        # match field_dict with source
        field_dict = TabularFieldMapping.tabular_field_mapping_dict[param_dataset_source]

        # # encode restriction using domain
        # param_restrictions = EBARUtils.encodeRestriction(param_geodatabase, param_restrictions)

        # check/add InputDataset row
        dataset = param_dataset_name + ', ' + param_dataset_source + ', ' + str(param_date_received)
        EBARUtils.displayMessage(messages, 'Checking for dataset [' + dataset + '] and adding if new')
        input_dataset_id, dataset_exists = EBARUtils.checkAddInputDataset(param_geodatabase,
                                                                          param_dataset_name,
                                                                          dataset_source_id,
                                                                          param_date_received,
                                                                          param_sensitivity_restriction_reason)
                                                                          #param_restrictions)

        # read existing species into dict
        EBARUtils.displayMessage(messages, 'Reading full list of Species and Synonyms')
        species_dict = EBARUtils.readSpecies(param_geodatabase)
        synonym_dict = EBARUtils.readSynonyms(param_geodatabase)
        synonym_species_dict = EBARUtils.readSynonymSpecies(param_geodatabase)

        # read existing unique IDs into dict
        EBARUtils.displayMessage(messages, 'Reading existing Unique IDs for the Dataset Source')
        id_dict = EBARUtils.readDatasetSourceUniqueIDs(param_geodatabase, table_name_prefix, dataset_source_id,
                                                       'Point', False)
        bad_dict = EBARUtils.readDatasetSourceUniqueIDs(param_geodatabase, table_name_prefix, dataset_source_id,
                                                        'Point', True)

        # get bbc domain values
        domains = arcpy.da.ListDomains(param_geodatabase)
        for domain in domains:
            if domain.name == 'BreedingAndBehaviourCode':
                bbc_domain_values = domain.codedValues
                bbc_domain_values_lower = {}
                for bbc_domain_value in bbc_domain_values:
                    bbc_domain_values_lower[bbc_domain_value.lower()] = bbc_domain_values[bbc_domain_value]

        # try to open data file as a csv
        infile = io.open(param_raw_data_file, 'r', encoding='mbcs') # mbcs encoding is Windows ANSI
        reader = csv.DictReader(infile)

        # process all file lines
        EBARUtils.displayMessage(messages, 'Processing file lines')
        count = 0
        no_species_match = 0
        no_match_list = []
        no_coords = 0
        inaccurate = 0
        fossils = 0
        bad_data = 0
        updates = 0
        non_research = 0
        deleted = 0
        private = 0
        individual_count_0 = 0
        bad_bbc = 0
        bad_bbcs_list = []
        bad_date = 0
        try:
            for file_line in reader:
                # check/add point for current line
                input_point_id, status, max_date, bbc_bad = self.CheckAddPoint(id_dict, bad_dict, param_geodatabase,
                                                                               input_dataset_id, species_dict, 
                                                                               synonym_dict, synonym_species_dict,
                                                                               file_line, field_dict, no_match_list,
                                                                               bbc_domain_values_lower, bad_bbcs_list,
                                                                               messages)
                # increment/report counts
                count += 1
                if count % 1000 == 0:
                    EBARUtils.displayMessage(messages, 'Processed ' + str(count))
                if status == 'no_species_match':
                    no_species_match += 1
                elif status == 'no_coords':
                    no_coords += 1
                elif status == 'inaccurate':
                    inaccurate += 1
                elif status == 'fossil':
                    fossils += 1
                elif status == 'bad_data':
                    bad_data += 1
                elif status == 'updated':
                    updates += 1
                elif status == 'non-research':
                    non_research += 1
                elif status == 'deleted':
                    non_research += 1
                    deleted += 1
                elif status == 'private':
                    private += 1
                elif status == 'individual_count_0':
                    individual_count_0 += 1
                if bbc_bad:
                    bad_bbc += 1
                if status in ('new', 'updated') and not max_date:
                    bad_date += 1
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
            EBARUtils.displayMessage(messages, 'Species not matched (rejected) - ' + str(no_species_match))
            EBARUtils.displayMessage(messages, 'No coordinates (rejected) - ' + str(no_coords))
            EBARUtils.displayMessage(messages,
                                     'Accuracy worse than ' + str(EBARUtils.worst_accuracy) +
                                     ' m (rejected) - ' + str(inaccurate))
            EBARUtils.displayMessage(messages, 'Fossils (rejected) - ' + str(fossils))
            EBARUtils.displayMessage(messages, 'Geoprivacy=private (rejected) - ' + str(private))
            EBARUtils.displayMessage(messages, 'IndividualCount=0 (rejected) - ' + str(individual_count_0))
            EBARUtils.displayMessage(messages, 'Non-research (rejected) - ' + str(non_research))
            EBARUtils.displayMessage(messages, 'Non-research (deleted) - ' + str(deleted))
            EBARUtils.displayMessage(messages, 'Bad Data ignored - ' + str(bad_data))
            EBARUtils.displayMessage(messages, 'Duplicates updated - ' + str(updates))
            EBARUtils.displayMessage(messages, 'Imported without bad breeding and behaviour code - ' + str(bad_bbc))
            EBARUtils.displayMessage(messages, 'Imported without date - ' + str(bad_date))
            end_time = datetime.datetime.now()
            EBARUtils.displayMessage(messages, 'End time: ' + str(end_time))
            elapsed_time = end_time - start_time
            EBARUtils.displayMessage(messages, 'Elapsed time: ' + str(elapsed_time))

        infile.close()
        return

    def CheckAddPoint(self, id_dict, bad_dict, geodatabase, input_dataset_id, species_dict, synonym_dict,
                      synonym_species_dict, file_line, field_dict, no_match_list, bbc_domain_values_lower,
                      bad_bbcs_list, messages):
        """If point already exists, check if needs update; otherwise, add"""
        bad_bbc = False
        # check for species
        # ## NT perf debug
        # species_start = datetime.datetime.now()
        if not file_line[field_dict['scientific_name']]:
            if '[None]' not in no_match_list:
                no_match_list.append('[None]')
                EBARUtils.displayMessage(messages,
                                         'WARNING: No match for species [None]')
            return None, 'no_species_match', None, bad_bbc
        if (file_line[field_dict['scientific_name']].lower() not in species_dict and
            file_line[field_dict['scientific_name']].lower() not in synonym_dict):
            if file_line[field_dict['scientific_name']] not in no_match_list:
                no_match_list.append(file_line[field_dict['scientific_name']])
                EBARUtils.displayMessage(messages,
                                         'WARNING: No match for species ' + file_line[field_dict['scientific_name']])
            return None, 'no_species_match', None, bad_bbc
        else:
            synonym_id = None
            if file_line[field_dict['scientific_name']].lower() in species_dict:
                species_id = species_dict[file_line[field_dict['scientific_name']].lower()]
            else:
                species_id = synonym_species_dict[file_line[field_dict['scientific_name']].lower()]
                synonym_id = synonym_dict[file_line[field_dict['scientific_name']].lower()]
        #unique_id_species = str(file_line[field_dict['unique_id']]) + ' - ' + str(species_id)
        unique_id_species = str(file_line[field_dict['unique_id']])
        # ## NT perf debug
        # species_time = datetime.datetime.now() - species_start
        # EBARUtils.displayMessage(messages, 'Species checked: ' + str(species_time))

        # ## NT perf debug
        # ob_geom_accuracy_start = datetime.datetime.now()
        # CoordinatesObscured
        coordinates_obscured = False
        if field_dict['coordinates_obscured']:
            if file_line[field_dict['coordinates_obscured']] in (True, 'TRUE', 'true', 'T', 't', 1):
                coordinates_obscured = True

        # Geometry/Shape
        input_point = None
        output_point = None
        private_coords = False
        if coordinates_obscured:
            # check for private lon/lat
            if field_dict['private_longitude'] and field_dict['private_latitude']:
                if (file_line[field_dict['private_longitude']] not in ('NA', '') and
                    file_line[field_dict['private_latitude']] not in ('NA', '')):
                    private_coords = True
                    coordinates_obscured = False
                    input_point = arcpy.Point(float(file_line[field_dict['private_longitude']]),
                                              float(file_line[field_dict['private_latitude']]))
        if not private_coords:
            if (file_line[field_dict['longitude']] not in ('NA', '') and
                file_line[field_dict['latitude']] not in ('NA', '')):
                input_point = arcpy.Point(float(file_line[field_dict['longitude']]),
                                          float(file_line[field_dict['latitude']]))
        if input_point:
            # assume WGS84 if not provided
            srs = EBARUtils.srs_dict['WGS84']
            if field_dict['srs']:
                # srs provided
                if file_line[field_dict['srs']].lower() not in ('unknown', 'not recorded', 'NA', ''):
                    srs = file_line[field_dict['srs']]
                    if '84' in srs.lower() and 'wgs' in srs.lower():
                        srs = 'WGS84'
                    if '85' in srs.lower() and 'wgs' in srs.lower():
                        srs = 'WGS84'
                    if '87' in srs.lower() and 'wgs' in srs.lower():
                        srs = 'WGS84'
                    elif 'gps' in srs.lower():
                        srs = 'WGS84'
                    elif 'prp_m' in srs.lower():
                        srs = 'WGS84'
                    elif 'nad' in srs.lower() and '83' in srs.lower():
                        srs = 'NAD83'
                    elif 'nad' in srs.lower() and '27' in srs.lower():
                        srs = 'NAD27'
                    elif 'nad' in srs.lower() and '28' in srs.lower():
                        srs = 'NAD27'
                    elif 'ocotepeque' in srs.lower():
                        srs = 'Ocotepeque 1935'
                    srs = EBARUtils.srs_dict[srs]
            input_geometry = arcpy.PointGeometry(input_point, arcpy.SpatialReference(srs))
            output_geometry = input_geometry.projectAs(
                arcpy.SpatialReference(EBARUtils.srs_dict['North America Albers Equal Area Conic']))
            output_point = output_geometry.lastPoint
        if not output_point:
            return None, 'no_coords', None, bad_bbc

        # Accuracy
        accuracy = None
        if (not coordinates_obscured) or private_coords:
            if private_coords:
                if field_dict['private_accuracy']:
                    if file_line[field_dict['private_accuracy']] not in ('NA', ''):
                        accuracy = round(float(file_line[field_dict['private_accuracy']]))
            elif field_dict['accuracy']:
                if file_line[field_dict['accuracy']] not in ('NA', ''):
                    accuracy = round(float(file_line[field_dict['accuracy']]))
            if accuracy:
                if accuracy > EBARUtils.worst_accuracy:
                    return None, 'inaccurate', None, bad_bbc
        else:
            # provided accuracy is not relevant for obscured data, estimate based on 0.2 degree square
            accuracy = EBARUtils.estimateAccuracy(input_point.Y, 0.2)
        # ## NT perf debug
        # ob_geom_accuracy_time = datetime.datetime.now() - ob_geom_accuracy_start
        # EBARUtils.displayMessage(messages, 'Obscured, Geometry, Accuracy: ' + str(ob_geom_accuracy_time))

        # ## NT perf debug
        # date_fossil_grade_start = datetime.datetime.now()
        # MaxDate
        max_date = None
        if field_dict['date']:
            # date field
            max_date = EBARUtils.extractDate(file_line[field_dict['date']])
        if not max_date:
            # separate ymd fields
            if field_dict['year']:
                if file_line[field_dict['year']] not in ('NA', ''):
                    max_year = int(file_line[field_dict['year']])
                    max_month = 1
                    if field_dict['month']:
                        if file_line[field_dict['month']] not in ('NA', ''):
                            max_month = int(file_line[field_dict['month']])
                    max_day = 1
                    if field_dict['day']:
                        if file_line[field_dict['day']] not in ('NA', ''):
                            max_day = int(file_line[field_dict['day']])
                    if max_year >= 1500:
                        if max_month <= 0 or max_month > 12:
                            max_month = 1
                        if max_day <= 0 or max_day > 31:
                            max_day = 1
                        max_date = datetime.datetime(max_year, max_month, max_day)

        # reject fossils records
        if field_dict['basis_of_record']:
            if file_line[field_dict['basis_of_record']].lower() in ('fossil_specimen', 'fossil', 'fossilspecimen'):
                return None, 'fossil', None, bad_bbc

        # grade
        quality_grade = 'research'
        if field_dict['quality_grade']:
            quality_grade = file_line[field_dict['quality_grade']]

        # check for existing bad data with same unique_id within the dataset source
        if unique_id_species in bad_dict:
            return None, 'bad_data', None, bad_bbc

        # check for existing point with same unique_id within the dataset source
        delete = False
        update = False
        if unique_id_species in id_dict:
            # already exists
            if quality_grade.lower() not in ('research', '1', 'true'):
                # delete it because it has been downgraded
                with arcpy.da.UpdateCursor(geodatabase + '/InputPoint',
                                           ['InputPointID', 'InputDatasetID', 'SpeciesID'],
                                           'InputPointID = ' + str(id_dict[unique_id_species])) as cursor:
                                           #"DatasetSourceUniqueID = '" + str(file_line[field_dict['unique_id']]) +
                                           #"' AND InputDatasetID = " + str(input_dataset_id)) as cursor:
                    row = None
                    for row in cursor:
                        cursor.deleteRow()
                    if row:
                        del row
                    return id_dict[unique_id_species], 'deleted', None, bad_bbc
            else:
                update = True
            #if private_coords:
            #    # check if it was previously obscured, and if so update
            #    with arcpy.da.SearchCursor(geodatabase + '/InputPoint', ['CoordinatesObscured'],
            #                               "InputPointID = " + str(id_dict[unique_id_species])) as cursor:
            #        row = None
            #        for row in EBARUtils.searchCursor(cursor):
            #            update = row['CoordinatesObscured']
            #        if row:
            #            del row

            #if not update:
            #    # existing record that does not need to be updated
            #    return id_dict[unique_id_species], 'duplicate', None, bad_bbc

        # don't add non research grade
        if quality_grade.lower() not in ('research', '1', 'true'):
            return None, 'non-research', None, bad_bbc
        # ## NT perf debug
        # date_fossil_grade_time = datetime.datetime.now() - date_fossil_grade_start
        # EBARUtils.displayMessage(messages, 'Date, Fossil, Grade, Uniqueness: ' + str(date_fossil_grade_time))

        # ## NT perf debug
        # other_start = datetime.datetime.now()
        # URI
        uri = None
        if field_dict['uri']:
            uri = file_line[field_dict['uri']]

        # License
        license = None
        if field_dict['license']:
            license = file_line[field_dict['license']]

        # IndividualCount
        individual_count = None
        if field_dict['individual_count']:
            if file_line[field_dict['individual_count']] not in ('NA', 'X', ''):
                individual_count = int(file_line[field_dict['individual_count']])
        if individual_count == 0:
            return None, 'individual_count_0', None, bad_bbc

        # Geoprivacy
        geoprivacy = None
        if field_dict['geoprivacy']:
            geoprivacy = file_line[field_dict['geoprivacy']]
            if geoprivacy == 'private':
                return None, 'private', None, bad_bbc

        # TaxonGeoprivacy
        taxon_geoprivacy = None
        if field_dict['taxon_geoprivacy']:
            taxon_geoprivacy = file_line[field_dict['taxon_geoprivacy']]
        # ## NT perf debug
        # other_time = datetime.datetime.now() - other_start
        # EBARUtils.displayMessage(messages, 'Other Fields: ' + str(other_time))

        # BreedingAndBehaviourCode
        breeding_code = None
        if field_dict['breeding_code']:
            #if file_line[field_dict['breeding_code']] not in ('NA', ''):
            if file_line[field_dict['breeding_code']]:
                if file_line[field_dict['breeding_code']].lower().strip() in bbc_domain_values_lower:
                    breeding_code = file_line[field_dict['breeding_code']].strip()
                else:
                    if file_line[field_dict['breeding_code']] not in bad_bbcs_list:
                        bad_bbcs_list.append(file_line[field_dict['breeding_code']])
                        EBARUtils.displayMessage(messages, 'Warning: Bad Breeding and Behaviour Code ' +
                                                file_line[field_dict['breeding_code']])
                    bad_bbc = True

        # ## NT perf debug
        # save_start = datetime.datetime.now()
        # update or insert
        if update:
            with arcpy.da.UpdateCursor(geodatabase + '/InputPoint',
                                       ['SHAPE@XY', 'InputDatasetID', 'URI', 'License', 'SpeciesID', 'SynonymID',
                                        'MaxDate', 'CoordinatesObscured', 'Accuracy', 'IndividualCount', 'Geoprivacy',
                                        'TaxonGeoprivacy', 'BreedingAndBehaviourCode'],
                                        "InputPointID = " + str(id_dict[unique_id_species])) as cursor:
                row = None
                for row in EBARUtils.updateCursor(cursor):
                    cursor.updateRow([output_point, input_dataset_id, uri, license, species_id, synonym_id, max_date,
                                      coordinates_obscured, accuracy, individual_count, geoprivacy, taxon_geoprivacy,
                                      breeding_code])
                if row:
                    del row
            # ## NT perf debug
            # save_time = datetime.datetime.now() - save_start
            # EBARUtils.displayMessage(messages, 'Save: ' + str(save_time))
            return id_dict[unique_id_species], 'updated', max_date, bad_bbc
        else:
            # insert, set new id and return
            point_fields = ['SHAPE@XY', 'InputDatasetID', 'DatasetSourceUniqueID', 'URI', 'License', 'SpeciesID',
                            'SynonymID', 'MaxDate', 'CoordinatesObscured', 'Accuracy', 'IndividualCount', 'Geoprivacy',
                            'TaxonGeoprivacy', 'BreedingAndBehaviourCode']
            with arcpy.da.InsertCursor(geodatabase + '/InputPoint', point_fields) as cursor:
                object_id = cursor.insertRow([output_point, input_dataset_id,
                                              str(file_line[field_dict['unique_id']]), uri, license, species_id,
                                              synonym_id, max_date, coordinates_obscured, accuracy, individual_count,
                                              geoprivacy, taxon_geoprivacy, breeding_code])
            input_point_id = EBARUtils.getUniqueID(geodatabase + '/InputPoint', 'InputPointID', object_id)
            id_dict[unique_id_species] = input_point_id
            # ## NT perf debug
            # save_time = datetime.datetime.now() - save_start
            # EBARUtils.displayMessage(messages, 'Save: ' + str(save_time))
            return input_point_id, 'new', max_date, bad_bbc


# controlling process
if __name__ == '__main__':
    itd = ImportTabularDataTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:/GIS/EBAR/EBAR-KBA-Dev.gdb'
    param_raw_data_file = arcpy.Parameter()
    param_raw_data_file.value = 'C:/GIS/EBAR/BBA/QC Northern/naturecounts_data_test.csv'
    param_dataset_name = arcpy.Parameter()
    param_dataset_name.value = 'QC Northen BBA Test4'
    param_dataset_source = arcpy.Parameter()
    param_dataset_source.value = 'QC Breeding Bird Atlas'
    param_date_received = arcpy.Parameter()
    param_date_received.value = 'July 20, 2022'
    # param_restrictions = arcpy.Parameter()
    # param_restrictions.value = 'Non-restricted'
    param_sensitivity_restriction_reason = arcpy.Parameter()
    param_sensitivity_restriction_reason.value = 'XProprietary'
    parameters = [param_geodatabase, param_raw_data_file, param_dataset_name, param_dataset_source,
                  param_date_received, param_sensitivity_restriction_reason] # param_restrictions]
    itd.runImportTabularDataTool(parameters, None)
