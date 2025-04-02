#!/bin/bash
#run this as mythtv

# prerequisite
#sudo apt install xmltv
# http://<mythtv>:6544 under source, select schedules Direct

#then interactively go through 
#tv_grab_zz_sdjson --configure

tv_grab_zz_sdjson --output mythtv_test.xml --days 1 --config-file ~/.mythtv/s4.xmltv

#make a backup of the db
#mysqldump --no-tablespaces -u mythtv -p mythconverg > mythconverg_backup_prior2channelxml.sql

grep '<channel id=' -A1 mythtv_test.xml |   sed -n 's/.*<channel id="\([^"]*\)".*/\1:/p; s/.*<display-name>\(.*\)<\/display-name>.*/\1/p' |   paste - - > xmltv_channels.txt
cat xmltv_channels.txt 

while IFS=':' read -r xmltvid display; do
	clean_display=$(echo "$display" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
	clean_display=$(echo "$clean_display" | sed "s/'/\\'/g");   
	echo "UPDATE channel SET xmltvid='$xmltvid' WHERE name LIKE '%$clean_display%' OR callsign LIKE '%$clean_display%';"; done < xmltv_channels.txt > update_xmltvid.sql

#check the file
cat update_xmltvid.sql
mysql -u mythtv -p mythconverg < update_xmltvid.sql
mythfilldatabase 

#be sure to add mythfilldatabase to crontab
#sudo crontab -e
