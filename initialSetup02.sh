sudo apt install libhttp-cookies-perl

sudo apt install liblwp-protocol-https-perl

sudo apt install libjson-perl

wget https://raw.githubusercontent.com/shuaiscott/zap2xml/master/zap2xml.pl

chmod a+x zap2xml.pl

./zap2xml.pl -u <zap2it email> -p <zap2it password>

mythfilldatabase --only-update-guide --file --sourceid 1 --xmlfile xmltv.xml

crontab -e

#57 * * * * /home/matt/zap2xml.pl -u <> -p <> 

#58 * * * * mythfilldatabase --only-update-guide --file --sourceid 1 --xmlfile xmltv.xml
