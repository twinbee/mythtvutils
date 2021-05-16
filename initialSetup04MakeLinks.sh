wget https://raw.githubusercontent.com/MythTV/mythtv/master/mythtv/contrib/user_jobs/mythlink.pl
chmod a+x mythlink.pl
/home/matt/mythtvutils/mythlink.pl --format %T/%T\ -\ %oY.%om.%od\ -\ %S

#install plex
echo "wget <latest plex link>"
wget https://downloads.plex.tv/plex-media-server-new/1.22.1.4228-724c56e62/debian/plexmediaserver_1.22.1.4228-724c56e62_amd64.deb
echo sudo dpkg -i plexmediaserver_1.22.1.4228-724c56e62_amd64.deb
echo "http://hostname:32400/web"

 
