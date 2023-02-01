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
            # apply spatial inclusions and species susceptible to persecution and harm (STPH) exclusions
            # need to reset Ys to NULLs in case rules/datasets change
            arcpy.CalculateField_management(param_geodatabase + '/' + spatial_input, 'NSXProTransfer', None)
            arcpy.CalculateField_management(param_geodatabase + '/' + spatial_input, 'AllowedPrecisionSquareMiles',
                                            None)

            # jurisdiction-level rules are handled by prov/territory, with NF and LB separated
            jurs = ['BC', 'AB', 'SK', 'MB', 'ON', 'NB', 'PE', 'NS', 'NF', 'LB', 'NU', 'NT', 'YT']

            # join STPH table to jurisdiction
            arcpy.MakeTableView_management(param_geodatabase + '/SpeciesSTPH', 'stph_view')
            arcpy.AddJoin_management('stph_view', 'JurisdictionID', param_geodatabase + '/Jurisdiction',
                                     'JurisdictionID', 'KEEP_COMMON')

            # process rules in five steps, using coarsest of all rules
            # iNaturalist.ca Canada-wide STPHs
            row = None
            with arcpy.da.SearchCursor('stph_view', ['SpeciesID', 'AllowedPrecisionSquareMiles'],
                                       table_name_prefix + "Jurisdiction.JurisdictionAbbreviation = 'CA' AND " +
                                       table_name_prefix + "SpeciesSTPH.ObscuredForiNatca = 'Y'") as cursor:
                for row in EBARUtils.searchCursor(cursor):
                    self.applyJurisdictionSpecies(param_geodatabase, table_name_prefix, spatial_input, jurs,
                                                  row[table_name_prefix + 'SpeciesSTPH.SpeciesID'], None,
                                                  row[table_name_prefix + 'SpeciesSTPH.AllowedPrecisionSquareMiles'])
            if row:
                del row
            del cursor

            # iNaturalist.ca by jurisdiction STPHs

            # NSC/CDC Canada-wide STPHs

            # NSC/CDC by jurisdiction STPHs

            arcpy.Delete_management('stph_view')

            # EBAR provider permissions
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
            where = 'InputDatasetID IN (' + ','.join(input_dataset_ids) + ')'
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/'+ spatial_input, 'input_lyr', where)

        # select by Location interesting jur(s) buffers
        arcpy.MakeFeatureLayer_management(param_geodatabase + '/JurisdictionBufferFull', 'jurbuffer_lyr')
        arcpy.AddJoin_management('jurbuffer_lyr', 'JurisdictionID', param_geodatabase + '/Jurisdiction',
                                 'JurisdictionID', 'KEEP_COMMON')
        arcpy.SelectLayerByAttribute_management('jurbuffer_lyr', 'NEW_SELECTION',
                                                table_name_prefix + 'Jurisdiction.JurisdictionAbbreviation IN (' +
                                                ','.join(jurs) + ')')
        arcpy.SelectLayerByLocation_management('input_lyr', 'INTERSECT', 'jurbuffer_lyr')
        update_row = None
        with arcpy.da.updateCursor('input_lyr', ['AllowedPrecisionSquareMiles']) as update_cursor:
            for update_row in EBARUtils.updateCursor(update_cursor):
                update = False
                # default to coarsest resolution (343)
                prec = 343
                if allowed_precision_sq_miles < 343:
                    prec = allowed_precision_sq_miles
                # set coarsest of all rules
                if update_row['AllowedPrecisionSquareMiles']:
                    if prec > update_row['AllowedPrecisionSquareMiles']:
                        update = True
                else:
                    update = True
                if update:
                    update_cursor.updateRow(['Y', prec])
        if update_row:
            del update_row
        del update_cursor

        return
        # # create Layer on input with filter DatasetSource.NSXProTransfer=Y
        # where = "InputDatasetID IN (SELECT InputDatasetID FROM InputDataset WHERE DatasetSourceID IN" + \
        #         " (SELECT DatasetSourceID FROM DatasetSource WHERE NSXProTransfer='Y'))"
        # arcpy.MakeFeatureLayer_management(param_geodatabase + '/'+ spatial_input, 'input_lyr', where)

        # # select by Attribute on SpeciesIDs not in STPH for jur + Canada exclusion
        # with arcpy.da.SearchCursor():
        #     pass
        # #  update cursor on layer
        # #  if not N, set to Y



# controlling process
if __name__ == '__main__':
    pnpt = PrepareNSXProTransferTool()
    # hard code parameters for debugging
    param_geodatabase = arcpy.Parameter()
    param_geodatabase.value = 'C:/GIS/EBAR/EBAR-KBA-Dev.gdb'
    parameters = [param_geodatabase]
    #pnpt.runPrepareNSXProTransferTool(parameters, None)
