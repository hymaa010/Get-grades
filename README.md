# Get-grades

you can add fast after first use in user_info.txt to get the same courses faster

grades.json changes every run time
grades_backup.json only at first run or if doesn't exist to check for grades change

links.json for in faster if back_up is not there
links_backup.json only at first run or if doesn't exist backed up links for use if using faster

edited-out lines are for use if you want to keep searching for grades every random time between 00:30 and 05:30 

needed libraries if not using release: lxml bs4 aiohttp colorama tkinter
build using:  Pyinstaller get_grades.py -n get_grades.exe -F
or: python -m Pyinstaller -n get_grades.exe -F
depending on system conferation
