# Zcaler Sublocation Adder/Remover
:office: Adds or removes sublocations for existed parent locations in Zscaler platform

[Zscaler](https://www.zscaler.com/) Internet Access provides secure access to external applications. 

If necessary, add a large number of sublocations to the network in Location Managment. The script sends post requests only for those parent locations where there are no specific sublocations. 

If sublocations already exist, then the script skips them and writes this data to the log file. Also you can track the progress of the task in the command line.
