#!/usr/bin/python

import subprocess
import sys


def main():
    try:
        # vagrant-service-manager plugin is required to boot up ADB box
        subprocess.check_call(
            ['vagrant', 'plugin', 'install', 'vagrant-service-manager']
        )

        # ADB repo is cloned to /root/adb using Ansible
        subprocess.check_call(
            ['vagrant', 'up'],
            cwd='/root/adb/components/centos/centos-k8s-singlenode-setup'
        )

        # Check if k8s is properly setup
        output = subprocess.check_output(
            ['vagrant', 'ssh', '-c', '%s' % "kubectl get nodes"],
            cwd="/root/adb/components/centos/centos-k8s-singlenode-setup"
        )

        # Destroy vagrant box
        subprocess.check_call(
            ['vagrant', 'destroy', '-f'],
            cwd="/root/adb/components/centos/centos-k8s-singlenode-setup"
        )

    except subprocess.CalledProcessError as e:
        print ("Command '%s' exited with exit status %d." %
               (e.cmd, e.returncode))
        sys.exit(e.returncode)

    if "127.0.0.1" in output \
            and \
            "Ready" in output:
        print "Kubernetes successfully running in the Vagrant box."
        sys.exit(0)
    else:
        print "Kubernetes not running in the Vagrant box."
        sys.exit(1)

if __name__ == "__main__":
    main()
