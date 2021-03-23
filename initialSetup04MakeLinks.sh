wget https://raw.githubusercontent.com/MythTV/mythtv/master/mythtv/contrib/user_jobs/mythlink.pl
chmod a+x mythlink.pl
/home/matt/mythtvutils/mythlink.pl

wget https://downloads.plex.tv/plex-media-server-new/1.22.1.4200-c073686f2/debian/plexmediaserver_1.22.1.4200-c073686f2_amd64.deb
sudo dpkg -i https://downloads.plex.tv/plex-media-server-new/1.22.1.4200-c073686f2/debian/plexmediaserver_1.22.1.4200-c073686f2_amd64.deb
echo "Visit http://localhost:32400/web to set up plex. Point a new library at <storageDir>/show_names directory"
