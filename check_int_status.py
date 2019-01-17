import csv
import re
import sqlite3
import time
import paramiko
import datetime
# This will connect to the SQLite database file provided on github.
# The database itself is nothing special; a new one may be created with the following SQL command: CREATE TABLE int_conn_counts (device_name,interface, connected_count, last_conn_date, UNIQUE(device_name,interface))
# You can change this to a custom folder location; be aware that slashes (\) need to be escaped with another slash (\\).
# Example C:\\users\\Administrator\\Desktop\\int_conn_counts.db
conn = sqlite3.connect('int_conn_counts.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()
int_regex = re.compile(r'Fa{1}\S*\d/\S*\d{1,2}|Gi{1}\S*\d/\S*\d|Eth{1}\d/\S*\d{1,2}')
# Provide credentials to log into your network equipment
username = "username"
password = "password"
# Provide path to CSV containing network inventory; the CSV file must have these two columns: Name,IP
devices = open('devices.csv', 'r', newline='')

def main():
    # create csv reader for devices.csv
    devices_read = csv.DictReader(devices)
    # create paramiko ssh client
    ssh_conn_def = paramiko.SSHClient()
    ssh_conn_def.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for devices_row in devices_read:
        ssh_conn_def.connect(devices_row['IP'], username=username, password=password,look_for_keys=False, allow_agent=False)
        ssh_conn = ssh_conn_def.invoke_shell()
        # send "show int status" command with filter for "notconnect" interfaces
        ssh_conn.send('term len 0\nshow int status | exc notconn\n')
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
            # if the regex pattern matches the current line of "show int status"
            if int_match:
                check = [devices_row['Name'], int_match.group()]
                # find matching row for device and interface in database
                c.execute(
                    "SELECT device_name,interface,connected_count FROM int_conn_counts WHERE device_name=? AND interface=?;",
                    (check[0], check[1]))
                prev_counts = c.fetchone()
                try:
                    # if the current line of the "show int status" input matches, increment count by 1
                    if check[0] == prev_counts['device_name'] and check[1] == prev_counts['interface']:
                        c.execute('''UPDATE int_conn_counts
                                 SET connected_count = connected_count+1, last_conn_date=?
                                 WHERE device_name=? AND interface=?;''',
                                  (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), check[0], check[1]))
                        conn.commit()
                except TypeError:
                    continue


main()
