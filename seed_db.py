import csv
import re
import sqlite3
import time
import paramiko
# This will connect to the SQLite database file provided on github.
# The database itself is nothing special; a new one may be created with the following SQL command: CREATE TABLE int_conn_counts (device_name,interface,connected_count) 
# You can change this to a custom folder location; be aware that slashes (\) need to be escaped with another slash (\\).
# Example C:\\users\\Administrator\\Desktop\\int_conn_counts.db
conn = sqlite3.connect('int_conn_counts.db')
c = conn.cursor()
int_regex = re.compile(r'Fa{1}\S*\d/\S*\d{1,2}|Gi{1}\S*\d/\S*\d|Eth{1}\d/\S*\d{1,2}')
# Provide credentials to log into your network equipment
username = "username"
password = "password"
# Provide path to CSV containing network inventory; the CSV file must have these two columns: Name,IP
devices = open('devices.csv', 'r', newline='')

def main():
    # create reader for CSV inventory
    devices_read = csv.DictReader(devices)
    # create paramiko ssh client
    ssh_conn_def = paramiko.SSHClient()
    ssh_conn_def.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for devices_row in devices_read:
        ssh_conn_def.connect(devices_row['IP'], username=username, password=password,look_for_keys=False, allow_agent=False)
        ssh_conn = ssh_conn_def.invoke_shell()
        # send "show int status" command with filter for "notconnect" interfaces
        ssh_conn.send('term len 0\nshow int status\n')
        time.sleep(.5)
        # receive output of "show int status" command
        int_statuses = ssh_conn.recv(10000)
        # close SSH connection to current IP Address
        ssh_conn_def.close()
        int_statuses = int_statuses.decode('utf-8')
        # for each line of the "show int status" output
        for int_status_line in int_statuses.splitlines():
            # regex search each line for interface name pattern
            int_match = re.search(int_regex, int_status_line)
            # if the regex pattern matches the current line of "show int status", insert a row into the db
            if int_match:
                int_counts = [(devices_row['Name']), int_match.group(), 0]
                c.executemany("INSERT INTO int_conn_counts VALUES (?,?,?,null)", (int_counts,))
                conn.commit()

main()