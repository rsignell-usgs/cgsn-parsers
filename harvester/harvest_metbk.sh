#!/bin/bash
#
# Read the raw METBK data files for the Endurance Coastal Surface Moorings and
# create parsed datasets available in Matlab formatted .MAT files for further
# processing and review.
#
# Wingard, C. 2015-04-17

# TODO: Convert this to accept input arguements for platform and deployment names

RAW="/home/nereus/data/Moorings/raw"
PARSED="/home/nereus/data/Moorings/parsed"

# CE02SHSM
OUT="$PARSED/ce02shsm/D00001/metbk"
for raw in $RAW/ce02shsm/D00001/cg_data/dcl11/metbk/*.log; do
    FILE=`basename $raw`
    python ../parsers/parse_metbk.py -i $raw -o $OUT/${FILE%.log}.mat
done

# CE04OSSM
OUT="$PARSED/ce04ossm/D00001/metbk"
for raw in $RAW/ce04ossm/D00001/cg_data/dcl11/metbk/*.log; do
    FILE=`basename $raw`
    python ../parsers/parse_metbk.py -i $raw -o $OUT/${FILE%.log}.mat
done

# CE07SHSM
OUT="$PARSED/ce07shsm/D00001/metbk"
for raw in $RAW/ce07shsm/D00001/cg_data/dcl11/metbk/*.log; do
    FILE=`basename $raw`
    python ../parsers/parse_metbk.py -i $raw -o $OUT/${FILE%.log}.mat
done

# CE02SHSM
OUT="$PARSED/ce09ossm/D00001/metbk"
for raw in $RAW/ce09ossm/D00001/cg_data/dcl11/metbk/*.log; do
    FILE=`basename $raw`
    python ../parsers/parse_metbk.py -i $raw -o $OUT/${FILE%.log}.mat
done
