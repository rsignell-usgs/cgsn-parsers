#!/bin/bash
#
# Read the parsed PCO2W data files from the Endurance Surface Moorings and create
# processed datasets available in JSON formatted files with the vendor factory
# calibration coefficients applied for further processing and review.
#
# C. Wingard 2017-01-24

# Parse the command line inputs
if [ $# -ne 5 ]; then
    echo "$0: required inputs are the platform and deployment names, the PCO2W"
    echo "directory name, the UID name of the stored factory calibration data,"
    echo "and the name of the file to process."
    echo ""
    echo "     example: $0 ce07shsm D00004 mfn/pco2w PCO2WB/CGINS-PCO2WB-C0082__20160921 20161012.pco2w.json"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
PCO2W=${3,,}
UID=${4^^}
CFILE=`/bin/basename $UID`
FILE=`/bin/basename $5`

# Set the default directory paths and input/output sources
BIN="/home/cgsnmo/dev/cgsn-parsers/cgsn_parsers/process"
PYTHON="/home/cgsnmo/anaconda3/envs/py27/bin/python"

PROC="/webdata/cgsn/data/proc"
IN="$PROC/$PLATFORM/$DEPLOY/$PCO2W/$FILE"
OUT="$PROC/$PLATFORM/$DEPLOY/$PCO2W/${FILE%.json}.proc.json"

COEFF="$PROC/$PLATFORM/$DEPLOY/$PCO2W/$CFILE.coeff"
BLANK="$PROC/$PLATFORM/$DEPLOY/$PCO2W/$CFILE.blank"
URL="https://github.com/ooi-integration/asset-management/raw/master/calibration/$UID.csv"

# Process the file
if [ -e $IN ]; then
    $PYTHON -m $BIN/proc_pco2w -i $IN -o $OUT -c $COEFF -d $BLANK -u $URL
fi
