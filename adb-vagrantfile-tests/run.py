#!/usr/bin/python

import json
import urllib
import subprocess
import sys
import os

url_base = "http://admin.ci.centos.org:8080"
api_key = os.environ['API_KEY']
count = os.environ['MACHINE_COUNT']
ver = "7"
arch = "x86_64"
req_url = "%s/Node/get?key=%s&ver=%s&arch=%s&i_count=%s" \
    % (url_base, api_key, ver, arch, count)

git_repo_url = os.environ['GIT_REPO_URL']
test_cmd = os.environ['TEST_CMD']

jsondata = urllib.urlopen(req_url).read()
data = json.loads(jsondata)

for host in data['hosts']:
    ssh_cmd = "ssh -t -t "
    ssh_cmd += "-o UserKnownHostsFile=/dev/null "
    ssh_cmd += "-o StrictHostKeyChecking=no "
    ssh_cmd += "root@%s " % (host)

    remote_cmd = "yum -y install centos-release-scl && "
    remote_cmd += "yum -y install sclo-vagrant1 git wget && "
    remote_cmd += "wget https://raw.githubusercontent.com/dharmit/adb-tests/adb-fix-195/adb-vagrantfile-tests/install.sh && chmod +x install.sh && "
    remote_cmd += "scl enable sclo-vagrant1 ./install.sh"

    cmd = '%s "%s"' % (ssh_cmd, remote_cmd)
    print("Running cmd: {}".format(cmd))
    exit_code = subprocess.call(cmd, shell=True)

    # Send a rest request to release the node
    done_nodes_url = "%s/Node/done?key=%s&ssid=%s" % (url_base, api_key, data['ssid'])
    print urllib.urlopen(done_nodes_url).read()
sys.exit(exit_code)
