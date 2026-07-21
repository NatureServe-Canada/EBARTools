import arcpy


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = 'Test Merge'
        self.alias = ''

        # List of tool classes associated with this toolbox
        self.tools = [TestMergeTool]


class TestMergeTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = 'Test Merge'
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
        if messages:
            arcpy.AddMessage('TEST begin')
        else:
            print('TEST begin')
        temp_point_buffer = r'C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempPointBuffer202611993629'
        temp_line_buffer = r'C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempLineBuffer202611993629'
        input_polygon_layer = 'input_polygon_layer'
        arcpy.MakeFeatureLayer_management(r'C:\GIS\EBAR\nsc-gis-ebarkba.sde\InputPolygon', input_polygon_layer, '0=1')
        temp_all_inputs = r'C:\GIS\EBAR\nsc-gis-ebarkba.sde\TempMerge'
        arcpy.env.overwriteOutput = True
        # Three scenarios with output prefixes as follows:
        # py = command-line run of py file (should be no different than pytc!)
        # pytc = command-line run of pyt file
        # pyti = toolbox run in Pro
        # 1. all good with correct inputs
        # 1. ERROR 002948: The shape type of InputPolygon is not the same as that of previously entered datasets (when mistakenly had a table as input)
        arcpy.Merge_management([temp_point_buffer, temp_line_buffer, input_polygon_layer], temp_all_inputs,
                                add_source='ADD_SOURCE_INFO')
        # # 2. removed temp_line_buffer - succeeds but creates table not polygons
        # # 2b. added explicit field_match_mode
        # arcpy.Merge_management([temp_point_buffer, input_polygon_layer], temp_all_inputs, add_source='ADD_SOURCE_INFO', field_match_mode='AUTOMATIC')
        # # 3. reordered inputs - no error but empty/incorrect results
        # arcpy.Merge_management([input_polygon_layer, temp_point_buffer, temp_line_buffer], temp_all_inputs,
        #                         add_source='ADD_SOURCE_INFO')
        if messages:
            arcpy.AddMessage('TEST end')
        else:
            print('TEST end')


# controlling process
if __name__ == '__main__':
    tm = TestMergeTool()
    tm.execute([], None)
