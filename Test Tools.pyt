# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen, Meg Southee
# © NatureServe Canada 2020 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: EBAR Tools.pyt
# ArcGIS Python toolbox for testing

# Notes:
# - following 120 maximum line length "convention"
# - tested with ArcGIS Pro 2.5.1


# import python packages
import arcpy
import PublishRangeMapTool
import pdfkit
import datetime
import zipfile
#import shutil
import os


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = 'Test Tools'
        self.alias = ''

        # List of tool classes associated with this toolbox
        self.tools = [PublishRangeMap, TestPDF, TestZip]


class PublishRangeMap(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'PublishRangeMap'
        self.description = 'Create JPG, PDF and Spatial Data (Zip) for a Range Map'
        self.canRunInBackground = True

    def getParameterInfo(self):
        ## Species
        #param_species = arcpy.Parameter(
        #    displayName='Species Scientific Name',
        #    name='species',
        #    datatype='GPString',
        #    parameterType='Required',
        #    direction='Input')

        ## Secondary Species
        #param_secondary = arcpy.Parameter(
        #    displayName='Secondary Species',
        #    name='secondary_species',
        #    datatype='GPString',
        #    parameterType='Optional',
        #    direction='Input',
        #    multiValue=True)

        ## Range Version
        #param_version = arcpy.Parameter(
        #    displayName='Range Version',
        #    name='range_version',
        #    datatype='GPString',
        #    parameterType='Required',
        #    direction='Input')
        #param_version.value = '1.0'

        ## Range Stage
        #param_stage = arcpy.Parameter(
        #    displayName='Range Stage',
        #    name='range_stage',
        #    datatype='GPString',
        #    parameterType='Required',
        #    direction='Input')
        #param_stage.value = 'Expert Reviewed'

        # Range Map ID
        param_range_map_id = arcpy.Parameter(
            displayName='Range Map ID',
            name='range_map_id',
            datatype='GPString',
            parameterType='Required',
            direction='Input')
        param_stage.value = '199'

        # Include PDF
        param_pdf = arcpy.Parameter(
            displayName='Include PDF',
            name='include_pdf',
            datatype='GPBoolean',
            parameterType='Required',
            direction='Input')
        param_pdf.value = True

        # Include JPG
        param_jpg = arcpy.Parameter(
            displayName='Include JPG',
            name='include_jpg',
            datatype='GPBoolean',
            parameterType='Required',
            direction='Input')
        param_jpg.value = True

        # Include Spatial
        param_spatial = arcpy.Parameter(
            displayName='Include Spatial Data (ZIP)',
            name='include_spatial',
            datatype='GPBoolean',
            parameterType='Required',
            direction='Input')
        param_spatial.value = True

        params = [param_range_map_id, param_pdf, param_jpg, param_spatial]
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
        prm = PublishRangeMapTool.PublishRangeMapTool()
        prm.RunPublishRangeMapTool(parameters, messages)
        return


class TestPDF(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Test PDF'
        self.description = 'Test PDF desc'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        # output pdf
        param_output_pdf = arcpy.Parameter(
            displayName='Output PDF',
            name='output_pdf',
            datatype='DEFile',
            parameterType='Required',
            direction='Output')
        param_output_pdf.filter.list = ['pdf']

        return [param_output_pdf]

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
        param_output_pdf = parameters[0].valueAsText
        pdfkit.from_string('Hello world at ' + str(datetime.datetime.now()), param_output_pdf) #, pdf_options)


class TestZip(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Test Zip'
        self.description = 'Test Zip desc'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Feature Class to Zip
        param_feature_class = arcpy.Parameter(
            displayName='Feature Class',
            name='feature_class',
            datatype='GPFeatureLayer',
            parameterType='Required',
            direction='Input')
        param_feature_class.filter.list = ['Point', 'Multipoint', 'Polyline', 'Polygon', 'MultiPatch']

        # folder
        param_folder = arcpy.Parameter(
            displayName='Folder',
            name='folder',
            datatype='DEFolder',
            parameterType='Required',
            direction='Input')

        # text
        param_text = arcpy.Parameter(
            displayName='Text',
            name='text',
            datatype='GPString',
            parameterType='Required',
            direction='Input')

        return [param_feature_class, param_folder, param_text]

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
        param_feature_class = parameters[0].valueAsText
        param_output_folder = parameters[1].valueAsText
        param_output_text = parameters[2].valueAsText
        if arcpy.Exists('C:/GIS/EBAR/test1.gdb'):
            arcpy.Delete_management('C:/GIS/EBAR/test1.gdb')
        arcpy.CreateFileGDB_management('C:/GIS/EBAR', 'test1.gdb')
        arcpy.CopyFeatures_management(param_feature_class, 'C:/GIS/EBAR/test1.gdb/test1')
        #arcpy.Copy_management('C:/GIS/EBAR/test1.gdb', 'C:/GIS/EBAR/testout.gdb')
        os.chdir('C:/GIS/EBAR')
        #shutil.make_archive(param_output_folder + '/testout', 'zip', 'C:/GIS/EBAR/test1.gdb', 'C:/GIS/EBAR/test1.gdb')
        zip1 = zipfile.ZipFile('C:/GIS/EBAR/testout.zip', 'w')
        for root, dirs, files in os.walk('C:/GIS/EBAR/test1.gdb'):
            for file in files:
                #zip1.write(os.path.join(root, file))
                zip1.write('test1.gdb/' + file)
        zip1.close()
