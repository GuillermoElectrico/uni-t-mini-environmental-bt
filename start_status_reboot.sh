#!/bin/bash

## Service or script to monitor if it is running 
SERVICE=read.py

while :
do
	result=$(ps ax|grep -v grep|grep $SERVICE)
#	echo ${#result}
	if [ ${#result} != 0 ] 
	then
		# everything is ok 
		# every 10 seconds we test if it is still ok 
		sleep 10
	else
		# is not working 
		# start script (in this case a python script) 
		screen -dm bash -c 'python3 /home/pi/uni-t-mini-environmental-bt/read.py'
		# we wait for it to load 
		sleep 10
	fi
done

#add in /etc/rc.local > /home/pi/uni-t-mini-environmental-bt/start_status_reboot.sh > /var/log/start_status_reboot.log &