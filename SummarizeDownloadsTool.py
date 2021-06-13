# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Gabrielle Miller
# © NatureServe Canada 2021 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: SummarizeDownloadStatus.py
# ArcGIS Python tool for summarizing file download stats using IIS logs

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import os
import EBARUtils


class SummarizeDownloadsTool:
    """Summarize file download stats using IIS logs"""
    def __init__(self):
        pass

    def runSummarizeDownloadsTool(self, parameters, messages):
        log_folder = 'C:/GIS/EBAR/LogFiles'
        file_list = os.listdir(log_folder)
        year_month_pdfs = {}
        year_month_zips = {}
        file_count = 0
        for file_name in file_list:
            # get year/month
            year_month = file_name[4:8]
            if not year_month in year_month_pdfs:
                year_month_pdfs[year_month] = 0
                year_month_zips[year_month] = 0
            # open file
            with open(log_folder + '/' + file_name, 'r', encoding='MBCS') as log_file:
                # read the whole file to a string
                log_text = log_file.read()
                # search/count .pdf and add to stats
                year_month_pdfs[year_month] += log_text.count('.pdf')
                # search/count .zip and add to stats
                year_month_zips[year_month] += log_text.count('.zip')
            file_count +=1
            if file_count % 100 == 0:
                EBARUtils.displayMessage(messages, 'Log files processed: ' + str(file_count))
        EBARUtils.displayMessage(messages, 'Log files processed: ' + str(file_count))

        # write stats by month
        EBARUtils.displayMessage(messages, '')
        EBARUtils.displayMessage(messages, 'PDF downloads/views by month:')
        for year_month in year_month_pdfs:
            EBARUtils.displayMessage(messages, '20' + year_month[0:2] + '/' + year_month[2:4] + ': ' +
                                     str(year_month_pdfs[year_month]))
        EBARUtils.displayMessage(messages, '')
        EBARUtils.displayMessage(messages, 'Spatial ZIP downloads by month:')
        for year_month in year_month_zips:
            EBARUtils.displayMessage(messages, '20' + year_month[0:2] + '/' + year_month[2:4] + ': ' +
                                     str(year_month_zips[year_month]))


# controlling process
if __name__ == '__main__':
    sd = SummarizeDownloadsTool()
    # hard code parameters for debugging
    #param_geodatabase = arcpy.Parameter()
    #param_geodatabase.value = 'C:/GIS/EBAR/EBAR-KBA-Dev.gdb'
    #parameters = [param_geodatabase, param_raw_data_file, param_dataset_name, param_dataset_source,
    #              param_date_received, param_restrictions]
    sd.runSummarizeDownloadsTool(None, None)
