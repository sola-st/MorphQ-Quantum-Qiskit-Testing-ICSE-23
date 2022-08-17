#!/bin/bash

# LOG THE ACTIVITY OF OTHER USERS
# This script is used to log the activity of other users.


# save the log to a file
echo "Logging the activity of other users"
echo "timestamp, username, pid, cpu, mem, process, time" > user_activities.txt
# every one minute, log the activity of other users
while true
do
    # print the activity of the top five processes with the timestamp
    timestamp=$(date +%s)
    echo "Timestamp log: $timestamp"
    ps ahux --sort=-c | awk -v date=$timestamp 'NR<=5{printf"%s,%s,%s,%.2f,%.2f,%s,%s\n",date,$1,$2,$3,$4,$11,$10}' >> user_activities.txt
    sleep 30
done