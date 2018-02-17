#!/bin/bash
# Shell-guy to monitor a process (0~0)
#<monitor_agent.sh> "service_name"
echo "|----------------------------------------------------------------------|"
echo "| Enter the service name you like to Monitor:__________________________|"
echo "|----------------------------------------------------------------------|"
service=$1
if [ "$(systemctl status $service | grep -c "active (running)")" -gt 0 ];then
   echo "$service is running !!"
elif [ "$(systemctl status $service | grep -c "active (running)")" -eq 0 ];then
   echo "$service is not running"
   $service restart
   if [ "$(systemctl status $service | grep -c "active (running)")" -lt 1 ];then
     $service restart
   elif [ "$(systemctl status $service | grep -c "active (running)")" -eq 0 ];then
     echo "The service is not found!!"
   fi
fi
