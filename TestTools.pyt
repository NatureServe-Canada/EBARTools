# import python packages
import arcpy


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = 'Test Tools'
        self.alias = ''

        # List of tool classes associated with this toolbox
        self.tools = [TestTool]


class TestTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Test Tool'
        self.description = 'Test'
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        return None

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
        arcpy.AddMessage('TEST0')