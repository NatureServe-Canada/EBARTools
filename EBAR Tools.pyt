# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: EBAR Tools.pyt
# ArcGIS Python toolbox for importing species datasets and generating EBAR maps

# Note: following 120 maximum line length "convention"


# import python packages
import arcpy
import ImportGBIFTool


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = 'EBAR Tools'
        self.alias = ''

        # List of tool classes associated with this toolbox
        self.tools = [ImportGBIF]


class ImportGBIF(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Import GBIF'
        self.description = 'Imports Global Biodiversity Information System (https://www.gbif.org/) data into the ' + \
                           'InputDataset and InputPoint tables of the EBAR geodatabase'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Raw Data File parm
        param_raw_data_file = arcpy.Parameter(
            displayName ='Raw Data File',
            name ='raw_data_file',
            datatype ='DETextFile',
            parameterType ='Required',
            direction ='Input')
        param_raw_data_file.filter.list = ['txt', 'csv']

        # Geodatabase parm
        param_geodatabase = arcpy.Parameter(
            displayName ='Geodatabase',
            name ='geodatabase',
            datatype ='DEWorkspace',
            parameterType ='Required',
            direction ='Input')
        param_geodatabase.filter.list = ['Local Database', 'Remote Database']

        params = [param_raw_data_file, param_geodatabase]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.  This method is " + \
        "called whenever a parameter has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.  This method is called " " \
        "after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        igt = ImportGBIFTool.ImportGBIFTool()
        igt.RunImportGBIFTool(parameters, messages)
        return
