## Cisco - Connected Interface Counts

####Please read to ensure these scripts run with intended functionality.

####Overview

These scripts will import a CSV file of Cisco switch names and IP addresses, log into each one, and determine if an interface is connected. For each connected interface, it will populate a row in a SQLite database file, increment a counter of how many times an interface has been found active, and record the date and time the port was last seen active.

This script is intended to be run as a scheduled task on an interval you see fit. The idea is to collect this data at a rate allowing you enough comfort to pull the cable from a switch port that may not be in use.

**These scripts are only intended to work with Cisco switches.**

####Requirements

-Python 3.x (it could work in 2.7 but I don't write code in Python2)
-Python library paramiko
-SSH access to your Cisco switches
-A single username and password with access to all devices in your devices.csv file

####Instructions

For your scheduled task, the seed_db.py file should be run first. This file populates the database with active interface names that the check_int_status.py script will increment counts for when observed active. If a new interface is found active after the initial seed_db.py pass, it will be added to the database.

**You must** create a CSV file with two columns: Names,IP 

The Names column is used to identify a device in the database. The IP is the management address the script will SSH into. This IP is not stored in the database. The name of the CSV file and its folder path can be customized within *__both scripts__*.
 
**You must** edit *__both scripts__* to provide credentials to your devices.

*__Any edits must be made in both scripts!__* I tried to be very descriptive with my comments in both scripts. I recommend reading the comments (#) in both scripts before setting up your scheduled task.

To access the data within the .db file, I recommend using <a href="https://sqlitebrowser.org/">DB Browser for SQLite</a>.