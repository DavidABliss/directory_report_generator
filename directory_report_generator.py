import os
import datetime
import csv 
import argparse

def directoryReport(rootDir, reportDir):
    # Path to three output reports (one temporary)
    csvPath1 = reportDir + 'directory_report.csv'
    csvPath2 = reportDir + 'directory_report_new.csv'
    txtPath = reportDir + 'directory_report.txt'

    # Determine whether there is an existing directory_report.csv file at the
    # output path. Create a new temporary report if needed.
    reportDirContents = os.listdir(reportDir)
    if 'directory_report.csv' not in reportDirContents:
        with open(csvPath1, 'a', encoding='utf-8', newline='') as blankSpreadsheet:
            blankSpreadsheet.write('DATE\n')
            blankSpreadsheet.write('TOTAL')
            
    # Create a list of directories (ignoring files) at the user-provided path
    directories = []
    topDirs = os.listdir(rootDir)
    
    # Remove the '.snapshot' directory from the list to skip it. This directory
    # contains temporary archived copies of the entire directory/volume and 
    # makes the process take several times longer if it is included
    if '.snapshot' in topDirs:
        topDirs.remove('.snapshot') 
    for item in topDirs:
        if os.path.isdir(rootDir + item):
            directories.append(item)

    # Create a variable for the total size of all directories at the path
    # Store a list of the directories included in the previous report
    # Create a new column header with today's date. Use the header row to 
    # determine the total number of reports included in this spreadsheet
    total_size = 0
    with open(csvPath1, 'r', encoding='utf-8') as prevSpreadsheet:
            csvReader = csv.reader(prevSpreadsheet, delimiter=',', quotechar='"')
            prevList = []
            for row in csvReader:
                prevList.append(row[0])
                if csvReader.line_num == 1:
                    row.append(datetime.date.today().isoformat())
                    sheetLength = len(row)
                    zeroSheetLength = sheetLength - 1
                    print('This is report number ' + str(zeroSheetLength))
                    with open(csvPath2, 'a', encoding = 'utf-8', newline='') as newSpreadsheet:
                        csvWriter = csv.writer(newSpreadsheet, delimiter = ',', quotechar='"')
                        csvWriter.writerow(row)
    
    # Calculate the size of each top-level directory. Add each directory's size
    # to the running total size count.
    # Convert the directory's size to GiB, and if that folder name was in the
    # previous report, add the latest data to that folder's row.
    for folder in directories:
        size = 0    
        print('Now reading directory: ' + folder)
        for root, dirs, files in os.walk(rootDir + folder):
            for file in files:
                filepath = os.path.join(root, file)
                size += os.path.getsize(filepath)
        total_size = total_size + size
        size_gib = size / 1073741824
        size_gib = round(size_gib, 2)
        if folder in prevList:
            with open(csvPath1, 'r', encoding='utf-8') as prevSpreadsheet:
                csvReader = csv.reader(prevSpreadsheet, delimiter=',', quotechar='"')
                for row in csvReader:
                    if row[0] == folder:
                        while len(row) < zeroSheetLength:
                            row.append('')
                            continue
                        row.append(size_gib)
                        newRow = row
        # If the folder was not in the last report, create a new entry for 
        # it in the new report. Insert blank cells to ensure that the new
        # data is stored in the correct column. 
        else:
            newRow = []
            newRow.append(folder)
            while len(newRow) < zeroSheetLength:
                newRow.append('')
                continue
            newRow.append(size_gib) 
        with open(csvPath2, 'a', encoding = 'utf-8', newline='') as newSpreadsheet:
            csvWriter = csv.writer(newSpreadsheet, delimiter = ',', quotechar='"')
            csvWriter.writerow(newRow)
            
    # Read the previous report spreadsheet one last time to identify folders 
    # that were present in a previous report but which do not currently exist.
    # Add a 'TOTAL' column.
    with open(csvPath1, 'r', encoding='utf-8') as prevSpreadsheet:
        csvReader = csv.reader(prevSpreadsheet, delimiter=',', quotechar='"')
        for row in csvReader:
            if row[0] not in directories:
                if row[0] != 'DATE':
                    if row[0] != 'TOTAL':
                        with open(csvPath2, 'a', encoding='utf-8', newline='') as newSpreadsheet:
                            csvWriter = csv.writer(newSpreadsheet, delimiter=',', quotechar='"')
                            csvWriter.writerow(row)
                    if row[0] == 'TOTAL':
                        row.append(total_size / 1073741824)
                        row[-1] = round(row[-1], 2)
                        with open(csvPath2, 'a', encoding='utf-8', newline='') as newSpreadsheet:
                            csvWriter = csv.writer(newSpreadsheet, delimiter=',', quotechar='"')
                            csvWriter.writerow(row)
    
    # Remove the previous spreadsheet and replace it with the new one                
    os.remove(csvPath1)
    os.rename(csvPath2, csvPath1)

    # Create a report output text file, or add to an existing one at the path.
    # Write the date, the folder name, and size of the folder in GiB or TiB.
    # Determine whether the folder is new in the latest report, was deleted
    # after the previous report, or is unchanged. Wherever possible, provide
    # the change in absolute and percentage terms.
    with open(txtPath, 'a+', encoding='utf-8') as output:
        output.write('\n ----------------------------------- \n\n')            
        output.write('Report date: ' + str(datetime.date.today().isoformat()) + '\n\n')
        with open(csvPath1, 'r', encoding='utf-8', newline='') as reportSpreadsheet:
            csvReader = csv.reader(reportSpreadsheet, delimiter=',', quotechar='"')
            next(csvReader)
            for row in csvReader:
                folderName = row[0]
                if folderName == 'TOTAL':
                    output.write('\n')
                # Identify folders that were not scanned in the last report,
                # because they have been removed. If these folders were present
                # in the last scan, note that they have been removed and output
                # the change in GiB. Folders that have been gone for more than 
                # one report are not output in the text file, but are kept in 
                # the spreadsheet. If they are ever re-added to the directory,
                # the function will add blank column values above (line 110) 
                # prior to this step.
                if len(row) < sheetLength:
                    if len(row) == (sheetLength - 1):
                        lastSize = float(row[-1])
                        growth_gib = (0 - lastSize)
                        growth_gib = round(growth_gib, 2)
                        growth_tib = growth_gib / 1024
                        growth_tib = round(growth_tib, 2)
                        if lastSize < 1024:
                            output.write(folderName + ' -- removed (' + str(growth_gib) + ' GiB change) \n')
                        elif lastSize >= 1024:
                            output.write(folderName + ' -- removed (' + str(growth_tib) + ' TiB change) \n')
                # For rows that are not blank in the last column, determine
                # whether this is the first report, whether the folder is new,
                # or if there has been a change in values between the last two
                # reports. Produce the appropriate output for each condition.
                else:
                    currentSize = float(row[-1])
                    currentSize_tib = currentSize / 1024
                    currentSize_tib = round(currentSize_tib, 2)
                    if currentSize == 0:
                        if sheetLength == 2:
                            output.write(folderName + ' -- ' + str(currentSize) + ' GiB \n')
                        elif row[-2] == '':
                            output.write(folderName + ' -- ' + str(currentSize) + ' GiB (new folder) \n')
                        else:
                            lastSize = float(row[-2])
                            if currentSize == lastSize:
                                output.write(folderName + ' -- ' + str(currentSize) + ' GiB (no change) \n')
                            elif currentSize != lastSize:
                                growth_gib = (currentSize - lastSize)
                                growth_gib = round(growth_gib, 2)
                                if growth_gib < 1024:
                                    output.write(folderName + ' -- '  + str(currentSize) + ' GiB, (' + str(growth_gib) + ' GiB change) \n')
                                elif growth_gib >= 1024:
                                    growth_tib = growth_gib / 1024
                                    growth_tib = round(growth_tib, 2)
                                    output.write(folderName + ' -- '  + str(currentSize) + ' TiB, (' + str(growth_tib) + ' GiB change) \n')
                    elif currentSize > 0:
                        if row[-2] == '':
                            if currentSize < 1024:
                                output.write(folderName + ' -- ' + str(currentSize) + ' GiB (new folder) \n')
                            elif currentSize >= 1024:
                                output.write(folderName + ' -- ' + str(currentSize_tib) + ' TiB (new folder) \n')
                        elif sheetLength == 2:
                            if currentSize < 1024:
                                output.write(folderName + ' -- ' + str(currentSize) + ' GiB \n')
                            elif currentSize >= 1024:
                                output.write(folderName + ' -- ' + str(currentSize_tib) + ' TiB \n')
                        elif row[-2] != row[0]:
                            lastSize = float(row[-2])
                            growth_gib = (currentSize - lastSize)
                            growth_gib = round(growth_gib, 2)
                            growth_tib = growth_gib / 1024
                            growth_tib = round(growth_tib, 2)
                            if currentSize == lastSize:
                                if currentSize <= 1024:
                                    output.write(folderName + ' -- ' + str(currentSize) + ' GiB (no change) \n')
                                elif currentSize > 1024:
                                    output.write(folderName + ' -- ' + str(currentSize_tib) + ' TiB (no change) \n')
                            elif currentSize != lastSize:
                                if lastSize != 0:
                                    growthPercent = (currentSize - lastSize) / lastSize * 100
                                    growthPercent = round(growthPercent, 2)
                                    if growth_gib < 1024:
                                        if currentSize < 1024:
                                            output.write(folderName + ' -- ' + str(currentSize) + ' GiB (' + str(growth_gib) + ' GiB change, ' + str(growthPercent) + '% growth) \n')
                                        elif currentSize >= 1024:
                                            output.write(folderName + ' -- ' + str(currentSize_tib) + ' TiB (' + str(growth_gib) + ' GiB change, ' + str(growthPercent) + '% growth) \n')
                                    elif growth_gib >= 1024:
                                        if currentSize < 1024:
                                            output.write(folderName + ' -- ' + str(currentSize) + ' GiB (' + str(growth_tib) + ' TiB change, ' + str(growthPercent) + '% growth) \n')
                                        elif currentSize >= 1024:
                                            output.write(folderName + ' -- ' + str(currentSize_tib) + ' TiB (' + str(growth_tib) + ' TiB change, ' + str(growthPercent) + '% growth) \n')
                                else:
                                    if growth_gib < 1024:
                                        output.write(folderName + ' -- '  + str(currentSize) + ' GiB, (' + str(growth_gib) + ' GiB change) \n')
                                    elif growth_gib >= 1024:
                                        growth_tib = growth_gib / 1024
                                        growth_tib = round(growth_tib, 2)
                                        output.write(folderName + ' -- '  + str(currentSize) + ' TiB, (' + str(growth_tib) + ' GiB change) \n')


        output.write('\n ----------------------------------- \n')    

# Get user input for the path to be scanned and the path to place reports.
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', required=True, help="path to the drive or directory to be scanned", action="store", dest="i")
parser.add_argument('-o', '--output', required=True, help="Path to a directory where reports will be saved", action="store", dest="o")

args = parser.parse_args()        
inputDir = args.i
outputDir = args.o

if not inputDir.endswith('/'):
    inputDir = inputDir + '/'
if not outputDir.endswith('/'):
    outputDir = outputDir + '/'
directoryReport(inputDir.rstrip(), outputDir.rstrip())
