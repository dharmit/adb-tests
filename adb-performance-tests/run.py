#!/usr/bin/python

import os
import json
import urllib
import subprocess
import sys


url_base = "http://admin.ci.centos.org:8080"
api_key = os.environ['API_KEY']
count = os.environ['MACHINE_COUNT']
ver = "7"
arch = "x86_64"
req_url = "%s/Node/get?key=%s&ver=%s&arch=%s&count=%s" % \
    (url_base, api_key, ver, arch, count)

ansible_repo_url = os.environ['ANSIBLE_REPO_URL']
test_cmd = os.environ['TEST_CMD']

jsondata = urllib.urlopen(req_url).read()

data = json.loads(jsondata)

for host in data['hosts']:
    ssh_cmd = "ssh -t -t "
    ssh_cmd += "-o UserKnownHostsFile=/dev/null "
    ssh_cmd += "-o StrictHostKeyChecking=no "
    ssh_cmd += "root@%s " % (host)

    ansible_cmd = 'yum -y install git && '
    ansible_cmd += 'git clone %s &&' % ansible_repo_url
    ansible_cmd += 'cd adb-ci-ansible && ./install-ansible.sh &&'
    ansible_cmd += 'ansible-playbook install-adb.yml --extra-vars \
        "adb_tests_dharmit=true"'

    cmd = '%s "%s"' % (ssh_cmd, ansible_cmd)

    exit_code = subprocess.call(cmd, shell=True)
    if exit_code != 0:
        sys.exit("Ansible command failed")

    # actual tests
    remote_cmd = '/bin/bash -c ' + test_cmd

    cmd = '%s "%s"' % (ssh_cmd, remote_cmd)

    exit_code = subprocess.call(cmd, shell=True)
    if exit_code != 0:
        sys.exit("Tests failed")

    done_nodes_url = "%s/Node/done?key=%s&sside=%s" % \
        (url_base, api_key, data['ssid'])

    print urllib.urlopen(done_nodes_url)
