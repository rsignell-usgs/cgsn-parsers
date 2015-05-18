#!/bin/bash -e
#
# Harvest and process the various data files for an entire Coastal Surface
# Moorings.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 3 ]; then
    echo "$0: required inputs are the platform and deployment name, and"
    echo "the time flag for processing today's file or yesterday's"
    echo "     example: $0 ce01issm D00001 0"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
TIME="-$3 day"
FNAME=`date -u +%Y%m%d --date="$TIME"`

RAW="/home/ooiuser/data/raw"
HARVEST="/home/ooiuser/bin/cgsn-parsers/harvester"

# Set some instrument names and processing flags based on the platform name
case "$PLATFORM" in
    "ce02shsm" | "ce04ossm" )
        MFN_FLAG=0
        ADCP1="adcpt"
        CTDBP="ctdbp"
        OPTAA="optaa"
        PHSEN="phsen" ;;
    "ce07shsm" )
        MFN_FLAG=1
        ADCP1="adcpt1"
        ADCP2="adcpt2"
        CTDBP="ctdbp1"
        OPTAA="optaa1"
        PHSEN="phsen1" ;;
    "ce09ossm" )
        MFN_FLAG=1
        ADCP1="adcpt"
        ADCP2="adcps"
        CTDBP="ctdbp1"
        OPTAA="optaa1"
        PHSEN="phsen1" ;;
    * )
        echo "Unknown platform, please check the name again"
        exit 0 ;;
esac

# CPM1
$HARVEST/harvest_pwrsys.sh $PLATFORM $DEPLOY $FNAME.pwrsys.log
$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm1 0 $FNAME.superv.log

# DCL11
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl11 $FNAME.superv.log
$HARVEST/harvest_hydrogen.sh $PLATFORM $DEPLOY dcl11 hyd1 $FNAME.hyd1.log
$HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY $FNAME.metbk.log
# TODO: MOPAK
# TODO: VELPT1

# DCL12
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl12 $FNAME.superv.log
$HARVEST/harvest_hydrogen.sh $PLATFORM $DEPLOY dcl12 hyd2 $FNAME.hyd2.log
$HARVEST/harvest_wavss.sh $PLATFORM $DEPLOY $FNAME.wavss.log
# TODO: PCO2A
# TODO: FDCHP

# CPM2
$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm2 1 $FNAME.superv.log

# DCL26
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl26 $FNAME.superv.log
$HARVEST/harvest_adcp.sh $PLATFORM $DEPLOY dcl26 $ADCP1 $FNAME.$ADCP1.log
# TODO: NUTNR
# TODO: PHSEN
# TODO: SPKIR
# TODO: VELPT2

# DCL27
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl27 $FNAME.superv.log
$HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl27 $CTDBP 1 $FNAME.$CTDBP.log
# TODO: DOSTA
# TODO: FLORT
# TODO: OPTAA

# Washington MFN
if [ $MFN_FLAG == 1 ]; then
    # CPM3
    $HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm3 1 $FNAME.superv.log    
    
    # DCL35
    $HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl35 $FNAME.superv.log
    $HARVEST/harvest_adcp.sh $PLATFORM $DEPLOY dcl35 $ADCP2 $FNAME.$ADCP2.log
    #TODO: PCO2W
    #TODO: PHSEN
    #TODO: PRESF
    #TODO: VEL3D
    
    # DCL37
    $HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl37 $FNAME.superv.log
    $HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl37 $CTDBP 2 $FNAME.$CTDBP.log
    #TODO: OPTAA
    #TODO: ZPLSC
fi
