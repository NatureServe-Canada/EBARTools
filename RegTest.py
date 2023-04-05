#import arcpy
#import EBARUtils
#import re


mapx_file = open('C:/Temp/EBAR_ECCC_2022-23_Species_All_Data/test.txt')
mapx_text = mapx_file.read()
mapx_file.close()
input = '\\GIS\\EBAR\\temp\\EBAR_ECCC_2022-23_Species_All_Data'.replace('\\', '\\\\')
mapx_text = mapx_text.replace(input, '.')
#mapx_text = re.sub('[DATABASE=]', 'XXX', mapx_text)
print(mapx_text)
