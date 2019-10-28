# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: ImportPolygonsTool.py
# ArcGIS Python tool for importing polygon data into the
# InputDataset and InputPolygon tables of the EBAR geodatabase

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import sys
import traceback
import arcpy
import io
import csv
import datetime
#import locale
import EBARUtils
import PointsFieldMapping


class ImportPolygonsTool:
    """Import point data into the InputDataset and InputPoint tables of the EBAR geodatabase"""
    def __init__(self):
        pass

    def RunImportPolygonsTool(self, parameters, messages):
        return


# controlling process
if __name__ == '__main__':
    ipt = ImportPolygonsTool()
    # hard code parameters for debugging
    ipt.RunImportPolygonsTool(None, None)
