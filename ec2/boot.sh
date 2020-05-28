#!/bin/bash -x
# log user data output to /var/log/user-data.log
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
export TERM=xterm-256color 
export environment=aws
echo script start $(date)

# install EPEL repositories
yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm

# upgrade yum repo list
yum update -y

# install pihole prerequirements
yum install lighttpd-fastcgi php git whiptail procps bind -y

# workaround - set OS release to fedora
# there is no "unsupported OS" flag within the pihole installation script, so this is currently the easiest way
echo "fedora" > /etc/redhat-release

# install pihole unattended
wget -O /tmp/basic-install.sh https://install.pi-hole.net
bash /tmp/basic-install.sh --unattended

# set pihole dns server to localhost
echo "PIHOLE_DNS_1=127.0.0.1#53" > /etc/pihole/setupVars.conf

# set the pihole web ui password
/usr/local/bin/pihole -a -p @PASSWORD@

echo script stop $(date)
