#!/usr/bin/python

import subprocess
import sys

subprocess.check_call(
    ['vagrant',
     'plugin', 'install',
     'vagrant-service-manager']
)
output = subprocess.check_output(
    ['cd', '/root/adb/components/centos/centos-k8s-singlenode-setup', '&&',
     'vagrant', 'up', '&&',
     'vagrant', 'ssh', '-c', 'kubectl', 'get', 'nodes']
)

if "127.0.0.1" in output \
        and \
        "Ready" in output:
    print "Kubernetes successfully running in the Vagrant Box."
    sys.exit(0)
else:
    print "Kubernetes not running in the Vagrant Box."
    sys.exit(1)
