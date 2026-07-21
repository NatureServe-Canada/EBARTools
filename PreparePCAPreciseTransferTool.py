# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Samantha Stefanoff
# © NatureServe Canada 2026 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: PreparePCAPreciseTransferTool.py
# ArcGIS Python tool for setting InputPoint/Polygon fields used for exporting for transfer to NatureServe
# NSXPro and GeoData Portal for Parks Canada Agency

# Notes:
# - Relies on views in server geodatabase, so not possible to use/debug with local file gdb
# - Modeling after PrepareNSXProTransferTool.py, but slightly simplifed because PCA is always provided precise
# therefore this tool just needs to set the Sensitive flag for ESTH

# import Python packages
import EBARUtils
import arcpy
import datetime


class PreparePCAPreciseTransferTool:
    """Set InputPoint/Polygon fields used for PCA Precise transfer"""
    def __init__(self):
        pass

    def runPreparePCAPreciseTransferTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True

        # make variables for parms
        EBARUtils.displayMessage(messages, 'Processing parameters')
        param_geodatabase = parameters[0].valueAsText

        # get table name prefix (needed for joined tables and feature classes in enterprise geodatabases)
        table_name_prefix = EBARUtils.getTableNamePrefix(param_geodatabase)

        # new mixed approach to improve performance by avoiding so many steps with expensive joins and queries!

        # A. done directly in batch/psql (using batch size of 50K took 2+ days)
        # A1. Reset PCAPreciseTemp, PermitPCAPreciseTransfer, PCAPreciseSensitive, PCAPreciseSensitiveCategory to NULL
        # [not required first time; should probably also be done in batch]
        # A2. Calculate PCAPreciseTemp = 1 WHERE DatasetSource.DatasetType = 'Species Observations' AND
        # DatasetSource.JurisdictionID IS NULL AND
        # (DatasetSource.PermitNSCBiodiversityScience = 'Y' OR DatasetSource.PermitAll = 'Y')
        # [see PCAPreciseWorker.sql and PCAPreciseController.bat at C:\Users\Public\Documents on server
        #  or at OneDrive\EBAR\Requirements\NSX]
		# XA3. Index PCAPreciseTemp [don't bother, not sufficiently selective due to high proportion of a single value]

        # B. Select Layer by Attribute WHERE PCAPreciseTemp = 1 (only points meet filter criteria in March 2026)
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/InputPoint', 'input_lyr', 'PCAPreciseTemp = 1')
        EBARUtils.displayMessage(messages, 'Made Feature Layer for PCAPreciseTemp at ' + str(datetime.datetime.now()))

        # process one prov/terr at a time and check both Cdn and P/T ESTHs
        jur_ids = [1,2,3,4,5,6,7,8,9,10,11,12,18,19]
        for jur_id in jur_ids:
            # C. Select Layer by Location SUBSET intersect JurisdictionBufferFull for Canadian PTs
            arcpy.MakeFeatureLayer_management(param_geodatabase + '/JurisdictionBufferFull', 'jurbuffer_lyr')
            arcpy.SelectLayerByAttribute_management('jurbuffer_lyr', 'NEW_SELECTION', 'JurisdictionID = ' + str(jur_id))
            EBARUtils.displayMessage(messages,
                                     'Jurisdiction ' + str(jur_id) + ' selected at ' + str(datetime.datetime.now()))
            arcpy.SelectLayerByLocation_management('input_lyr', 'INTERSECT', 'jurbuffer_lyr',
                                                   selection_type='NEW_SELECTION')
            point_count = arcpy.GetCount_management('input_lyr')[0]
            EBARUtils.displayMessage(messages, str(point_count) + ' points selected at ' + str(datetime.datetime.now()))

            # D. Calculate PermitPCAPreciseTransfer = 'Y'
            arcpy.CalculateField_management('input_lyr', 'PermitPCAPreciseTransfer', "'Y'", 'PYTHON3')
            EBARUtils.displayMessage(messages, 'PermitPCAPreciseTransfer calculated at ' + str(datetime.datetime.now()))

            # E1. Add Join to InputDataset
            arcpy.AddJoin_management('input_lyr', 'InputDatasetID', param_geodatabase + '/InputDataset', 'InputDatasetID',
                                     'KEEP_COMMON')
            EBARUtils.displayMessage(messages, 'Added Join at ' + str(datetime.datetime.now()))

            # E2. Select Layer by Attribute SUBSET SpeciesID IN (CanadianESTHSpeciesIDs) OR (ProvTerrESTHSpeciesIDs)
            # InputDataset.SensitiveEcologicalDataCat IS NOT NULL
            cdn_esth_species_ids = None
            with arcpy.da.SearchCursor(param_geodatabase + '/CanadianESTHSpeciesIDs', ['SpeciesIDs']) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    cdn_esth_species_ids = row['SpeciesIDs']
            if cdn_esth_species_ids:
                del row
            del cursor
            EBARUtils.displayMessage(messages, 'Retrieved CanadianESTHSpeciesIDs at ' + str(datetime.datetime.now()))
            prov_terr_esth_species_ids = None
            with arcpy.da.SearchCursor(param_geodatabase + '/ProvTerrESTHSpeciesIDs', ['SpeciesIDs'],
                                       'JurisdictionID = ' + str(jur_id)) as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    prov_terr_esth_species_ids = row['SpeciesIDs']
            if prov_terr_esth_species_ids:
                del row
            del cursor
            EBARUtils.displayMessage(messages, 'Retrieved ProvTerrESTHSpeciesIDs at ' + str(datetime.datetime.now()))
            where = table_name_prefix + 'InputPoint.SpeciesID IN (' + cdn_esth_species_ids + ') OR ' + \
                table_name_prefix + 'InputPoint.SpeciesID IN (' + prov_terr_esth_species_ids + ') OR ' + \
                table_name_prefix + 'InputDataset.SensitiveEcologicalDataCat IS NOT NULL'
            arcpy.SelectLayerByAttribute_management('input_lyr', 'SUBSET_SELECTION', where)
            EBARUtils.displayMessage(messages, 'Selected SUBSET Sensitive at ' + str(datetime.datetime.now()))

            # F. Calculate PCAPreciseSensitive = 'Y'
            arcpy.CalculateField_management('input_lyr', table_name_prefix + 'InputPoint.PCAPreciseSensitive', "'Y'",
                                            'PYTHON3')
            EBARUtils.displayMessage(messages, 'PCAPreciseSensitive calculated at ' + str(datetime.datetime.now()))

            # G. Calculate PCAPreciseSensitiveCategory = [Python Code Block]
            code_block = '''
def GetCat(SensitiveEcologicalDataCat):
    ret = 'Fragile Species or Habitat'
    if SensitiveEcologicalDataCat == 'Proprietary':
        ret = 'Proprietary Data'
    elif SensitiveEcologicalDataCat in ('Private Lands', 'Indigenous Lands'):
        ret = 'Land Owner Restrictions'
    return ret'''
            arcpy.CalculateField_management('input_lyr', table_name_prefix + 'InputPoint.PCAPreciseSensitiveCategory',
                                            'GetCat(!' + table_name_prefix + 'InputDataset.SensitiveEcologicalDataCat!)',
                                            'PYTHON3', code_block)
            arcpy.RemoveJoin_management('input_lyr', table_name_prefix + 'InputDataset')
            EBARUtils.displayMessage(messages, 'PCAPreciseSensitiveCategory calculated at ' + str(datetime.datetime.now()))

            arcpy.Delete_management('jurbuffer_lyr')

        arcpy.Delete_management('input_lyr')
        
        # # process points and polygons
        # for spatial_input in ['InputPoint', 'InputPolygon']:
        #     EBARUtils.displayMessage(messages, 'Processing ' + spatial_input)

        #     # record counts
        #     count = 0

        #     # # reset to NULLs in case rules/datasets have changed since last transfer
        #     # EBARUtils.displayMessage(messages, 'Resetting transfer fields')
        #     # # # can't add and remove indexes due to schema lock!
        #     # # arcpy.AddIndex_management(param_geodatabase + '/' + spatial_input, ['PermitPCAPreciseTransfer'],
        #     # #                           'pca_precise_index')
        #     # # arcpy.AddIndex_management(param_geodatabase + '/' + spatial_input, ['PCAPreciseSensitive'],
        #     # #                           'pca_sensitive_index')
        #     # arcpy.MakeTableView_management(param_geodatabase + '/' + spatial_input, 'input_view',
        #     #                                'PermitPCAPreciseTransfer IS NOT NULL OR PCAPreciseSensitive IS NOT NULL')
        #     # # arcpy.RemoveIndex_management(param_geodatabase + '/' + spatial_input, 'pca_precise_index')
        #     # # arcpy.RemoveIndex_management(param_geodatabase + '/' + spatial_input, 'pca_sensitive_index')
        #     # arcpy.CalculateField_management('input_view', 'PermitPCAPreciseTransfer', 'None')
        #     # arcpy.CalculateField_management('input_view', 'PCAPreciseSensitive', 'None')
        #     # arcpy.Delete_management('input_view')

        #     # jurisdiction-level rules are handled by prov/territory, with NF and LB separated
        #     jurs = ['BC', 'AB', 'SK', 'MB', 'ON', 'QC', 'NB', 'PE', 'NS', 'NF', 'LB', 'NU', 'NT', 'YT']

        #     # join ESTH table to jurisdiction
        #     arcpy.MakeTableView_management(param_geodatabase + '/ESTH', 'esth_view')
        #     arcpy.AddJoin_management('esth_view', 'JurisdictionID', param_geodatabase + '/Jurisdiction',
        #                              'JurisdictionID', 'KEEP_COMMON')

        #     # apply elements susceptible to harm (ESTH) rules then permissions
        #     # process rules in three steps, don't overrid previous sensitive
        #     # 1. Canada-wide ESTHs
        #     EBARUtils.displayMessage(messages, 'Applying Canada-wide ESTHs')
        #     row = None
        #     with arcpy.da.SearchCursor('esth_view', [table_name_prefix + 'ESTH.SpeciesID'],
        #                                table_name_prefix + "Jurisdiction.JurisdictionAbbreviation = 'CA' AND (" +
        #                                table_name_prefix + "ESTH.ObscuredForiNatca = 'Y' OR " +
        #                                table_name_prefix + "ESTH.ObscuredForNSC = 'Y')") as cursor:
        #         for row in EBARUtils.searchCursor(cursor):
        #             self.applyJurisdictionSpecies(param_geodatabase, table_name_prefix, spatial_input, jurs,
        #                                           row[table_name_prefix + 'ESTH.SpeciesID'], None,
        #                                           count, messages)
        #     if row:
        #         del row
        #     del cursor

        #     # 2. jurisdiction ESTHs
        #     EBARUtils.displayMessage(messages, 'Applying Jurisdictional ESTHs')
        #     row = None
        #     with arcpy.da.SearchCursor('esth_view', [table_name_prefix + 'ESTH.SpeciesID',
        #                                              table_name_prefix + 'Jurisdiction.JurisdictionAbbreviation'],
        #                                table_name_prefix + "Jurisdiction.JurisdictionAbbreviation <> 'CA' AND ()" +
        #                                table_name_prefix + "ESTH.ObscuredForiNatca = 'Y' OR " +
        #                                table_name_prefix + "ESTH.ObscuredForNSC = 'Y')") as cursor:
        #         for row in EBARUtils.searchCursor(cursor):
        #             self.applyJurisdictionSpecies(param_geodatabase, table_name_prefix, spatial_input,
        #                                           [row[table_name_prefix + 'Jurisdiction.JurisdictionAbbreviation']],
        #                                           row[table_name_prefix + 'ESTH.SpeciesID'], None,
        #                                           count, messages)
        #     if row:
        #         del row
        #     del cursor

        #     arcpy.Delete_management('esth_view')

        #     # 3. EBAR provider permissions
        #     EBARUtils.displayMessage(messages, 'Applying EBAR provider permissions')
        #     row = None
        #     with arcpy.da.SearchCursor(param_geodatabase + '/DatasetSource',
        #                                ['DatasetSourceID'],
        #                                "(PermitNSCBiodiversityScience = 'Y') OR (PermitAll = 'Y')") as cursor:
        #         for row in EBARUtils.searchCursor(cursor):
        #             # get InputDatasetIDs
        #             input_dataset_ids = []
        #             id_row = None
        #             with arcpy.da.SearchCursor(param_geodatabase + '/InputDataset', ['InputDatasetID'],
        #                                        'DatasetSourceID = ' + str(row['DatasetSourceID'])) as id_cursor:
        #                 for id_row in EBARUtils.searchCursor(id_cursor):
        #                     input_dataset_ids.append(id_row['InputDatasetID'])
        #             if id_row:
        #                 del id_row
        #             del id_cursor
        #             if len(input_dataset_ids) > 0:
        #                 self.applyJurisdictionSpecies(param_geodatabase, table_name_prefix, spatial_input, jurs, None,
        #                                               input_dataset_ids, count, messages)
        #     if row:
        #         del row
        #     del cursor

        #     # # index to help export performance
        #     # EBARUtils.displayMessage(messages, 'Indexing')
        #     # arcpy.AddIndex_management(param_geodatabase + '/' + spatial_input, ['PermitPCAPreciseTransfer'],
        #     #                           'pca_precise_index')

        #     # record counts
        #     EBARUtils.displayMessage(messages, spatial_input + ' record count: ' + str(count))

        # export to file geodatabase
        # CONSIDER REQUEST FROM NS TO PREJOIN DATASET SOURCE???
        EBARUtils.displayMessage(messages, 'Exporting to File Geodatabase')
        output_gdb = 'PCAPreciseTransfer' + str(datetime.datetime.now().day) + \
            datetime.datetime.now().strftime('%b') + str(datetime.datetime.now().year)
        arcpy.CreateFileGDB_management(EBARUtils.temp_folder, output_gdb)
        output_gdb_folder = EBARUtils.temp_folder + '/' + output_gdb + '.gdb'
        arcpy.ExportFeatures_conversion(param_geodatabase + '/PCAPreciseInputPoint',
                                        output_gdb_folder + '/PCAPreciseInputPoint')
        # arcpy.ExportFeatures_conversion(param_geodatabase + '/PCAPreciseInputPolygon',
        #                                 output_gdb_folder + '/PCAPreciseInputPolygon')
        arcpy.ExportTable_conversion(param_geodatabase + '/PCAPreciseDatasetSource',
                                     output_gdb_folder + '/PCAPreciseDatasetSource')

        # zip and provide link
        EBARUtils.createZip(output_gdb_folder, EBARUtils.download_folder + '/' + output_gdb + '.zip', None)
        EBARUtils.displayMessage(messages,
                                 'Zipped file geodatabase: ' + EBARUtils.download_url + '/' + output_gdb + '.zip')

        # end time
        end_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'End time: ' + str(end_time))
        elapsed_time = end_time - start_time
        EBARUtils.displayMessage(messages, 'Elapsed time: ' + str(elapsed_time))


    # def applyJurisdictionSpecies(self, param_geodatabase, table_name_prefix, spatial_input, jurs, species_id,
    #                              input_dataset_ids, count, messages):
    #     """apply rules for a single step"""
    #     arcpy.MakeFeatureLayer_management(param_geodatabase + '/'+ spatial_input, 'input_lyr')
    #     arcpy.AddJoin_management('input_lyr', 'InputDatasetID', param_geodatabase + '/InputDataset', 'InputDatasetID',
    #                              'KEEP_COMMON')
    #     arcpy.AddJoin_management('input_lyr', 'DatasetSourceID', param_geodatabase + '/DatasetSource',
    #                              'DatasetSourceID', 'KEEP_COMMON')

    #     # only incude non-CDC data
    #     # species_id is provided for ESTH rules, input_dataset_ids for permissions
    #     if species_id:
    #         EBARUtils.displayMessage(messages, 'Species: ' + str(species_id))
    #         EBARUtils.displayMessage(messages, 'At: ' + str(datetime.datetime.now()))
    #         where = table_name_prefix + spatial_input + '.SpeciesID = ' + str(species_id)
    #     else:
    #         where = table_name_prefix + spatial_input + '.InputDatasetID IN (' + \
    #             ','.join(map(str, input_dataset_ids)) + ')'
    #     where += ' AND ' + table_name_prefix + 'DatasetSource.CDCJurisdictionID IS NULL'
    #     arcpy.SelectLayerByAttribute_management('input_lyr', 'NEW_SELECTION', where)
    #     EBARUtils.displayMessage(messages, 'Select by attribute: ' + str(datetime.datetime.now()))
        
    #     # select by Location interesting jur(s) buffers
    #     arcpy.MakeFeatureLayer_management(param_geodatabase + '/JurisdictionBufferFull', 'jurbuffer_lyr')
    #     arcpy.AddJoin_management('jurbuffer_lyr', 'JurisdictionID', param_geodatabase + '/Jurisdiction',
    #                              'JurisdictionID', 'KEEP_COMMON')
    #     arcpy.SelectLayerByAttribute_management('jurbuffer_lyr', 'NEW_SELECTION',
    #                                             table_name_prefix + 'Jurisdiction.JurisdictionAbbreviation IN (' +
    #                                             "'{0}'".format("','".join(jurs)) + ')')
    #     arcpy.SelectLayerByLocation_management('input_lyr', 'INTERSECT', 'jurbuffer_lyr')
    #     EBARUtils.displayMessage(messages, 'Select by location: ' + str(datetime.datetime.now()))
    #     search_row = None
    #     # set PCAPreciseSensitive to "Y" and set PCAPreciseSensitiveCategory as follows:
    #     # - to "Proprietary Data" if InputDataset.SensitiveEcologicalCat is Proprietary
    #     # - to "Land Owner Restrictions" if InputDataset.SensitiveEcologicalCat is Private Lands or Indigenous Lands
    #     # - to "Fragile Species or Habitat" if InputDataset.SensitiveEcologicalCat is any non-null value other than
    #     #   list above, or if species in iNat.ca or NSC/CDC list of ESTH
    #     # table_name_prefix + input_features + '.' + input_features + 'ID'
    #     with arcpy.da.SearchCursor('input_lyr',
    #                                [table_name_prefix + spatial_input + '.' + spatial_input + 'ID',
    #                                 table_name_prefix + spatial_input + '.PCAPreciseSensitive',
    #                                 table_name_prefix + spatial_input + '.PCAPreciseSensitiveCategory',
    #                                 table_name_prefix + 'InputDataset.SensitiveEcologicalDataCat']) as search_cursor:
    #         for search_row in EBARUtils.searchCursor(search_cursor):
    #             update = False
    #             pca_precise_transfer = None
    #             pca_precise_sensitive = None
    #             pca_precise_sensitive_category = None
    #             if species_id:
    #                 # ESTH rule
    #                 if not search_row[table_name_prefix + spatial_input + '.PCAPreciseSensitive']:
    #                     # not previously set
    #                     update = True
    #                     pca_precise_sensitive = 'Y'
    #                     pca_precise_sensitive_category = 'Fragile Species or Habitat'
    #             else:
    #                 # Permission
    #                 update = True
    #                 pca_precise_transfer = 'Y'
    #                 pca_precise_sensitive = search_row[table_name_prefix + spatial_input + '.PCAPreciseSensitive']
    #                 pca_precise_sensitive_category = search_row[table_name_prefix + spatial_input +
    #                                                             '.PCAPreciseSensitiveCategory']
    #                 if search_row[table_name_prefix + 'InputDataset.SensitiveEcologicalDataCat'] == 'Proprietary':
    #                     pca_precise_sensitive_category = 'Proprietary Data'
    #                 elif search_row[table_name_prefix +
    #                                 'InputDataset.SensitiveEcologicalDataCat'] in ('Private Lands', 'Indigenous Lands'):
    #                     pca_precise_sensitive_category = 'Land Owner Restrictions'
    #                 elif search_row[table_name_prefix + 'InputDataset.SensitiveEcologicalDataCat']:
    #                     pca_precise_sensitive_category = 'Fragile Species or Habitat'
    #             if update:
    #                 update_row = None
    #                 with arcpy.da.UpdateCursor(param_geodatabase + '/' + spatial_input,
    #                                            ['PermitPCAPreciseTransfer',
    #                                             'PCAPreciseSensitive',
    #                                             'PCAPreciseSensitiveCategory'],
    #                                             spatial_input + 'ID = ' +
    #                                             str(search_row[table_name_prefix + spatial_input + '.' + spatial_input
    #                                                            + 'ID'])) as update_cursor:
    #                     for update_row in update_cursor:
    #                         update_cursor.updateRow([pca_precise_transfer, pca_precise_sensitive,
    #                                                  pca_precise_sensitive_category])
    #                         if input_dataset_ids:
    #                             count += 1
    #                 if update_row:
    #                     del update_row
    #                 del update_cursor
    #     if search_row:
    #         del search_row
    #     del search_cursor

    #     arcpy.Delete_management('jurbuffer_lyr')
    #     arcpy.Delete_management('input_lyr')


# controlling process
if __name__ == '__main__':
    pppt = PreparePCAPreciseTransferTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:/GIS/EBAR/nsc-gis-ebarkba.sde' #'C:/GIS/EBAR/NSXProDebug.gdb'
    parameters = [param_geodatabase]
    pppt.runPreparePCAPreciseTransferTool(parameters, None)
