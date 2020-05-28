#!/bin/bash -x
# log user data output to /var/log/user-data.log
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo script start $(date)
export TERM=${TERM:-dumb}

# install EPEL repositories
yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm

# upgrade yum repo list
yum update -y

# install pihole prerequirements
yum install lighttpd-fastcgi php git whiptail procps -y

# workaround - set OS release to fedora
# there is no "unsupported OS" flag within the pihole installation script, so this is currently the easiest way
echo "fedora" > /etc/redhat-release

# set pihole dns server to cloudflare dns
mkdir /etc/pihole/
echo "PIHOLE_DNS_1=1.1.1.1" > /etc/pihole/setupVars.conf
echo "PIHOLE_DNS_1=1.0.0.1" > /etc/pihole/setupVars.conf
echo "DNSMASQ_LISTENING=all" > /etc/pihole/setupVars.conf

# install pihole unattended
wget -O /tmp/basic-install.sh https://install.pi-hole.net
bash /tmp/basic-install.sh --unattended

# set the pihole web ui password
/usr/local/bin/pihole -a -p @PASSWORD@

# upgrade packages
yum update -y

echo script stop $(date)
