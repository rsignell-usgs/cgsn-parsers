Shell scripts used by OOI Endurance staff to harvest and parse raw data from
the surface moorings for monitoring purposes. The master harvester scripts are
used to call all of the associated harvesters for a particular mooring and
deployment. Scheduling is handled via crontab. Other users would need to modify
input and output paths for their applications.

There are several options for obtaining the raw data files. Endurance uses a
simple wget command (Linux command line utility, also available for Windows and
MacOS) to download all of the data for a deployment, scheduling its execution
via the use of crontab (Linux scheduler utility). An example wget command line
is shown below for downloading data from the Oregon Inshore Surface Mooring
Fall 2016 (D00006) deployment:

cd /home/ooiuser/data/raw
wget -Nr -np -p CE01ISSM/D00006 https://rawdata.oceanobservatories.org/files/CE01ISSM/D00006/

This will recursively download all the data for the Fall 2016 deployment,
updating previously downloaded data files each time it is called, if the source
data file is newer. 

Alternatively, one can load the cgsn_parsers as a module in python. Several
python utilities are available for accessing data directly over the Internet
passing it directly to the respective parser. 
