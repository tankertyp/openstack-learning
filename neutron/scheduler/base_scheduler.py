# Copyright (c) 2015 OpenStack Foundation.
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

import abc
from operator import attrgetter
import random

from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class BaseScheduler(object, metaclass=abc.ABCMeta):
    """The base scheduler (agnostic to resource type).
       Child classes of BaseScheduler must define the
       self.resource_filter to filter agents of
       particular type.
    """
    resource_filter = None

    @abc.abstractmethod
    def select(self, plugin, context, resource_hostable_agents,
               resource_hosted_agents, num_agents_needed):
        """Return a subset of agents based on the specific scheduling logic."""

    def schedule(self, plugin, context, resource):
        """Select and bind agents to a given resource."""
        if not self.resource_filter:
            return
        # filter the agents that can host the resource
        filtered_agents_dict = self.resource_filter.filter_agents(
            plugin, context, resource)
        num_agents = filtered_agents_dict['n_agents']
        hostable_agents = filtered_agents_dict['hostable_agents']
        hosted_agents = filtered_agents_dict['hosted_agents']
        chosen_agents = self.select(plugin, context, hostable_agents,
                                    hosted_agents, num_agents)
        # bind the resource to the agents
        force_scheduling = bool(resource.get('candidate_hosts'))
        self.resource_filter.bind(
            context, chosen_agents, resource['id'], force_scheduling)
        debug_data = ['(%s, %s, %s)' %
                      (agent['agent_type'], agent['host'], resource['id'])
                      for agent in chosen_agents]
        LOG.debug('Resources bound (agent type, host, resource id): %s',
                  ', '.join(debug_data))
        return chosen_agents


class BaseChanceScheduler(BaseScheduler):
    """Choose agents randomly."""

    def __init__(self, resource_filter):
        self.resource_filter = resource_filter

    def select(self, plugin, context, resource_hostable_agents,
               resource_hosted_agents, num_agents_needed):
        chosen_agents = random.sample(resource_hostable_agents,
                                      num_agents_needed)
        return chosen_agents


class BaseWeightScheduler(BaseScheduler):
    """Choose agents based on load."""

    def __init__(self, resource_filter):
        self.resource_filter = resource_filter

    def select(self, plugin, context, resource_hostable_agents,
               resource_hosted_agents, num_agents_needed):
        chosen_agents = sorted(resource_hostable_agents,
                               key=attrgetter('load'))[0:num_agents_needed]
        return chosen_agents


def get_vacant_binding_index(num_agents, bindings, lowest_binding_index,
                             force_scheduling=False):
    """Return a vacant binding_index to use and whether or not it exists.

    This method can be used with DHCP and L3 agent schedulers. It will return
    the lowest vacant index for one of those agents.
    :param num_agents: (int) number of agents (DHCP, L3) already scheduled
    :param bindings: (NetworkDhcpAgentBinding, RouterL3AgentBinding) agent
                     binding object, must have "binding_index" field.
    :param lowest_binding_index: (int) lowest index number to be scheduled.
    :param force_scheduling: (optional)(boolean) if enabled, the method will
                             always return an index, even if this number
                             exceeds the maximum configured number of agents.
    """
    binding_indices = [b.binding_index for b in bindings]
    all_indices = set(range(lowest_binding_index, num_agents + 1))
    open_slots = sorted(list(all_indices - set(binding_indices)))

    if open_slots:
        return open_slots[0]

    if not force_scheduling:
        return -1

    # Last chance: if this is a manual scheduling, we're gonna allow
    # creation of a binding_index even if it will exceed
    # dhcp_agents_per_network.
    if max(binding_indices) == len(binding_indices):
        return max(binding_indices) + 1
    else:
        # Find binding index set gaps and return first free one.
        all_indices = set(range(lowest_binding_index,
                                max(binding_indices) + 1))
        open_slots = sorted(list(all_indices - set(binding_indices)))
        return open_slots[0]
