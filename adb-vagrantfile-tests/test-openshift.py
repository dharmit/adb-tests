#!/usr/bin/python

import subprocess
import unittest
from unittest import TestCase


class OpenShiftTests(TestCase):
    """This class tests Openshift on ADB box."""

    def test_01_service_manager_install(self):
        """Install required plugins."""
        # vagrant-service-manager plugin is required to boot up ADB box
        subprocess.check_call(
            ['vagrant', 'plugin', 'install', 'vagrant-service-manager']
        )

    def test_02_VagrantUp(self):
        """Check if vagrant up succeeds."""
        try:
            # ADB repo is cloned to /root/adb using Ansible
            exit_code = subprocess.check_call(
                ['vagrant', 'up'],
                cwd='/root/adb/components/centos/centos-k8s-singlenode-setup'
            )
        except:
            pass
        self.assertEqual(exit_code, 0)

    def test_03_VagrantSSH(self):
        """Check if k8s is properly setup."""
        # Dirty hack to ensure below check doesn't fail due to service taking
        # time to start
        subprocess.call(["sleep", "5"])
        try:
            output = subprocess.check_output(
                ['vagrant', 'ssh', '-c', '%s' % "kubectl get nodes"],
                cwd="/root/adb/components/centos/centos-k8s-singlenode-setup"
            )
        except:
            pass
        self.assertIn('127.0.0.1', output.split())
        self.assertIn('Ready', output.split())

    def test_04_VagrantDestroy(self):
        """Check force destroy vagrant box."""
        try:
            exit_code = subprocess.check_call(
                ['vagrant', 'destroy', '-f'],
                cwd="/root/adb/components/centos/"
                "centos-k8s-singlenode-setup"
            )
        except:
            pass
        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
