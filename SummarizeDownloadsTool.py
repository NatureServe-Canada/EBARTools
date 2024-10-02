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
        log_file_count = 0
        file_download_count = {}
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
                        # only count .pdf and .zip files
                        if (file_line.count('.pdf') > 0) or (file_line.count('.zip') > 0):
                            # ignore bots and http return errors
                            if ((file_line.count('bot.') == 0) and (file_line.count('bot/') == 0) and
                                (file_line.count('bot)') == 0) and (file_line.count('/bot') == 0) and
                                (file_line.count(' - 301') == 0) and (file_line.count(' - 400') == 0) and
                                (file_line.count(' - 401') == 0) and (file_line.count(' - 404') == 0) and
                                (file_line.count(' - 405') == 0) and (file_line.count(' - 500') == 0) and
                                (file_line.count('favicon') == 0)):
                                # increment overall counts
                                if file_line.count('.pdf') > 0:
                                    year_month_species_pdfs[year_month] += 1
                                else: # .zip files
                                    if file_line.count('all+pdfs.zip') > 0:
                                        year_month_taxa_pdfs[year_month] += 1
                                    elif file_line.count('all+data.zip') > 0:
                                        year_month_taxa_zips[year_month] += 1
                                    else:
                                        year_month_species_zips[year_month] += 1
                                # increment file counts
                                line_segments = line_raw.split(' ')
                                for line_segment in line_segments:
                                    if line_segment[0:10] == '/download/':
                                        download_file_name = line_segment[11:]
                                        if download_file_name not in file_download_count.keys():
                                            file_download_count[download_file_name] = 1
                                        else:
                                            file_download_count[download_file_name] += 1
                                # test
                                test_file.write(line_raw)
                    else:
                        break
            log_file_count +=1
            if log_file_count % 100 == 0:
                EBARUtils.displayMessage(messages, 'Log files processed: ' + str(log_file_count))
        test_file.close()
        EBARUtils.displayMessage(messages, 'Log files processed: ' + str(log_file_count))

        # write individual file download counts
        EBARUtils.displayMessage(messages, '')
        for download_file in sorted(file_download_count.keys()):
            EBARUtils.displayMessage(messages, download_file + ' downloaded ' +
                                     str(file_download_count[download_file]) + ' times')

        # write overall stats by month
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
            
        # write overall stats
        EBARUtils.displayMessage(messages, '')
        EBARUtils.displayMessage(messages, 'Species PDF downloads/views overall: ' +
                                 sum(year_month_species_pdfs.values()))
        EBARUtils.displayMessage(messages, '')
        EBARUtils.displayMessage(messages, 'Species Spatial ZIP downloads overall: ' +
                                 sum(year_month_species_zips.values()))
        EBARUtils.displayMessage(messages, '')
        EBARUtils.displayMessage(messages, 'Taxa Group PDF downloads/views overall: ' +
                                 sum(year_month_taxa_pdfs.values()))
        EBARUtils.displayMessage(messages, '')
        EBARUtils.displayMessage(messages, 'Taxa Group Spatial ZIP downloads overall: ' +
                                 sum(year_month_taxa_pdfs.values()))


# controlling process
if __name__ == '__main__':
    sd = SummarizeDownloadsTool()
    sd.runSummarizeDownloadsTool(None, None)
