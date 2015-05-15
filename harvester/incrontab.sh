#!/bin/bash -e

PLATFORM=${1,,}
DEPLOY=${2^^}

RAW="/home/ooiuser/data/raw"
HARVEST="/home/ooiuser/bin/cgsn-parsers/harvester"

# Coastal Surface Moorings -- CPM1
echo "$RAW/$PLATFORM/$DEPLOY/pwrsys IN_CLOSE_WRITE $HARVEST/harvest_pwrsys.sh $PLATFORM $DEPLOY \$#"
echo "$RAW/$PLATFORM/$DEPLOY/superv IN_CLOSE_WRITE $HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm1 \$#"

# Coastal Surface Moorings -- DCL11
echo "$RAW/$PLATFORM/$DEPLOY/dcl11/hyd1 IN_CLOSE_WRITE $HARVEST/harvest_hydrogen.sh $PLATFORM $DEPLOY dcl11 hyd1 \$#"
echo "$RAW/$PLATFORM/$DEPLOY/dcl11/metbk IN_CLOSE_WRITE $HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY \$#"
echo "$RAW/$PLATFORM/$DEPLOY/superv IN_CLOSE_WRITE $HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl11 \$#"

# Coastal Surface Moorings -- DCL12
echo "$RAW/$PLATFORM/$DEPLOY/dcl12/hyd2 IN_CLOSE_WRITE $HARVEST/harvest_hydrogen.sh $PLATFORM $DEPLOY dcl12 hyd2 \$#"
echo "$RAW/$PLATFORM/$DEPLOY/dcl12/wavss IN_CLOSE_WRITE $HARVEST/harvest_wavss.sh $PLATFORM $DEPLOY \$#"
echo "$RAW/$PLATFORM/$DEPLOY/superv IN_CLOSE_WRITE $HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl12 \$#"

# Coastal Surface Moorings -- CPM2
echo "$RAW/$PLATFORM/$DEPLOY/superv IN_CLOSE_WRITE $HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm2 \$#"

# Coastal Surface Moorings -- DCL26
echo "$RAW/$PLATFORM/$DEPLOY/superv IN_CLOSE_WRITE $HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl26 \$#"

# Coastal Surface Moorings -- DCL27
echo "$RAW/$PLATFORM/$DEPLOY/superv IN_CLOSE_WRITE $HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl27 \$#"

# Coastal Surface Moorings -- CPM3

# Coastal Surface Moorings -- DCL35
echo "$RAW/$PLATFORM/$DEPLOY/superv IN_CLOSE_WRITE $HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl35 \$#"

# Coastal Surface Moorings -- DCL37
echo "$RAW/$PLATFORM/$DEPLOY/superv IN_CLOSE_WRITE $HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl37 \$#"

