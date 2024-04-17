# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Josh Eisenbath <j.m.eisenbath@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
    name: orion_nodes_inventory
    short_description: Solarwinds Orion nodes inventory source
    author:
      - Josh Eisenbath (@jeisenbath)
    description:
      - A dynamic inventory plugin that will query nodes from the Solarwinds Orion database.
    extends_documentation_fragment:
      - inventory_cache
      - constructed
    requirements:
      - "requests"
      - "orionsdk"
    options:
      orion_hostname:
        description: Hostname of the Solarwinds Orion server.
        required: true
        type: string
      orion_username: 
        description: Username to Authenticate with Orion Server.
        required: true
        type: string
      orion_password:
        description: Password to Authenticate with Orion Server. Accepts ansible-vault encrypted string.
        required: true
        type: string
      filter:
        description: Optional WHERE filter used when querying the Orion.Nodes table to filter out hosts.
        required: false
        type: string
      hostname_field:
        description: Choice of using IP_Address, DNS or Caption as the inventory hostname
        required: true
        choices:
          - IP_Address
          - DNS
          - Caption
        type: string
      hostvar_prefix:
        description:
          - String to prepend to the Orion.Nodes field name when converting to a host variable.
          - E.g. 'hostvar_prefix: orion_' generates variables like 'orion_dns', 'orion_ip_address', 'orion_caption'
        required: false
        type: string
        default: orion_
      hostvar_fields:
        description: List of fields to select from Orion.Nodes from which to generate host variables.
        required: false
        type: list
        elements: string
      hostvar_custom_properties:
        description: List of custom properties from which to generate host variables.
        required: false
        type: list
        elements: string
'''

EXAMPLES = r'''
# This example will pull in all SNMP polled devices that have a DNS field in Orion.Nodes
# It will use that DNS field as the host name
# It will also pull in IP_Address and Caption to create host variables from
# In this environment, the nodes have a custom property 'Server_Environment'
# So we will pull that value and create a host variable, 
# then use the keyed_groups function to turn that value into a group.
---
plugin: solarwinds.orion.orion_nodes_inventory
cache: true
strict: false
orion_hostname: orion.hostname.com
orion_username: Ansible
orion_password: changeme
filter: "WHERE ObjectSubType = 'SNMP' AND DNS != ''"
hostname_field: DNS
hostvar_fields:
  - IP_Address
  - Caption
hostvar_custom_properties:
  - Server_Environment
keyed_groups:
  - key: orion_Server_Environment
    prefix: env

'''

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.module_utils._text import to_text, to_native
from ansible.utils.display import Display
from ansible.parsing.yaml.objects import AnsibleVaultEncryptedUnicode

display = Display()

# 3rd party imports
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from orionsdk import SwisClient
    HAS_ORION = True
except ImportError:
    HAS_ORION = False

from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable, Constructable

requests.packages.urllib3.disable_warnings()


class InventoryModule(BaseInventoryPlugin, Cacheable, Constructable):
    NAME = 'solarwinds.orion.orion_nodes_inventory'

    def __init__(self):
        super(InventoryModule, self).__init__()
        if not HAS_ORION:
            raise AnsibleError('Missing python module: orionsdk')
        if not HAS_REQUESTS:
            raise AnsibleError('Missing python module: requests')

    def verify_file(self, path):
        """ return true/false if this is possibly a valid file for this plugin to consume """
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('orion.yaml', 'orion.yml', 'solarwinds.yaml', 'solarwinds.yml')):
                valid = True
            else:
                self.display.vvv("Inventory source doesn't match 'solarwinds' or 'orion', skipping...")
        return valid

    def parse(self, inventory, loader, path, cache=True):
        try:
            super(InventoryModule, self).parse(inventory, loader, path)

            config = self._read_config_data(path)

            self._consume_options(config)
        except Exception as e:
            raise AnsibleParserError('Failed to consume options:    {}'.format(to_native(e)))

        cache_key = self.get_cache_key(path)
        update_cache = False

        if cache:
            try:
                self.display.vvv("Getting cached data...")
                cacheable_results = self._cache[cache_key]
                self.display.vvv("Got cached data...")
            except KeyError:
                self.display.vvv("Cache needs updating...")
                update_cache = True

        if cache and not update_cache:
            self.display.vvv("Populating from cache...")
            self._populate_from_cache(cacheable_results)
        else:
            self.display.vvv("Populating from source...")
            cacheable_results = self._populate_from_source()

        if update_cache or (not cache and self.get_option('cache')):
            self.display.vvv("Updating cache data...")
            self._cache[cache_key] = cacheable_results

    def _populate_from_cache(self, cache_data):
        """
        Populate cache using source data

        """
        for host, host_properties in cache_data.items():
            self.add_host(host, host_properties)

    def _populate_from_source(self):
        inv_hostvars = {}

        data = self.get_orion_nodes()

        if data:
            self.display.vvv("Building inventory from query data...")
            for node in data:
                try:
                    node_hostvars = {}
                    node_hostname = node[self.get_option('hostname_field')]

                    for hostvar in self.get_option('hostvar_fields'):
                        node_hostvars[hostvar] = node[hostvar]

                    if self.get_option('hostvar_custom_properties'):
                        for custom_property in self.get_option('hostvar_custom_properties'):
                            node_hostvars[custom_property] = node[custom_property]

                    inv_hostvars[node_hostname] = node_hostvars
                    self.add_host(node_hostname, node_hostvars)
                except Exception as e:
                    raise AnsibleParserError('Error iterating over query results: {}'.format(to_native(e)))

        return inv_hostvars

    def get_orion_nodes(self):
        orion_password = self.get_option('orion_password')
        if isinstance(orion_password, AnsibleVaultEncryptedUnicode):
            orion_password = orion_password.data
        try:
            swis_options = {
                'hostname': self.get_option('orion_hostname'),
                'username': self.get_option('orion_username'),
                'password': orion_password,
            }
            __SWIS__ = SwisClient(**swis_options)
            __SWIS__.query('SELECT uri FROM Orion.Environment')
        except Exception as e:
            raise AnsibleError('Failed to connect to Orion database:   {}'.format(to_native(e)))

        hostname_field = self.get_option('hostname_field')
        select_string = "SELECT NodeID, node.{}".format(hostname_field)
        for hostvar_field in self.get_option('hostvar_fields'):
            select_string = select_string + ", node.{}".format(hostvar_field)
        if self.get_option('hostvar_custom_properties'):
            for custom_property in self.get_option('hostvar_custom_properties'):
                select_string = select_string + ", custom.{0} as {1}".format(custom_property, custom_property)

        query = "{0} FROM Orion.Nodes as node ".format(select_string)

        if self.get_option('hostvar_custom_properties'):
            query = query + "LEFT JOIN Orion.NodesCustomProperties as custom on node.NodeID = custom.NodeID "

        if self.get_option('filter'):
            query = query + self.get_option('filter')

        self.display.vvv('Using query "{}"'.format(to_text(query)))

        results = __SWIS__.query(query)

        return results['results']

    def add_host(self, hostname, hostvars):
        self.inventory.add_host(hostname, group='all')

        for var_name, var_value in hostvars.items():
            var_name = "{0}{1}".format(self.get_option('hostvar_prefix'), var_name)
            try:
                self.inventory.set_variable(hostname, var_name, var_value)
            except ValueError as e:
                self.display.warning("Could not set hostvar {0} to {1} for the {2} host, skipping:  {3}".format(
                    var_name, to_native(var_value), hostname, to_native(e)
                ))

        strict = self.get_option('strict')

        # Add variables created by the user's Jinja2 expressions to the host
        self._set_composite_vars(self.get_option('compose'), hostvars, hostname, strict=True)

        # Create user-defined groups using variables and Jinja2 conditionals
        self._add_host_to_composed_groups(self.get_option('groups'), hostvars, hostname, strict=strict)
        # need to format group name, remove or replace spaces and make lowercase
        self._add_host_to_keyed_groups(self.get_option('keyed_groups'), hostvars, hostname, strict=strict)
