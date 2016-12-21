#!/bin/bash -e
#
# Harvest and process the various data files for an Inshore Surface Mooring.
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
FNAME=`/bin/date -u +%Y%m%d --date="$TIME"`

RAW="/home/ooiuser/data/raw"
HARVEST="/home/ooiuser/bin/cgsn-parsers/utlities/harvesters"

# CPM1
$HARVEST/harvest_gps.sh $PLATFORM $DEPLOY $FNAME.gps.log
$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm1 0 $FNAME.superv.log

# DCL17
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl17 $FNAME.superv.log
$HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl17 ctdbp3 3 $FNAME.ctdbp3.log
for mopak in $RAW/$PLATFORM/$DEPLOY/dcl17/mopak/$FNAME*.mopak.log; do
    if [ -e $mopak ]; then
        SIZE=`du -k "$mopak" | cut -f1`
        if [ $SIZE > 0 ]; then
            $HARVEST/harvest_mopak.sh $PLATFORM $DEPLOY dcl17 $mopak
        fi
    fi
done
$HARVEST/harvest_velpt.sh $PLATFORM $DEPLOY dcl17 velpt1 $FNAME.velpt1.log

# DCL16
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl16 $FNAME.superv.log
$HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl16 ctdbp1 2 $FNAME.ctdbp1.log
$HARVEST/harvest_flort.sh $PLATFORM $DEPLOY dcl16 $FNAME.flort.log
$HARVEST/harvest_nutnr.sh $PLATFORM $DEPLOY dcl16 0 $FNAME.nutnr.log
$HARVEST/harvest_pco2w.sh $PLATFORM $DEPLOY dcl16 pco2w1 $FNAME.pco2w1.log
$HARVEST/harvest_phsen.sh $PLATFORM $DEPLOY dcl16 phsen1 $FNAME.phsen1.log
for optaa in $RAW/$PLATFORM/$DEPLOY/dcl16/optaa1/$FNAME*.optaa1.log; do
    if [ -e $optaa ]; then
        SIZE=`du -k "$optaa" | cut -f1`
        if [ $SIZE > 0 ]; then
            $HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY dcl16 optaa1 $optaa
        fi
    fi
done
$HARVEST/harvest_spkir.sh $PLATFORM $DEPLOY dcl16 $FNAME.spkir.log
$HARVEST/harvest_velpt.sh $PLATFORM $DEPLOY dcl16 velpt2 $FNAME.velpt2.log

# CPM3
$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm3 1 $FNAME.superv.log

# DCL35
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl35 $FNAME.superv.log
$HARVEST/harvest_adcp.sh $PLATFORM $DEPLOY dcl35 adcpt $FNAME.adcpt.log
$HARVEST/harvest_pco2w.sh $PLATFORM $DEPLOY dcl35 pco2w2 $FNAME.pco2w2.log
$HARVEST/harvest_phsen.sh $PLATFORM $DEPLOY dcl35 phsen2 $FNAME.phsen2.log
$HARVEST/harvest_presf.sh $PLATFORM $DEPLOY $FNAME.presf.log
for vel3d in $RAW/$PLATFORM/$DEPLOY/dcl35/vel3d/$FNAME*.vel3d.log; do
    if [ -e $vel3d ]; then
        SIZE=`du -k "$vel3d" | cut -f1`
        if [ $SIZE > 0 ]; then
            $HARVEST/harvest_vel3d.sh $PLATFORM $DEPLOY $vel3d
        fi
    fi
done

# DCL37
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl37 $FNAME.superv.log
$HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl37 ctdbp2 2 $FNAME.ctdbp2.log
for optaa in $RAW/$PLATFORM/$DEPLOY/dcl37/optaa2/$FNAME*.optaa2.log; do
    if [ -e $optaa ]; then
        SIZE=`du -k "$optaa" | cut -f1`
        if [ $SIZE > 0 ]; then
            $HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY dcl37 optaa2 $optaa
        fi
    fi
done
$HARVEST/harvest_zplsc.sh $PLATFORM $DEPLOY $FNAME.zplsc.log
