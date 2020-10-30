# Copyright 2017 DT Dream Technology Co.,Ltd.
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

import contextlib

from neutron.services.trunk import plugin as trunk_plugin
from neutron.tests.functional import base
from neutron_lib import constants as n_consts
from neutron_lib.objects import registry as obj_reg
from neutron_lib.plugins import utils
from neutron_lib.services.trunk import constants as trunk_consts
from oslo_utils import uuidutils


class TestOVNTrunkDriver(base.TestOVNFunctionalBase):

    def setUp(self):
        super(TestOVNTrunkDriver, self).setUp()
        self.trunk_plugin = trunk_plugin.TrunkPlugin()
        self.trunk_plugin.add_segmentation_type(
            trunk_consts.SEGMENTATION_TYPE_VLAN,
            utils.is_valid_vlan_tag)

    @contextlib.contextmanager
    def trunk(self, sub_ports=None):
        sub_ports = sub_ports or []
        with self.network() as network:
            with self.subnet(network=network) as subnet:
                with self.port(subnet=subnet) as parent_port:
                    tenant_id = uuidutils.generate_uuid()
                    trunk = {'trunk': {
                        'port_id': parent_port['port']['id'],
                        'tenant_id': tenant_id, 'project_id': tenant_id,
                        'admin_state_up': True,
                        'name': 'trunk', 'sub_ports': sub_ports}}
                    trunk = self.trunk_plugin.create_trunk(self.context, trunk)
                    yield trunk

    @contextlib.contextmanager
    def subport(self):
        with self.port() as port:
            sub_port = {'segmentation_type': 'vlan',
                        'segmentation_id': 1000,
                        'port_id': port['port']['id']}
            yield sub_port

    def _get_ovn_trunk_info(self):
        ovn_trunk_info = []
        for row in self.nb_api.tables[
                'Logical_Switch_Port'].rows.values():
            if row.parent_name and row.tag:
                ovn_trunk_info.append({'port_id': row.name,
                                       'parent_port_id': row.parent_name,
                                       'tag': row.tag})
        return ovn_trunk_info

    def _verify_trunk_info(self, trunk, has_items):
        ovn_subports_info = self._get_ovn_trunk_info()
        neutron_subports_info = []
        for subport in trunk.get('sub_ports', []):
            neutron_subports_info.append({'port_id': subport['port_id'],
                                          'parent_port_id': [trunk['port_id']],
                                          'tag': [subport['segmentation_id']]})
            # Check that the subport has the binding is active.
            binding = obj_reg.load_class('PortBinding').get_object(
                self.context, port_id=subport['port_id'], host='')
            self.assertEqual(n_consts.PORT_STATUS_ACTIVE, binding['status'])

        self.assertItemsEqual(ovn_subports_info, neutron_subports_info)
        self.assertEqual(has_items, len(neutron_subports_info) != 0)

        if trunk.get('status'):
            self.assertEqual(trunk_consts.TRUNK_ACTIVE_STATUS, trunk['status'])

    def test_trunk_create(self):
        with self.trunk() as trunk:
            self._verify_trunk_info(trunk, has_items=False)

    def test_trunk_create_with_subports(self):
        with self.subport() as subport:
            with self.trunk([subport]) as trunk:
                self._verify_trunk_info(trunk, has_items=True)

    def test_subport_add(self):
        with self.subport() as subport:
            with self.trunk() as trunk:
                self.trunk_plugin.add_subports(self.context, trunk['id'],
                                               {'sub_ports': [subport]})
                new_trunk = self.trunk_plugin.get_trunk(self.context,
                                                        trunk['id'])
                self._verify_trunk_info(new_trunk, has_items=True)

    def test_subport_delete(self):
        with self.subport() as subport:
            with self.trunk([subport]) as trunk:
                self.trunk_plugin.remove_subports(self.context, trunk['id'],
                                                  {'sub_ports': [subport]})
                new_trunk = self.trunk_plugin.get_trunk(self.context,
                                                        trunk['id'])
                self._verify_trunk_info(new_trunk, has_items=False)

    def test_trunk_delete(self):
        with self.trunk() as trunk:
            self.trunk_plugin.delete_trunk(self.context, trunk['id'])
            self._verify_trunk_info({}, has_items=False)
