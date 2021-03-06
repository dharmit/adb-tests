#!/bin/bash
# vim: dict+=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of vagrant/service-manager/sanity
#   Description: test service-manager vagrant plugin
#   Author: Ondrej Ptak <optak@redhat.com>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2015 Red Hat, Inc.
#
#   This copyrighted material is made available to anyone wishing
#   to use, modify, copy, or redistribute it subject to the terms
#   and conditions of the GNU General Public License version 2.
#
#   This program is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE. See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public
#   License along with this program; if not, write to the Free
#   Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#   Boston, MA 02110-1301, USA.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Include Beaker environment
. /usr/share/beakerlib/beakerlib.sh || exit 1


rlJournalStart
    rlPhaseStartSetup
        rlImport 'testsuite/vagrant' || rlDie
        vagrantBoxIsProvided || rlDie
        vagrantBoxAdd || rlDie
        vagrantPluginInstall vagrant-service-manager
        vagrantConfigureGeneralVagrantfile skip
    rlPhaseEnd

for dir in $vagrant_VAGRANTFILE_DIRS;do
    rlPhaseStartTest testing_with_$dir
        #rhel-ose_found=false
        #for dir in $vagrant_VAGRANTFILE_DIRS; do
        #    if `echo $dir | grep "rhel-ose$"`; then
        #        rhel-ose_found=true
        #        break
        #    fi
        #done
        #if [ "$rhel-ose_found" == false ]; then
        #    rlDie "test do not have Vagrantfile for rhel-ose
        rlRun "pushd $dir"
        rlLogInfo "Testing without running VM"
        rlRun "vagrant service-manager env docker > stdout 2> stderr" 1-255
        echo -e "stdout:\n========"
        cat stdout
        echo -e "stderr:\n========"
        cat stderr
        echo "========"
        rlAssertNotGrep '.' stdout
        #rlAssertGrep "target machine is required to run" stderr
        rlAssertGrep "The virtual machine must be running before you execute this command." stderr

        rlLogInfo "Testing with running VM"
        rlRun "vagrant up --provider $vagrant_PROVIDER"
        rlRun "vagrant ssh -c 'echo hello' | grep hello"

        rlLogInfo "Testing env docker"
        rlRun "vagrant service-manager env docker > stdout 2> stderr"
        echo -e "stdout:\n========"
        cat stdout
        echo -e "stderr:\n========"
        cat stderr
        echo "========"
        rlAssertNotGrep "." stderr
        rlAssertGrep "DOCKER_HOST.tcp://[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*:[0-9]*" stdout
        if [ "$HOST_PLATFORM" == "win" ]; then
            set -x
            rlAssertGrep "DOCKER_CERT_PATH.*\.vagrant\\\\machines\\\\default\\\\${vagrant_PROVIDER}\\\\docker" stdout
            set +x
        else
            rlAssertGrep "DOCKER_CERT_PATH.*\.vagrant/machines/default/${vagrant_PROVIDER}/docker" stdout
        fi
        rlAssertGrep "DOCKER_TLS_VERIFY.1" stdout
        rlAssertGrep "DOCKER_API_VERSION.[0-9]\.[0-9]\+" stdout
        rlAssertNotGrep "setx" stdout
        rlAssertGrep "export" stdout
        if [ "$HOST_PLATFORM" == "win" ]; then
            rlAssertGrep "eval \"\$(VAGRANT_NO_COLOR=1 vagrant service-manager env docker \| tr -d '\r')\"" stdout
        else
            rlAssertGrep 'eval "$(vagrant service-manager env docker)' stdout
        fi

        rlLogInfo "Testing env openshift"
        rlRun "vagrant service-manager env openshift > stdout 2> stderr"
        echo -e "stdout:\n========"
        cat stdout
        echo -e "stderr:\n========"
        cat stderr
        echo "========"
        rlAssertNotGrep "." stderr
        rlAssertGrep "https://[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+:[0-9]\+/console" stdout
        rlAssertGrep "oc login https://[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+:[0-9]\+" stdout

        rlLogInfo "Testing box version"
        rlRun "vagrant service-manager box version > stdout 2> stderr"
        echo -e "stdout:\n========"
        cat stdout
        echo -e "stderr:\n========"
        cat stderr
        echo "========"
        rlAssertNotGrep "." stderr
        rlLogInfo "`cat stdout`"
        rlAssertGrep "." stdout

        rlLogInfo "Testing box version --scritp-readable"
        rlRun "vagrant service-manager box version --script-readable> stdout 2> stderr"
        echo -e "stdout:\n========"
        cat stdout
        echo -e "stderr:\n========"
        cat stderr
        echo "========"
        rlAssertNotGrep "." stderr
        rlAssertGrep "VARIANT=\".\+\"" stdout
        rlAssertGrep "VARIANT_ID=\".\+\"" stdout
        rlAssertGrep "VARIANT_VERSION=\".\+\"" stdout

        rlRun "vagrant destroy -f"
        rlRun "popd"
    rlPhaseEnd
done

    rlPhaseStartCleanup
        #vagrantBoxRemove # can be shared, so skipping
        rlRun "rm -f ~/.vagrant.d/Vagrantfile"
    rlPhaseEnd
rlJournalPrintText
rlJournalEnd
