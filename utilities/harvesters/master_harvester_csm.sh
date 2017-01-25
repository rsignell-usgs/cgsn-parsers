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

RAW="/webdata/cgsn/data/raw"
HARVEST="/home/cgsnmo/dev/cgsn-parsers/utilities/harvesters"

# Set some instrument names and processing flags based on the platform name
case "$PLATFORM" in
    "ce02shsm" | "ce04ossm" )
        MFN_FLAG=0
        ADCP1="adcpt"
        CTDBP1="ctdbp"
        OPTAA1="optaa"
        PHSEN1="phsen" ;;
    "ce07shsm"  )
        MFN_FLAG=1
        ADCP1="adcpt1"
        ADCP2="adcpt2"
        CTDBP1="ctdbp1"
        CTDBP2="ctdbp2"
        OPTAA1="optaa1"
        OPTAA2="optaa2"
        PHSEN1="phsen1"
        PHSEN2="phsen2" ;;
    "ce09ossm" )
        MFN_FLAG=1
        ADCP1="adcpt"
        ADCP2="adcps"
        CTDBP1="ctdbp1"
        CTDBP2="ctdbp2"
        OPTAA1="optaa1"
        OPTAA2="optaa2"
        PHSEN1="phsen1"
        PHSEN2="phsen2" ;;
    * )
        echo "Unknown platform, please check the name again"
        exit 0 ;;
esac

# CPM1
$HARVEST/harvest_gps.sh $PLATFORM $DEPLOY $FNAME.gps.log
$HARVEST/harvest_pwrsys.sh $PLATFORM $DEPLOY $FNAME.pwrsys.log
$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm1 0 $FNAME.superv.log

# DCL11
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl11 $FNAME.superv.log
$HARVEST/harvest_hydgn.sh $PLATFORM $DEPLOY dcl11 hyd1 $FNAME.hyd1.log
$HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY $FNAME.metbk.log
for mopak in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl11/mopak/$FNAME*.mopak.log; do
    if [ -e $mopak ]; then
        SIZE=`du -k "$mopak" | cut -f1`
        if [ $SIZE > 0 ]; then
            $HARVEST/harvest_mopak.sh $PLATFORM $DEPLOY dcl11 $mopak
        fi
    fi
done
$HARVEST/harvest_velpt.sh $PLATFORM $DEPLOY dcl11 velpt1 $FNAME.velpt1.log

# DCL12
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl12 $FNAME.superv.log
$HARVEST/harvest_hydgn.sh $PLATFORM $DEPLOY dcl12 hyd2 $FNAME.hyd2.log
$HARVEST/harvest_wavss.sh $PLATFORM $DEPLOY $FNAME.wavss.log
$HARVEST/harvest_pco2a.sh $PLATFORM $DEPLOY $FNAME.pco2a.log
$HARVEST/harvest_fdchp.sh $PLATFORM $DEPLOY $FNAME.fdchp.log

# CPM2
$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm2 1 $FNAME.superv.log

# DCL26
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl26 $FNAME.superv.log
$HARVEST/harvest_adcp.sh $PLATFORM $DEPLOY dcl26 $ADCP1 $FNAME.$ADCP1.log
$HARVEST/harvest_nutnr.sh $PLATFORM $DEPLOY dcl26 1 $FNAME.nutnr.log
$HARVEST/harvest_phsen.sh $PLATFORM $DEPLOY dcl26 $PHSEN1 $FNAME.$PHSEN1.log
$HARVEST/harvest_spkir.sh $PLATFORM $DEPLOY dcl26 $FNAME.spkir.log
$HARVEST/harvest_velpt.sh $PLATFORM $DEPLOY dcl26 velpt2 $FNAME.velpt2.log

# DCL27
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl27 $FNAME.superv.log
$HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl27 $CTDBP1 1 $FNAME.$CTDBP1.log
$HARVEST/harvest_dosta.sh $PLATFORM $DEPLOY $FNAME.dosta.log
$HARVEST/harvest_flort.sh $PLATFORM $DEPLOY dcl27 $FNAME.flort.log
for optaa in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl27/$OPTAA1/$FNAME*.$OPTAA1.log; do
    if [ -e $optaa ]; then
        SIZE=`du -k "$optaa" | cut -f1`
        if [ $SIZE > 0 ]; then
            $HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY dcl27 $OPTAA1 $optaa
        fi
    fi
done

# Washington MFN
if [ $MFN_FLAG == 1 ]; then
    # CPM3
    $HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm3 1 $FNAME.superv.log

    # DCL35
    $HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl35 $FNAME.superv.log
    $HARVEST/harvest_adcp.sh $PLATFORM $DEPLOY dcl35 $ADCP2 $FNAME.$ADCP2.log
    $HARVEST/harvest_pco2w.sh $PLATFORM $DEPLOY dcl35 pco2w $FNAME.pco2w.log
    $HARVEST/harvest_phsen.sh $PLATFORM $DEPLOY dcl35 $PHSEN2 $FNAME.$PHSEN2.log
    $HARVEST/harvest_presf.sh $PLATFORM $DEPLOY $FNAME.presf.log
    for vel3d in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl35/vel3d/$FNAME*.vel3d.log; do
        if [ -e $vel3d ]; then
            SIZE=`du -k "$vel3d" | cut -f1`
            if [ $SIZE > 0 ]; then
                $HARVEST/harvest_vel3d.sh $PLATFORM $DEPLOY $vel3d
            fi
        fi
    done

    # DCL37
    $HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl37 $FNAME.superv.log
    $HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl37 $CTDBP2 2 $FNAME.$CTDBP2.log
    for optaa in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl37/$OPTAA2/$FNAME*.$OPTAA2.log; do
        if [ -e $optaa ]; then
            SIZE=`du -k "$optaa" | cut -f1`
            if [ $SIZE > 0 ]; then
                $HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY dcl37 $OPTAA2 $optaa
            fi
        fi
    done
    $HARVEST/harvest_zplsc.sh $PLATFORM $DEPLOY $FNAME.zplsc.log
fi
