#!/bin/bash

systemctl start libvirtd
systemctl enable libvirtd
vagrant plugin install vagrant-service-manager
cat > /etc/yum.repos.d/virtualbox.repo <<- EOM
[virtualbox]
name=Oracle Linux / RHEL / CentOS-7 / x86_64 - VirtualBox
baseurl=http://download.virtualbox.org/virtualbox/rpm/el/7/x86_64
enabled=1
gpgcheck=1
gpgkey=https://www.virtualbox.org/download/oracle_vbox.asc

EOM
yum -y install VirtualBox-4.3
yum -y install @"Development Tools"
/etc/init.d/vboxdrv setup
mkdir /tmp/adb && cd /tmp/adb
git clone https://github.com/projectatomic/adb-atomic-developer-bundle.git .
cd components/centos/centos-k8s-singlenode-setup
vagrant up --provider virtualbox
vagrant ssh -c 'kubectl get nodes'
