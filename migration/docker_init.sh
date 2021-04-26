#!/bin/bash

sed -i 's/bind 127.0.0.1 ::1/bind 127.0.0.1/' /etc/redis/redis.conf
sed -i "s/dbpath=.*/dbpath=\/data\/mongodb/" /etc/mongodb.conf


mkdir -p /data/mongodb /data/log /data/logs
chmod -R a+wr /data/mongodb
chmod -R 777 /opt/Vulcan/app/plugins
service mongodb restart
service redis-server restart
cd /opt/Vulcan


nohup  python3.7 Vulcan.py >> /data/log/web.txt 2>&1 &

nohup  celery worker -P threads -A celerywing.tasks -B -E  --loglevel=info -n work1 >> /data/log/work1.txt 2>&1 &
nohup  celery worker -P threads -A celerywing.tasks -B -E  --loglevel=info -n work2 >> /data/log/work2.txt 2>&1 &

time=$(date "+%Y%m%d-%H%M%S")

nohup  app/plugins/xray/xray_linux_amd64 webscan --listen 127.0.0.1:1664 --webhook-output http://127.0.0.1:5000/webhook --html-output "${time}".html  >> /data/log/xraylog.txt 2>&1 &


nohup  python3.7 -m http.server 6000 >> /data/log/httplog.txt 2>&1 &

/bin/bash