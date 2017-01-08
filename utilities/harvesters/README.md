# Harvesters

Shell scripts used by OOI Endurance staff to harvest and parse data from the
moorings for monitoring purposes. The master harvester scripts are used to
call all of the associated harvesters for a particular mooring/deployment.
Scheduling is handled via crontab. Other users would need to modify input and
output paths for their own applications.

These scripts are provided as one example for how to use these parsers.
Alternatively, one can load the cgsn_parsers as a module in python and call the
respective parsers needed in that manner. The user will need to create their own
methodologies for loading the data files.

# Raw Data

The raw data needs to be downloaded to your machine prior to working with these
parsers. I've included an example below of the crontab OOI Endurance uses to
access the raw data for mooring monitoring and managing purposes. Note, I find
it much easier to limit the wget calls to a specific mooring and deployment.
Otherwise it just takes too long.

```bash
# OOI Endurance crontab
HOME=/home/ooiuser
SHELL=/bin/bash
MAILTO=aserver@somewhere.com
CRON_TZ=UTC

# Set deployment numbers for the moorings
CE01="D00006"
CE02="D00004"
CE04="D00003"
CE06="D00005"
CE07="D00004"
CE09="D00004"

# copy data from the rawdata server for each mooring
WGET_ISSM="/usr/bin/wget -rN -np -nv -nH --cut-dirs=3 -e robots=off -R index.html* --no-check-certificate"
WGET_CSM="/usr/bin/wget -rN -np -nv -nH --cut-dirs=4 -e robots=off -R index.html* --no-check-certificate"
URL="https://rawdata.oceanobservatories.org/files"
0 */6 * * *   cd $HOME/data/raw/ce01issm/$CE01; $WGET_ISSM $URL/CE01ISSM/$CE01/ > /dev/null
0 */6 * * *   cd $HOME/data/raw/ce02shsm/$CE02; $WGET_CSM $URL/CE02SHSM/$CE02/cg_data/ > /dev/null
0 */6 * * *   cd $HOME/data/raw/ce04ossm/$CE04; $WGET_CSM $URL/CE04OSSM/$CE04/cg_data/ > /dev/null
0 */6 * * *   cd $HOME/data/raw/ce06issm/$CE06; $WGET_ISSM $URL/CE06ISSM/$CE06/ > /dev/null
0 */6 * * *   cd $HOME/data/raw/ce07shsm/$CE07; $WGET_CSM $URL/CE07SHSM/$CE07/cg_data/ > /dev/null
0 */6 * * *   cd $HOME/data/raw/ce09ossm/$CE09; $WGET_CSM $URL/CE09OSSM/$CE09/cg_data/ > /dev/null

# process the daily log files, today's file and the last part of yesterday (try twice)
30 */6 * * *    $HOME/bin/cgsn-parsers/harvester/master_harvester_ism.sh ce01issm $CE01 0 > /dev/null
30 0,6 * * *    $HOME/bin/cgsn-parsers/harvester/master_harvester_ism.sh ce01issm $CE01 1 > /dev/null

30 */6 * * *    $HOME/bin/cgsn-parsers/harvester/master_harvester_csm.sh ce02shsm $CE02 0 > /dev/null
30 0,6 * * *    $HOME/bin/cgsn-parsers/harvester/master_harvester_csm.sh ce02shsm $CE02 1 > /dev/null

30 */6 * * *    $HOME/bin/cgsn-parsers/harvester/master_harvester_csm.sh ce04ossm $CE04 0 > /dev/null
30 0,6 * * *    $HOME/bin/cgsn-parsers/harvester/master_harvester_csm.sh ce04ossm $CE04 1 > /dev/null

30 */6 * * *    $HOME/bin/cgsn-parsers/harvester/master_harvester_ism.sh ce06issm $CE06 0 > /dev/null
30 0,6 * * *    $HOME/bin/cgsn-parsers/harvester/master_harvester_ism.sh ce06issm $CE06 1 > /dev/null

30 */6 * * *    $HOME/bin/cgsn-parsers/harvester/master_harvester_csm.sh ce07shsm $CE07 0 > /dev/null
30 0,6 * * *    $HOME/bin/cgsn-parsers/harvester/master_harvester_csm.sh ce07shsm $CE07 1 > /dev/null

30 */6 * * *    $HOME/bin/cgsn-parsers/harvester/master_harvester_csm.sh ce09ossm $CE09 0 > /dev/null
30 0,6 * * *    $HOME/bin/cgsn-parsers/harvester/master_harvester_csm.sh ce09ossm $CE09 1 > /dev/null
```
