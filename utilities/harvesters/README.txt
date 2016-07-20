Shell scripts used by OOI Endurance staff to harvest and parse data from the
moorings for monitoring purposes. The master harvester scripts are used to
call all of the associated harvesters for a particular mooring/deployment.
Scheduling is handled via crontab. Other users would need to modify input and
output paths for their applications.

These scripts are provided as an example for how to use these parsers.
Alternatively, one can load the cgsn_parsers as a module in python and call the
respective parsers needed in that manner.
