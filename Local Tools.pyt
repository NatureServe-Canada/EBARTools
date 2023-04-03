# import python packages
import arcpy
#import arcpy.mp
import EBARUtils
import PackageECCCPrioritySpecies


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = 'Local Tools'
        self.alias = 'LocalTools'

        # List of tool classes associated with this toolbox
        self.tools = [TestTool]


class TestTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Test Tool'
        self.description = 'Test desc'
        self.canRunInBackground = True

    def getParameterInfo(self):
        # """Define parameter definitions"""
        # param_species_id = arcpy.Parameter(
        #     displayName='Species ID',
        #     name='species_id',
        #     datatype='GPString',
        #     parameterType='Required',
        #     direction='Input')
        # params = [param_species_id]
        params = []
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is 
        called whenever a parameter has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called "
        "after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        ## make variables for parms
        # EBARUtils.displayMessage(messages, 'Processing parameters')
        # species_id = parameters[0].valueAsText
        # EBARUtils.displayMessage(messages, 'Species ID: ' + species_id)

        # # current ArcPro Project
        # aprx = arcpy.mp.ArcGISProject("CURRENT")

        # # current Active Map in ArcPro Project
        # map = aprx.activeMap

        # # new grp_lyr to be added to map
        # grp_lyr = arcpy.mp.LayerFile(EBARUtils.resources_folder + '/Species Data.lyrx')
        # map.addLayer(grp_lyr, 'TOP')
        # rename
        #grp_lyr

        # make feature layers for species
        # point_lyr = arcpy.MakeFeatureLayer_management(EBARUtils.restricted_service + '/0', 'point_lyr',
        #                                               'SpeciesID = ' + str(species_id))
        #if int(arcpy.GetCount_management(point_lyr).getOutput(0)) > 0:
            # grp_lyr.addLayer(point_lyr)
            #EBARUtils.displayMessage(messages, 'Records counted')
        # add to grp
        #map.addLayerToGroup(grp_lyr, point_lyr, 'BOTTOM')

        peps = PackageECCCPrioritySpecies.PackageECCCPrioritySpeciesTool()
        parameters = []
        peps.runPackageECCCPrioritySpeciesTool(parameters, messages)

        return