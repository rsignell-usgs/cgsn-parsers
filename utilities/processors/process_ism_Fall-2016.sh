#!/bin/bash -e
#
# Parse the various data files for a Coastal Surface Mooring.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 3 ]; then
    echo "$0: required inputs are the platform and deployment name, and"
    echo "the time flag for processing today's file (0) or N days prior"
    echo "     example: $0 ce02shsm D00001 0"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
TIME="-$3 day"
FNAME=`/bin/date -u +%Y%m%d --date="$TIME"`

PROC="/webdata/cgsn/data/proc"
PROCESS="/home/cgsnmo/dev/cgsn-parsers/utilities/processors"

# Set some instrument names and processing flags based on the platform name
case "$PLATFORM" in
    "ce01issm"  )
        MFN_FLAG=1
        declare -a OPTAA1=("None" "None")
        declare -a PCO2W1=("pco2w1" "PCO2WB/CGINS-PCO2WB-C0084__20160930")
        declare -a PHSEN1=("phsen1" "None")

        declare -a OPTAA2=("None" "None")
        declare -a PCO2W2=("pco2w2" "PCO2WB/CGINS-PCO2WB-C0053__20160930")
        declare -a PHSEN2=("phsen2" "None")
        ;;
    "ce06issm" )
        MFN_FLAG=1
        declare -a OPTAA1=("optaa1" "OPTAAD/CGINS-OPTAAD-00136__20160927")
        declare -a PCO2W1=("pco2w1" "PCO2WB/CGINS-PCO2WB-C0085__20160927")
        declare -a PHSEN1=("phsen1" "None")

        declare -a OPTAA2=("None" "None")
        declare -a PCO2W2=("pco2w2" "PCO2WB/CGINS-PCO2WB-C0081__20160927")
        declare -a PHSEN2=("None" "None")
        ;;
    * )
        echo "Unknown platform, please check the name again"
        exit 0 ;;
esac

# Buoy
#--> CTDBP + FLORT
#--> MOPAK
#--> UCSPP (acoustic modem communications with uCSPP)
#--> VELPT

# NSIF
#--> CTDBP + DOSTA
#--> FLORT
#--> NUTNR
for optaa in $PROC/$PLATFORM/$DEPLOY/nsif/optaa/$FNAME*.${OPTAA1[0]}.json; do
    if [ -e $optaa ]; then
        SIZE=`du -k "$optaa" | cut -f1`
        if [ $SIZE > 0 ]; then
            $PROCESS/process_optaa.sh $PLATFORM $DEPLOY "nsif/optaa" ${OPTAA1[1]} $optaa
        fi
    fi
done
$PROCESS/process_pco2w.sh $PLATFORM $DEPLOY "nsif/pco2w" ${PCO2W1[1]} $FNAME.${PCO2W1[0]}.json
$PROCESS/process_phsen.sh $PLATFORM $DEPLOY "nsif/phsen" $FNAME.${PHSEN1[0]}.json
#--> SPKIR
#--> VELPT

if [ $MFN_FLAG == 1 ]; then
    # MFN
    #--> ADCPT
    #--> CTDBP + DOSTA
    #--> CAMDS
    for optaa in $PROC/$PLATFORM/$DEPLOY/mfn/optaa/$FNAME*.${OPTAA2[0]}.json; do
        if [ -e $optaa ]; then
            SIZE=`du -k "$optaa" | cut -f1`
            if [ $SIZE > 0 ]; then
                $PROCESS/process_optaa.sh $PLATFORM $DEPLOY "mfn/optaa" ${OPTAA2[1]} $optaa
            fi
        fi
    done
    $PROCESS/process_pco2w.sh $PLATFORM $DEPLOY "mfn/pco2w" ${PCO2W2[1]} $FNAME.${PCO2W2[0]}.json
    $PROCESS/process_phsen.sh $PLATFORM $DEPLOY "mfn/phsen" $FNAME.${PHSEN2[0]}.json
    #--> PRESF
    #--> VEL3D
    #--> ZPLSC
fi
