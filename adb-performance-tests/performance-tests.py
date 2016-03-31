#!/usr/bin/python

import subprocess


def vagrant_init():
    vagrant_init_cmd = "vagrant init projectatomic/adb"
    try:
        subprocess.check_call(
            "%s" % vagrant_init_cmd, shell=True
        )
    except:
        pass


def test_adb_bootup_time():
    bootup_cmd = "time vagrant up"
    try:
        output = subprocess.check_output("%s" % bootup_cmd, shell=True)
        print output
    except:
        pass

if __name__ == "__main__":
    vagrant_init()
    test_adb_bootup_time()
