# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2013 Canonical Corp.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from nova.network import model as network_model
from nova import test
from nova.virt.vmwareapi import network_util
from nova.virt.vmwareapi import vif


class VMwareVifTestCase(test.TestCase):
    def setUp(self):
        super(VMwareVifTestCase, self).setUp()
        self.flags(vmwareapi_vlan_interface='vmnet0')
        network = network_model.Network(id=0,
                                        bridge='fa0',
                                        label='fake',
                                        vlan=3,
                                        bridge_interface='eth0',
                                        injected=True)

        self.vif = network_model.NetworkInfo([
                network_model.VIF(id=None,
                                  address='DE:AD:BE:EF:00:00',
                                  network=network,
                                  type=None,
                                  devname=None,
                                  ovs_interfaceid=None,
                                  rxtx_cap=3)
        ])[0]
        self.session = "fake"
        self.cluster = None

    def tearDown(self):
        super(VMwareVifTestCase, self).tearDown()

    def test_ensure_vlan_bridge(self):
        self.mox.StubOutWithMock(network_util, 'get_network_with_the_name')
        self.mox.StubOutWithMock(network_util,
            'get_vswitch_for_vlan_interface')
        self.mox.StubOutWithMock(network_util,
            'check_if_vlan_interface_exists')
        self.mox.StubOutWithMock(network_util, 'create_port_group')
        network_util.get_network_with_the_name(self.session, 'fa0',
            self.cluster).AndReturn(None)
        network_util.get_vswitch_for_vlan_interface(self.session, 'vmnet0',
            self.cluster).AndReturn('vmnet0')
        network_util.check_if_vlan_interface_exists(self.session, 'vmnet0',
            self.cluster).AndReturn(True)
        network_util.create_port_group(self.session, 'fa0', 'vmnet0', 3,
            self.cluster)

        self.mox.ReplayAll()
        vif.ensure_vlan_bridge(self.session, self.vif, create_vlan=True)

    # FlatDHCP network mode without vlan
    def test_ensure_vlan_bridge_without_vlan(self):
        self.mox.StubOutWithMock(network_util, 'get_network_with_the_name')
        self.mox.StubOutWithMock(network_util,
            'get_vswitch_for_vlan_interface')
        self.mox.StubOutWithMock(network_util,
            'check_if_vlan_interface_exists')
        self.mox.StubOutWithMock(network_util, 'create_port_group')

        network_util.get_network_with_the_name(self.session, 'fa0',
            self.cluster).AndReturn(None)
        network_util.get_vswitch_for_vlan_interface(self.session, 'vmnet0',
            self.cluster).AndReturn('vmnet0')
        network_util.check_if_vlan_interface_exists(self.session, 'vmnet0',
        self.cluster).AndReturn(True)
        network_util.create_port_group(self.session, 'fa0', 'vmnet0', 0,
            self.cluster)
        self.mox.ReplayAll()
        vif.ensure_vlan_bridge(self.session, self.vif, create_vlan=False)

    def test_get_network_ref_quantum(self):
        self.mox.StubOutWithMock(vif, 'get_quantum_network')
        vif.get_quantum_network(self.session, 'fa0', self.cluster, self.vif)
        self.mox.ReplayAll()
        vif.get_network_ref(self.session, self.cluster, self.vif, True)

    def test_get_network_ref_flat_dhcp(self):
        self.mox.StubOutWithMock(vif, 'ensure_vlan_bridge')
        vif.ensure_vlan_bridge(self.session, self.vif, cluster=self.cluster,
                               create_vlan=False)
        self.mox.ReplayAll()
        vif.get_network_ref(self.session, self.cluster, self.vif, False)

    def test_get_network_ref_bridge(self):
        self.mox.StubOutWithMock(vif, 'ensure_vlan_bridge')
        vif.ensure_vlan_bridge(self.session, self.vif, cluster=self.cluster,
                               create_vlan=True)
        self.mox.ReplayAll()
        network = network_model.Network(id=0,
                                        bridge='fa0',
                                        label='fake',
                                        vlan=3,
                                        bridge_interface='eth0',
                                        injected=True,
                                        should_create_vlan=True)
        self.vif = network_model.NetworkInfo([
                network_model.VIF(id=None,
                                  address='DE:AD:BE:EF:00:00',
                                  network=network,
                                  type=None,
                                  devname=None,
                                  ovs_interfaceid=None,
                                 rxtx_cap=3)
        ])[0]
        vif.get_network_ref(self.session, self.cluster, self.vif, False)