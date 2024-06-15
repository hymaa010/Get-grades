#!/bin/bash

# make wine quite
export WINEDEBUG=fixme-all 

version=$1
zip_location="./builds/Get_Grades_v${version}.zip"

if [ -f $zip_location ] 
then
    echo "version $version already exists"
    exit
fi

wine64 python -m nuitka --standalone get_grades.py -o Get_Grades_v${version}.exe

mv get_grades.dist Get_Grades
mkdir -p builds

zip -r -m $zip_location Get_Grades

rm get_grades.build -r

echo "created version $version"
