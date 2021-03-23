sudo apt install ssh

sudo mkdir /media/3tb

sudo chmod a+rwx /media/3tb

sudo nano /etc/fstab

#/dev/sdb1 /media/3tb auto defaults,auto 0 0

sudo add-apt-repository ppa:mythbuntu/31

sudo apt install mythtv

sudo mythfrontend

mythfrontend

#reboot at this point so that you and su will be added to the MythTV group

sudo shutdown -r now


