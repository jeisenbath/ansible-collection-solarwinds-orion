#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Josh M. Eisenbath <j.m.eisenbath@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: orion_update_node
short_description: Updates Node in Solarwinds Orion NPM
description:
    - Updates properties of a node, such as caption or IP Address.
    - Updating a node's caption, or polling method, can be used to retain historical data about the node.
    - For cases where that data isn't needed, it is recommended to use M(solarwinds.orion.orion_node) to re-add it.
    - Never use this to update a node_id.
version_added: "1.0.0"
author: "Josh M. Eisenbath (@jeisenbath)"
options:
    properties:
        description:
            - Properties of the node that will be updated.
        required: False
        default: {}
        type: dict
extends_documentation_fragment:
    - solarwinds.orion.orion_auth_options
    - solarwinds.orion.orion_node_options
requirements:
    - orionsdk
    - requests
'''

EXAMPLES = r'''
---

- name: Update node caption
  solarwinds.orion.orion_update_node:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    ip_address: "{{ node_ip_address }}"
    properties:
      Caption: "{{ new_node_caption }}"
  delegate_to: localhost

- name: Update node to SNMPv2 polling
  solarwinds.orion.orion_update_node:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    name: "{{ node_name }}"
    properties:
      ObjectSubType: SNMP
      SNMPVersion: 2
      Community: "{{ ro_community_string }}"
  delegate_to: localhost

- name: Update node to SNMPv3 polling
  solarwinds.orion.orion_update_node:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    name: "{{ node_name }}"
    properties:
      ObjectSubType: SNMP
      SNMPVersion: 3
      SNMPV3Username: "{{ snmpv3_user }}"
      SNMPV3AuthMethod: "{{ snmpv3_auth }}{{ snmpv3_auth_level }}"
      SNMPV3AuthKey: "{{ snmpv3_auth_pass }}"
      SNMPV3PrivMethod: "{{ snmpv3_priv }}{{ snmpv3_priv_level }}"
      SNMPV3PrivKey: "{{ snmpv3_priv_pass }}"
  delegate_to: localhost

'''

RETURN = r'''
orion_node:
    description: Info about an orion node.
    returned: always
    type: dict
    sample: {
        "caption": "localhost",
        "ipaddress": "127.0.0.1",
        "netobjectid": "N:12345",
        "nodeid": "12345",
        "objectsubtype": "SNMP",
        "status": 1,
        "statusdescription": "Node status is Up.",
        "unmanaged": false,
        "unmanagefrom": "1899-12-30T00:00:00+00:00",
        "unmanageuntil": "1899-12-30T00:00:00+00:00",
        "uri": "swis://host.domain.com/Orion/Orion.Nodes/NodeID=12345"
    }
'''

import requests
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.solarwinds.orion.plugins.module_utils.orion import OrionModule, orion_argument_spec
try:
    import orionsdk
    from orionsdk import SwisClient
    HAS_ORION = True
except ImportError:
    HAS_ORION = False
except Exception:
    raise Exception

requests.packages.urllib3.disable_warnings()

def properties_need_update(current_node, desired_properties):
    for key, value in desired_properties.items():
        if key not in current_node or current_node[key] != value:
            return True
    return False

def main():
    argument_spec = orion_argument_spec
    argument_spec.update(
        properties=dict(required=False, default={}, type='dict')
    )
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        required_one_of=[('name', 'node_id', 'ip_address')],
    )

    if not HAS_ORION:
        module.fail_json(msg='orionsdk required for this module')

    orion = OrionModule(module)
    
    node = orion.get_node()
    if not node:
        module.fail_json(skipped=True, msg='Node not found')

    changed = False
    
    # fields to be updated might not necessarily be in the limited scope of orion.get_node(), so we specifically get them here
    fields = "NodeID, "
    for key in module.params['properties']:
        fields += "{0}, ".format(key)
    query = "SELECT {0} FROM Orion.Nodes WHERE NodeID = '{1}'".format(fields, node['node_id'])
    current_node_properties = orion.swis_query(query)

    try:
        if module.check_mode:
            changed = True
        else:
            if properties_need_update(current_node_properties, module.params['properties']):
                orion.swis.update(node['uri'], **module.params['properties'])
                changed = True
    except Exception as OrionException:
        module.fail_json(msg='Failed to update {0}'.format(str(OrionException)))

    module.exit_json(changed=changed, orion_node=node)


if __name__ == "__main__":
    main()
