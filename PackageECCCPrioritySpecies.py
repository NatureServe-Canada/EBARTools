# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Gabrielle Miller
# © NatureServe Canada 2022 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: PackageECCCPrioritySpeciesTool.py
# ArcGIS Python tool for creating Zip of PDFs and Spatial Data for all ECCC Priority Species

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import EBARUtils
import shutil
import arcpy
import datetime


class PackageECCCPrioritySpeciesTool:
    """Create Zip of PDFs and Spatial Data for all ECCC Priority Species"""
    def __init__(self):
        pass

    def processPackage(self, messages, range_map_ids, attributes_dict, zip_folder, metadata):
        # export range maps, with biotics/species additions
        EBARUtils.displayMessage(messages, 'Exporting RangeMap records to CSV')
        EBARUtils.ExportRangeMapToCSV('range_map_view', range_map_ids, attributes_dict, zip_folder, 'RangeMap.csv',
                                      metadata)

        # export range map ecoshapes
        EBARUtils.displayMessage(messages, 'Exporting RangeMapEcoshape records to CSV')
        EBARUtils.ExportRangeMapEcoshapesToCSV('range_map_ecoshape_view', range_map_ids, zip_folder,
                                               'RangeMapEcoshape.csv', metadata)

        # export ecoshapes
        EBARUtils.displayMessage(messages, 'Exporting Ecoshape polygons to shapefile')
        EBARUtils.ExportEcoshapesToShapefile('ecoshape_layer', 'range_map_ecoshape_view', zip_folder, 'Ecoshape.shp',
                                             metadata)

        # export overview ecoshapes
        EBARUtils.displayMessage(messages, 'Exporting EcoshapeOverview polygons to shapefile')
        EBARUtils.ExportEcoshapeOverviewsToShapefile('ecoshape_overview_layer', 'range_map_ecoshape_view', zip_folder, 
                                                     'EcoshapeOverview.shp', metadata)

        # copy ArcMap template
        EBARUtils.displayMessage(messages, 'Copying ArcMap template')
        shutil.copyfile(EBARUtils.resources_folder + '/EBAR.mxd', zip_folder + '/EBAR ECCC Priority Species.mxd')
        shutil.copyfile(EBARUtils.resources_folder + '/EcoshapeOverview.lyr', zip_folder + '/EcoshapeOverview.lyr')
        shutil.copyfile(EBARUtils.resources_folder + '/Ecoshape.lyr', zip_folder + '/Ecoshape.lyr')

        # create spatial zip
        EBARUtils.displayMessage(messages, 'Creating ZIP: https://gis.natureserve.ca/download/' +
                                 'EBAR ECCC Priority Species.zip')
        EBARUtils.createZip(zip_folder,
                            EBARUtils.download_folder + '/EBAR ECCC Priority Species.zip', None)

        # create pdf zip
        EBARUtils.displayMessage(messages, 'Creating ZIP: https://gis.natureserve.ca/download/' +
                                 'EBAR ECCC Priority Species - All PDFs.zip')
        EBARUtils.createZip(zip_folder,
                            EBARUtils.download_folder + '/EBAR ECCC Priority Species - All PDFs.zip','.pdf')

    def runPackageECCCPrioritySpeciesTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True

        # make variables for parms
        #EBARUtils.displayMessage(messages, 'Processing parameters')

        # generate metadata
        EBARUtils.displayMessage(messages, 'Generating metadata')
        md = arcpy.metadata.Metadata()
        md.tags = 'Species Range, NatureServe Canada, Ecosystem-based Automated Range'
        md.description = 'See EBARxxxxx.pdf for per-species map and additional metadata, RangeMap.csv ' + \
            'for species attributes for each ELEMENT_GLOBAL_ID (xxxxx), and ' + \
            'EBARMethods.pdf for additional details. <a href="https://explorer.natureserve.org/">Go to ' + \
            'NatureServe Explorer</a> for information about the species.'
        md.credits = 'Copyright NatureServe Canada ' + str(datetime.datetime.now().year)
        md.accessConstraints = 'Publicly shareable under CC BY 4.0 (<a href=' + \
            '"https://creativecommons.org/licenses/by/4.0/">https://creativecommons.org/licenses/by/4.0/</a>)'

        # use EBAR BIOTICS table if can't get taxon API
        arcpy.MakeTableView_management(EBARUtils.ebar_feature_service + '/4', 'biotics_view')

        # loop all RangeMap records where IncludeInDownloadTable is populated and Publish=1
        arcpy.MakeTableView_management(EBARUtils.ebar_feature_service + '/11', 'range_map_view',
                                       'IncludeInDownloadTable IN (1, 2, 3, 4) AND Publish = 1')
        # join BIOTICS_ELEMENT_NATIONAL to RangeMap
        arcpy.AddJoin_management('range_map_view', 'SpeciesID', EBARUtils.ebar_feature_service + '/4', 'SpeciesID',
                                 'KEEP_COMMON')
        # join Species to RangeMap
        arcpy.AddJoin_management('range_map_view', 'SpeciesID', EBARUtils.ebar_feature_service + '/19', 'SpeciesID',
                                 'KEEP_COMMON')
        processed = 0
        # use Python sorted (sql_clause ORDER BY doesn't work), which precludes use of EBARUtils.SearchCursor
        where_clause = "L19Species.ECCC_PrioritySpecies = 'Yes'"

        # make zip folder
        zip_folder = EBARUtils.temp_folder + '/EBAR ECCC Priority Species'
        EBARUtils.createReplaceFolder(zip_folder)

        # copy static resources
        shutil.copyfile(EBARUtils.resources_folder + '/ReadmeSet.txt', zip_folder + '/Readme.txt')
        shutil.copyfile(EBARUtils.resources_folder + '/EBARMethods.pdf', zip_folder + '/EBARMethods.pdf')
        shutil.copyfile(EBARUtils.resources_folder + '/Jurisdiction.csv', zip_folder + '/Jurisdiction.csv')

        range_map_ids = []
        attributes_dict = {}
        row = None
        for row in sorted(arcpy.da.SearchCursor('range_map_view',
                          ['L4BIOTICS_ELEMENT_NATIONAL.CATEGORY',
                           'L4BIOTICS_ELEMENT_NATIONAL.TAX_GROUP',
                           'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_SCIENTIFIC_NAME',
                           'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_ENGL_NAME',
                           'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_FR_NAME',
                           'L4BIOTICS_ELEMENT_NATIONAL.ELEMENT_GLOBAL_ID',
                           'L4BIOTICS_ELEMENT_NATIONAL.GLOBAL_UNIQUE_IDENTIFIER',
                           'L11RangeMap.RangeMapScope',
                           'L11RangeMap.RangeMapID',
                           'L11RangeMap.IncludeInDownloadTable',
                           'L4BIOTICS_ELEMENT_NATIONAL.SpeciesID'], where_clause)):
            processed += 1

            # copy pdf 
            EBARUtils.displayMessage(messages, 'Range Map ID: ' + str(row[8]))
            element_global_id = str(row[5])
            if row[7] == 'N':
                element_global_id += 'N'
            shutil.copyfile(EBARUtils.download_folder + '/EBAR' + element_global_id + '.pdf',
                            zip_folder + '/EBAR' + element_global_id + '.pdf')

            # set range map attributes
            range_map_ids.append(str(row[8]))
            arcpy.SelectLayerByAttribute_management('biotics_view', 'NEW_SELECTION', 'SpeciesID = ' + str(row[10]))
            attributes_dict[str(row[8])] = EBARUtils.getTaxonAttributes(row[6], element_global_id, row[8],
                                                                        messages)

            # update ArcGIS Pro template
            EBARUtils.displayMessage(messages, 'Updating ArcGIS Pro template')
            EBARUtils.updateArcGISProTemplate(zip_folder, element_global_id, md, row[8])

        if row:
            self.processPackage(messages, range_map_ids, attributes_dict, zip_folder, md)
            del row

        EBARUtils.displayMessage(messages, 'Processed ' + str(processed) + ' RangeMaps')
        return


# controlling process
if __name__ == '__main__':
    peps = PackageECCCPrioritySpeciesTool()
    parameters = []
    peps.runPackageECCCPrioritySpeciesTool(parameters, None)
