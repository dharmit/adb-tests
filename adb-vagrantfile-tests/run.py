#!/usr/bin/python

import json
import urllib
import subprocess
import sys
import os
import re


regex_for_vagrantfile = re.compile("components/centos/.*/Vagrantfile")


def run(modified_files):
    """Request for nodes and execute tests on them."""
    # TODO: This could be split into multiple functions

    modified_custom_vagrantfiles = parse_modified_files(modified_files)
    providers = providers_to_test(modified_custom_vagrantfiles)

    url_base = "http://admin.ci.centos.org:8080"
    api_key = os.environ['API_KEY']
    count = os.environ['MACHINE_COUNT']
    ver = "7"
    arch = "x86_64"
    req_url = "%s/Node/get?key=%s&ver=%s&arch=%s&count=%s" \
        % (url_base, api_key, ver, arch, count)

    ansible_repo_url = os.environ['ANSIBLE_REPO_URL']
    # test_cmd = os.environ['TEST_CMD']

    # jsondata = urllib.urlopen(req_url).read()
    # data = json.loads(jsondata)

    # for host in data['hosts']:
    for provider in providers:
        jsondata = urllib.urlopen(req_url).read()
        data = json.loads(jsondata)
        host = data['hosts'][0]

        ssh_cmd = "ssh -t -t "
        ssh_cmd += "-o UserKnownHostsFile=/dev/null "
        ssh_cmd += "-o StrictHostKeyChecking=no "
        ssh_cmd += "root@%s " % (host)

        remote_cmd = "yum -y install git && "
        remote_cmd += "git clone %s && " % ansible_repo_url
        remote_cmd += "cd adb-ci-ansible && ./install.sh && "
        remote_cmd += "test-adb.py"

        cmd = '%s "%s"' % (ssh_cmd, remote_cmd)
        print("Running cmd: {}".format(cmd))
        exit_code = subprocess.call(cmd, shell=True)

        # Send a rest request to release the node
        done_nodes_url = "%s/Node/done?key=%s&ssid=%s" % (url_base, api_key,
                                                          data['ssid'])
        print urllib.urlopen(done_nodes_url).read()
    sys.exit(exit_code)


def providers_to_test(modified_custom_vagrantfiles):
    """Parse providers (OpenShift, K8s, Docker) that need to be tested."""
    providers = []

    for _ in modified_custom_vagrantfiles:
        providers.append(_.split('/')[2].split('-')[1])

    return providers


def parse_modified_files(modified_files):
    """Parse modified files into a list of custom Vagrantfiles."""
    modified_custom_vagrantfiles = []
    for _ in modified_files:
        is_modified = regex_for_vagrantfile.match(_)

        if is_modified:
            modified_custom_vagrantfiles.append(
                is_modified.group()
            )
        else:
            continue
    return modified_custom_vagrantfiles


def git_diff_tree():
    """Return a list of files that got modified in the PR."""
    files = subprocess.check_output(['git', 'diff-tree', '--no-commit-id',
                                     '--name-only', '-r', "%s" %
                                     (os.environ['ghprbActualCommit'])])
    return files.split("\n")


def is_any_custom_vagrantfile_modified():
    """Check if any custom vagrantfile is modified."""
    modified_files = git_diff_tree()

    for _ in modified_files:
        if regex_for_vagrantfile.match(_):
            return modified_files
        else:
            continue
    return False


if __name__ == "__main__":
    modified_files = is_any_custom_vagrantfile_modified()
    if modified_files:
        run(modified_files)
    else:
        # This block is executed when no custom Vagrantfile is modified in a PR
        sys.exit(0)
