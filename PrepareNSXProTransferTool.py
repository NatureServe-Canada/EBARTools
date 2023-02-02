# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Samantha Stefanoff
# © NatureServe Canada 2023 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: PrepareNSXProTransferTool.py
# ArcGIS Python tool for setting InputPoint/Polygon fields used by the NSXProTransfer service
# Restricted records

# Notes:
# - Relies on views in server geodatabase, so not possible to use/debug with local file gdb

# import Python packages
import EBARUtils
import arcpy
import datetime


class PrepareNSXProTransferTool:
    """Set InputPoint/Polygon fields used by the NSXProTransfer service"""
    def __init__(self):
        pass

    def runPrepareNSXProTransferTool(self, parameters, messages):
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

        # process points and polygons
        for spatial_input in ('InputPoint', 'InputPolygon'):
            EBARUtils.displayMessage(messages, 'Processing ' + spatial_input)
            # apply species susceptible to persecution and harm (STPH) exclusions then dataset inclusions
            # reset to NULLs in case rules/datasets have changed since last transfer
            EBARUtils.displayMessage(messages, 'Resetting transfer fields')
            arcpy.MakeTableView_management(param_geodatabase + '/' + spatial_input, 'input_view',
                                           'NSXProTransfer IS NOT NULL OR AllowedPrecisionSquareMiles IS NOT NULL')
            arcpy.CalculateField_management('input_view', 'NSXProTransfer', 'None')
            arcpy.CalculateField_management('input_view', 'AllowedPrecisionSquareMiles', 'None')
            arcpy.Delete_management('input_view')

            # jurisdiction-level rules are handled by prov/territory, with NF and LB separated
            jurs = ['BC', 'AB', 'SK', 'MB', 'ON', 'NB', 'PE', 'NS', 'NF', 'LB', 'NU', 'NT', 'YT']

            # join STPH table to jurisdiction
            arcpy.MakeTableView_management(param_geodatabase + '/SpeciesSTPH', 'stph_view')
            arcpy.AddJoin_management('stph_view', 'JurisdictionID', param_geodatabase + '/Jurisdiction',
                                     'JurisdictionID', 'KEEP_COMMON')

            # process rules in five steps, keep coarsest of all rules and don't overrid previous exclude
            # 1. iNaturalist.ca Canada-wide STPHs
            EBARUtils.displayMessage(messages, 'Applying iNaturalist.ca Canada-wide STPHs')
            row = None
            with arcpy.da.SearchCursor('stph_view', [table_name_prefix + 'SpeciesSTPH.SpeciesID',
                                                     table_name_prefix + 'SpeciesSTPH.AllowedPrecisionSquareMiles'],
                                       table_name_prefix + "Jurisdiction.JurisdictionAbbreviation = 'CA' AND " +
                                       table_name_prefix + "SpeciesSTPH.ObscuredForiNatca = 'Y'") as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    self.applyJurisdictionSpecies(param_geodatabase, table_name_prefix, spatial_input, jurs,
                                                  row[table_name_prefix + 'SpeciesSTPH.SpeciesID'], None,
                                                  row[table_name_prefix + 'SpeciesSTPH.AllowedPrecisionSquareMiles'])
            if row:
                del row
            del cursor

            # 2. iNaturalist.ca by jurisdiction STPHs
            EBARUtils.displayMessage(messages, 'Applying iNaturalist.ca by jurisdiction STPHs')
            row = None
            with arcpy.da.SearchCursor('stph_view', [table_name_prefix + 'SpeciesSTPH.SpeciesID',
                                                     table_name_prefix + 'SpeciesSTPH.AllowedPrecisionSquareMiles'],
                                       table_name_prefix + "Jurisdiction.JurisdictionAbbreviation <> 'CA' AND " +
                                       table_name_prefix + "SpeciesSTPH.ObscuredForiNatca = 'Y'") as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    self.applyJurisdictionSpecies(param_geodatabase, table_name_prefix, spatial_input,
                                                  [row[table_name_prefix + 'Jurisdiction.JurisdictionAbbreviation']],
                                                  row[table_name_prefix + 'SpeciesSTPH.SpeciesID'], None,
                                                  row[table_name_prefix + 'SpeciesSTPH.AllowedPrecisionSquareMiles'])
            if row:
                del row
            del cursor

            # 3. NSC/CDC Canada-wide STPHs
            EBARUtils.displayMessage(messages, 'Applying NSC/CDC Canada-wide STPHs')
            row = None
            with arcpy.da.SearchCursor('stph_view', [table_name_prefix + 'SpeciesSTPH.SpeciesID',
                                                     table_name_prefix + 'SpeciesSTPH.AllowedPrecisionSquareMiles'],
                                       table_name_prefix + "Jurisdiction.JurisdictionAbbreviation = 'CA' AND " +
                                       table_name_prefix + "SpeciesSTPH.ObscuredForNSC = 'Y'") as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    self.applyJurisdictionSpecies(param_geodatabase, table_name_prefix, spatial_input, jurs,
                                                  row[table_name_prefix + 'SpeciesSTPH.SpeciesID'], None,
                                                  row[table_name_prefix + 'SpeciesSTPH.AllowedPrecisionSquareMiles'])
            if row:
                del row
            del cursor

            # 4. NSC/CDC by jurisdiction STPHs
            EBARUtils.displayMessage(messages, 'Applying NSC/CDC by jurisdiction STPHs')
            row = None
            with arcpy.da.SearchCursor('stph_view', [table_name_prefix + 'SpeciesSTPH.SpeciesID',
                                                     table_name_prefix + 'SpeciesSTPH.AllowedPrecisionSquareMiles',
                                                     table_name_prefix + 'Jurisdiction.JurisdictionAbbreviation'],
                                       table_name_prefix + "Jurisdiction.JurisdictionAbbreviation <> 'CA' AND " +
                                       table_name_prefix + "SpeciesSTPH.ObscuredForNSC = 'Y'") as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    self.applyJurisdictionSpecies(param_geodatabase, table_name_prefix, spatial_input,
                                                  [row[table_name_prefix + 'Jurisdiction.JurisdictionAbbreviation']],
                                                  row[table_name_prefix + 'SpeciesSTPH.SpeciesID'], None,
                                                  row[table_name_prefix + 'SpeciesSTPH.AllowedPrecisionSquareMiles'])
            if row:
                del row
            del cursor

            arcpy.Delete_management('stph_view')

            # 5. EBAR provider permissions
            EBARUtils.displayMessage(messages, 'Applying EBAR provider permissions')
            input_dataset_ids = []
            row = None
            with arcpy.da.SearchCursor(param_geodatabase + '/DatasetSource',
                                       ['DatasetSourceID', 'AllowedPrecisionSquareMiles'],
                                       "NSXProTransfer='Y'") as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    # get InputDatasetIDs
                    id_row = None
                    with arcpy.da.SearchCursor(param_geodatabase + '/InputDataset', ['InputDatasetID'],
                                               'DatasetSourceID = ' + str(row['DatasetSourceID'])) as id_cursor:
                        for id_row in EBARUtils.searchCursor(id_cursor):
                            input_dataset_ids.append(id_row['InputDatasetID'])
                    if id_row:
                        del id_row
                    del id_cursor
                    self.applyJurisdictionSpecies(param_geodatabase, table_name_prefix, spatial_input, jurs, None,
                                                  input_dataset_ids, row['AllowedPrecisionSquareMiles'])
            if row:
                del row
            del cursor

    def applyJurisdictionSpecies(self, param_geodatabase, table_name_prefix, spatial_input, jurs, species_id,
                                 input_dataset_ids, allowed_precision_sq_miles):
        """apply rules for a single step"""
        # find spatial records with species_id not already set to N
        if species_id:
            where = 'SpeciesID = ' + str(species_id) # + ' AND NSXProTransfer IS NULL'
        else:
            where = 'InputDatasetID IN (' + ','.join(map(str, input_dataset_ids)) + ')'
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/'+ spatial_input, 'input_lyr', where)

        # select by Location interesting jur(s) buffers
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/JurisdictionBufferFull', 'jurbuffer_lyr')
        arcpy.AddJoin_management('jurbuffer_lyr', 'JurisdictionID', param_geodatabase + '/Jurisdiction',
                                 'JurisdictionID', 'KEEP_COMMON')
        arcpy.SelectLayerByAttribute_management('jurbuffer_lyr', 'NEW_SELECTION',
                                                table_name_prefix + 'Jurisdiction.JurisdictionAbbreviation IN (' +
                                                "'{0}'".format("','".join(jurs)) + ')')
        arcpy.SelectLayerByLocation_management('input_lyr', 'INTERSECT', 'jurbuffer_lyr')
        update_row = None
        with arcpy.da.UpdateCursor('input_lyr', ['NSXProTransfer', 'AllowedPrecisionSquareMiles']) as update_cursor:
            for update_row in EBARUtils.updateCursor(update_cursor):
                update = False
                # default to exclude
                nsx_pro_transfer = 'N'
                allowed_prec = 200000000 # NS magic number for exclude
                if allowed_precision_sq_miles < allowed_prec:
                    nsx_pro_transfer = 'Y'
                    allowed_prec = allowed_precision_sq_miles
                # keep coarsest of all rules and don't overrid previous exclude
                if (not update_row['NSXProTransfer']) or (update_row['NSXProTransfer'] == 'Y'):
                    if update_row['AllowedPrecisionSquareMiles']:
                        if allowed_prec > update_row['AllowedPrecisionSquareMiles']:
                            update = True
                    else:
                        update = True
                if update:
                    update_cursor.updateRow([nsx_pro_transfer, allowed_prec])
        if update_row:
            del update_row
        del update_cursor

        arcpy.Delete_management('jurbuffer_lyr')
        arcpy.Delete_management('input_lyr')


# controlling process
if __name__ == '__main__':
    pnpt = PrepareNSXProTransferTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:/GIS/EBAR/EBAR-KBA-Dev.gdb'
    parameters = [param_geodatabase]
    pnpt.runPrepareNSXProTransferTool(parameters, None)
