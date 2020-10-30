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


from neutron_lib.api.definitions import agent as agent_def
from neutron_lib.api.definitions import availability_zone as az_def
from neutron_lib.api.definitions import expose_port_forwarding_in_fip
from neutron_lib.api.definitions import fip_pf_description
from neutron_lib.api.definitions import floating_ip_port_forwarding
from neutron_lib.api.definitions import port_resource_request
from neutron_lib.api.definitions import qos
from neutron_lib.api.definitions import qos_bw_limit_direction
from neutron_lib.api.definitions import qos_default
from neutron_lib.api.definitions import qos_rule_type_details
from neutron_lib.api.definitions import qos_rules_alias
from neutron_lib.api.definitions import router_availability_zone as raz_def
from neutron_lib.api.definitions import segment as seg_def

# NOTE(russellb) This remains in its own file (vs constants.py) because we want
# to be able to easily import it and export the info without any dependencies
# on external imports.

# NOTE(russellb) If you update these lists, please also update
# doc/source/features.rst and the current release note.
ML2_SUPPORTED_API_EXTENSIONS_OVN_L3 = [
    'router',
    'extraroute',
    'ext-gw-mode',
    'fip-port-details',
    'pagination',
    'qos-fip',
    'sorting',
    'project-id',
    'dns-integration',
    agent_def.ALIAS,
    az_def.ALIAS,
    raz_def.ALIAS,
]
ML2_SUPPORTED_API_EXTENSIONS = [
    'address-scope',
    'agent',
    'allowed-address-pairs',
    'auto-allocated-topology',
    'binding',
    'default-subnetpools',
    'external-net',
    'extra_dhcp_opt',
    'multi-provider',
    'net-mtu',
    'network_availability_zone',
    'network-ip-availability',
    'port-security',
    'provider',
    port_resource_request.ALIAS,
    qos.ALIAS,
    qos_bw_limit_direction.ALIAS,
    qos_default.ALIAS,
    qos_rule_type_details.ALIAS,
    qos_rules_alias.ALIAS,
    'quotas',
    'rbac-address-scope',
    'rbac-policies',
    'standard-attr-revisions',
    'security-group',
    'standard-attr-description',
    'subnet_allocation',
    'standard-attr-tag',
    'standard-attr-timestamp',
    'trunk',
    'quota_details',
    seg_def.ALIAS,
    expose_port_forwarding_in_fip.ALIAS,
    fip_pf_description.ALIAS,
    floating_ip_port_forwarding.ALIAS,
]
