# directory_report_generator

This script returns the total volume in GiB of each top-level directory within a user-provided path. It ignores 'loose' files located at the top level. It is similar to `du -sh` in Unix, but with friendlier output.

It creates two output files in a user-provided output directory: 
    
The first is a spreadsheet, 'directory_report.csv'. This shows the size in GiB of all top-level directories in the path scanned for a given date, plus a total GiB of all directories. If the report is run multiple times on the same directory and the same output path is specified, new columns will be added to the previous spreadsheet, creating a running log of a directory's size over time.

The CSV output file is created using a second temporary spreadsheet, directory_report_new.csv, which replaces the previous spreadsheet once each directory has been scanned. This allows each version of the report to maintain a record of directories removed between scans, as well as new directories added between scans

The second output file is a human-readable text file, directory_report.txt, which compares each directory in the latest directory_report.csv against the previous scan. This is useful for identifying which directories show the most growth in GiB and by percentage. The text file also notes whether a folder was deleted or added between scans.

Although the calculation of each directory's size is in bytes, the report spreadsheet rounds these to GiB. The report text file rounds large directories (1024 GiB or more) to TiB, but calculates absolute and percent growth in GiB. This report function can be modified to leave byte counts unconverted, however in its original state it should not be used to determine precise changes in directory size.
