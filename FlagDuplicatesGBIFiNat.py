# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Samantha Stefanoff
# © NatureServe Canada 2024 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: FlagDuplicatesGBIFiNat.py
# ArcGIS Python tool for flagging InputPoint/Line/Polygon records with the same provider unique identifier
# across GBIF, iNaturalist.ca and iNaturalist.org DatasetSources

# Notes:
# - command-line execution only, not yet converted to an interactive tool


import sys
import arcpy
import datetime
import EBARUtils


# parameters
param_geodatabase = 'C:/GIS/EBAR/nsc-gis-ebarkba.sde'

# redirect output to file
start_time = datetime.datetime.now()
folder = 'C:/GIS/EBAR/LogFiles/'
filename = 'FlagDuplicatesGBIFiNat' + str(start_time.year) + str(start_time.month) + str(start_time.day) + \
    str(start_time.hour) + str(start_time.minute) + str(start_time.second) + '.txt'
logfile = open(folder + filename, 'w')
sys.stdout = logfile

try:
    EBARUtils.displayMessage(None, 'Start time: ' + str(start_time))
    # priority is iNat.ca then iNat.org then GBIF
    # 

finally:
    logfile.close()
    sys.stdout = sys.__stdout__
