# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Gabrielle Miller, Patrick Henry
# © NatureServe Canada 2024 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

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
        file_list = os.listdir(EBARUtils.log_folder)
        year_month_species_pdfs = {}
        year_month_species_zips = {}
        year_month_taxa_pdfs = {}
        year_month_taxa_zips = {}
        file_count = 0
        # test output file
        test_file = open('C:/GIS/EBAR/temp/test3.txt', 'w', encoding='MBCS')
        for file_name in file_list:
            # get year/month
            year_month = file_name[4:8]
            if not year_month in year_month_species_pdfs:
                year_month_species_pdfs[year_month] = 0
                year_month_species_zips[year_month] = 0
                year_month_taxa_pdfs[year_month] = 0
                year_month_taxa_zips[year_month] = 0
            # open file
            with open(EBARUtils.log_folder + '/' + file_name, 'r', encoding='MBCS') as log_file:
                # read one line at a time
                while True:
                    line_raw = log_file.readline()
                    file_line = line_raw.lower()
                    if file_line:
                        if (file_line.count('.pdf') > 0) or (file_line.count('.zip') > 0):
                            if ((file_line.count('bot.') == 0) and (file_line.count('bot/') == 0) and
                                (file_line.count('bot)') == 0) and (file_line.count('/bot') == 0) and
                                (file_line.count(' - 301') == 0) and (file_line.count(' - 400') == 0) and
                                (file_line.count(' - 401') == 0) and (file_line.count(' - 404') == 0) and
                                (file_line.count(' - 405') == 0) and (file_line.count(' - 500') == 0)):
                                if file_line.count('.pdf') > 0:
                                    year_month_species_pdfs[year_month] += 1
                                else: # .zip files
                                    if file_line.count('all+pdfs.zip') > 0:
                                        year_month_taxa_pdfs[year_month] += 1
                                    elif file_line.count('all+pdfs.zip') > 0:
                                        year_month_taxa_zips[year_month] += 1
                                    else:
                                        year_month_species_zips[year_month] += 1
                                test_file.write(file_line)
                    else:
                        break
            file_count +=1
            if file_count % 100 == 0:
                EBARUtils.displayMessage(messages, 'Log files processed: ' + str(file_count))
        test_file.close()
        EBARUtils.displayMessage(messages, 'Log files processed: ' + str(file_count))

        # write stats by month
        EBARUtils.displayMessage(messages, '')
        EBARUtils.displayMessage(messages, 'Species PDF downloads/views by month:')
        for year_month in year_month_species_pdfs:
            EBARUtils.displayMessage(messages, '20' + year_month[0:2] + '/' + year_month[2:4] + ': ' +
                                     str(year_month_species_pdfs[year_month]))
        EBARUtils.displayMessage(messages, '')
        EBARUtils.displayMessage(messages, 'Species Spatial ZIP downloads by month:')
        for year_month in year_month_species_zips:
            EBARUtils.displayMessage(messages, '20' + year_month[0:2] + '/' + year_month[2:4] + ': ' +
                                     str(year_month_species_zips[year_month]))
        EBARUtils.displayMessage(messages, '')
        EBARUtils.displayMessage(messages, 'Taxa Group PDF downloads/views by month:')
        for year_month in year_month_taxa_pdfs:
            EBARUtils.displayMessage(messages, '20' + year_month[0:2] + '/' + year_month[2:4] + ': ' +
                                     str(year_month_taxa_pdfs[year_month]))
        EBARUtils.displayMessage(messages, '')
        EBARUtils.displayMessage(messages, 'Taxa Group Spatial ZIP downloads by month:')
        for year_month in year_month_taxa_zips:
            EBARUtils.displayMessage(messages, '20' + year_month[0:2] + '/' + year_month[2:4] + ': ' +
                                     str(year_month_taxa_zips[year_month]))


# controlling process
if __name__ == '__main__':
    sd = SummarizeDownloadsTool()
    sd.runSummarizeDownloadsTool(None, None)
