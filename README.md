# Zcaler Sublocations Adder/Remover
:office: Adds or removes sublocations for existed parent locations on Zscaler platform

[Zscaler](https://www.zscaler.com/) Internet Access provides secure access to external applications. Script works through [API requests](https://help.zscaler.com/zia/api). 

**addSubs.py** 

Add a large number of sublocations to the network in Location Managment. The script sends post requests only for those parent locations where there are no specific sublocations. 
If sublocations already exist, then the script skips them and writes this data to the log file. Also you can track the progress of the task in the command line.

![pbar](https://github.com/teora13/Zcaler/blob/main/pbar.jpg)
        

**deleteSubs.py** 

Deleting sublocations is possible only with sending the parent's id to server. The script iterates through the list of locations and if their sublocations are in the list for deletion, then sends a delete request.

**deleteAll.py**

Delete filtered list of stores and their sublocations
