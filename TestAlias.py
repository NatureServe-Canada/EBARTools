import arcpy

fields = arcpy.ListFields(r'C:\GIS\EBAR\nsc-gis-ebarkba.sde\ebarkba.sde.TempEcoshapeMaxPolygon2026119102412')
for field in fields:
    print(field.aliasName)
