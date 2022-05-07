#!/bin/sh
 
pids=`ps -ef|awk '{if($3=='$1'){print $2} }'`;
	
if [ -n "$pids" ]; then
	for pid in $pids
	do
	sudo kill -s 9 $pid
	done
fi

sudo kill -s 9 $1