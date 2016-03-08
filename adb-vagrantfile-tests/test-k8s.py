#!/usr/bin/python

import subprocess
import sys

subprocess.check_call(
    ['vagrant',
     'plugin', 'install',
     'vagrant-service-manager']
)
subprocess.check_call(
    ['cd', '/root/adb/components/centos/centos-k8s-singlenode-setup']
)
subprocess.check_call(
    ['vagrant', 'up']
)

output = subprocess.check_output(
    ['vagrant',
     'ssh', '-c', 'kubectl', 'get', 'nodes']

if "127.0.0.1" in output \
    and \
    "Ready" in output:
    sys.exit(0)
else:
    sys.exit(1)
