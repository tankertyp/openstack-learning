# Copyright (c) 2016 Red Hat Inc.
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

from neutron_lib.api.definitions import portbindings
from neutron_lib import constants
from neutron_lib.db import constants as db_consts
from neutron_lib.services.qos import base
from neutron_lib.services.qos import constants as qos_consts
from oslo_log import log as logging

from neutron.objects import network as network_object


LOG = logging.getLogger(__name__)

DRIVER = None

SUPPORTED_RULES = {
    qos_consts.RULE_TYPE_BANDWIDTH_LIMIT: {
        qos_consts.MAX_KBPS: {
            'type:range': [0, db_consts.DB_INTEGER_MAX_VALUE]},
        qos_consts.MAX_BURST: {
            'type:range': [0, db_consts.DB_INTEGER_MAX_VALUE]},
        qos_consts.DIRECTION: {
            'type:values': constants.VALID_DIRECTIONS}
    },
    qos_consts.RULE_TYPE_DSCP_MARKING: {
        qos_consts.DSCP_MARK: {'type:values': constants.VALID_DSCP_MARKS}
    },
    qos_consts.RULE_TYPE_MINIMUM_BANDWIDTH: {
        qos_consts.MIN_KBPS: {
            'type:range': [0, db_consts.DB_INTEGER_MAX_VALUE]},
        qos_consts.DIRECTION: {'type:values': constants.VALID_DIRECTIONS}
    }
}


class OVSDriver(base.DriverBase):

    @staticmethod
    def create():
        return OVSDriver(
            name='openvswitch',
            vif_types=[portbindings.VIF_TYPE_OVS,
                       portbindings.VIF_TYPE_VHOST_USER],
            vnic_types=[portbindings.VNIC_NORMAL, portbindings.VNIC_DIRECT],
            supported_rules=SUPPORTED_RULES,
            requires_rpc_notifications=True)

    def validate_rule_for_port(self, context, rule, port):
        # Minimum-bandwidth rule is only supported on networks whose
        # first segment is backed by a physnet.
        if rule.rule_type == qos_consts.RULE_TYPE_MINIMUM_BANDWIDTH:
            net = network_object.Network.get_object(
                context, id=port.network_id)
            physnet = net.segments[0].physical_network
            if physnet is None:
                return False
        return True


def register():
    """Register the driver."""
    global DRIVER
    if not DRIVER:
        DRIVER = OVSDriver.create()
    LOG.debug('Open vSwitch QoS driver registered')
