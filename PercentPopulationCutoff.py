"""
Script documentation

- Tool parameters are accessed using arcpy.GetParameter() or 
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""
import arcpy
import EBARUtils


def script_tool(param_input_polygon, param_total_pop, param_cutoff_percent):
    """Script code goes below"""
    cutoff = round(param_total_pop * param_cutoff_percent / 100)
    row = None
    prev_pop = 0
    total = 0
    with arcpy.da.SearchCursor(param_input_polygon, ['gridcode'],
                               sql_clause=[None,'ORDER BY gridcode ASC']) as cursor:
        for row in EBARUtils.searchCursor(cursor):
            total += row['gridcode']
            if total > cutoff:
                return prev_pop
            prev_pop = row['gridcode']
    del cursor
    if row:
        del row
    return prev_pop


if __name__ == "__main__":

    param_input_polygon = arcpy.GetParameter(0)
    param_total_pop = arcpy.GetParameter(1)
    param_cutoff_percent = arcpy.GetParameter(2)

    param_max = script_tool(param_input_polygon, param_total_pop, param_cutoff_percent)
    arcpy.AddMessage('Max: ' + str(param_max))
    arcpy.SetParameter(3, param_max)
