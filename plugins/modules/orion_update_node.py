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

- name: Update node to SNMPv3 polling
  solarwinds.orion.orion_update_node:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_password }}"
    name: "{{ inventory_hostname }}"
    polling_method: SNMP
    snmp_version: "3"
    snmpv3_username: "{{ snmpv3_user }}"
    snmpv3_auth_method: "{{ snmpv3_auth }}{{ snmpv3_auth_level }}"
    snmpv3_auth_key: "{{ snmpv3_auth_pass }}"
    snmpv3_priv_method: "{{ snmpv3_priv }}{{ snmpv3_priv_level }}"
    snmpv3_priv_key: "{{ snmpv3_priv_pass }}"
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.solarwinds.orion.plugins.module_utils.orion import OrionModule, orion_argument_spec

try:
    import orionsdk
    from orionsdk import SwisClient
    HAS_ORION = True
except ImportError:
    HAS_ORION = False

def properties_need_update(current_node, desired_properties):
    for key, value in desired_properties.items():
        if key not in current_node or current_node[key] != value:
            return True
    return False

def main():
    argument_spec = orion_argument_spec
    argument_spec.update(
        polling_method=dict(required=False, choices=['External', 'ICMP', 'SNMP', 'WMI', 'Agent']),
        snmp_version=dict(required=False, choices=['2', '3']),
        snmpv3_username=dict(required=False, type='str'),
        snmpv3_auth_method=dict(required=False, choices=['SHA1', 'MD5']),
        snmpv3_auth_key=dict(required=False, type='str', no_log=True),
        snmpv3_priv_method=dict(required=False, choices=['DES56', 'AES128', 'AES192', 'AES256']),
        snmpv3_priv_key=dict(required=False, type='str', no_log=True),
        snmpv3_auth_key_is_pwd=dict(required=False, type='bool', default=True),
        snmpv3_priv_key_is_pwd=dict(required=False, type='bool', default=True),
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

    update_properties = {}
    
    if module.params['polling_method']:
        update_properties['ObjectSubType'] = module.params['polling_method'].upper()
    
    if module.params['snmp_version']:
        update_properties['SNMPVersion'] = module.params['snmp_version']
    
    if module.params['snmpv3_username']:
        update_properties['SNMPV3Username'] = module.params['snmpv3_username']
    
    if module.params['snmpv3_auth_method']:
        update_properties['SNMPV3AuthMethod'] = module.params['snmpv3_auth_method']
    
    if module.params['snmpv3_auth_key']:
        update_properties['SNMPV3AuthKey'] = module.params['snmpv3_auth_key']
        update_properties['SNMPV3AuthKeyIsPwd'] = module.params['snmpv3_auth_key_is_pwd']
    
    if module.params['snmpv3_priv_method']:
        update_properties['SNMPV3PrivMethod'] = module.params['snmpv3_priv_method']
    
    if module.params['snmpv3_priv_key']:
        update_properties['SNMPV3PrivKey'] = module.params['snmpv3_priv_key']
        update_properties['SNMPV3PrivKeyIsPwd'] = module.params['snmpv3_priv_key_is_pwd']

    try:
        if module.check_mode:
            module.exit_json(changed=properties_need_update(node, update_properties), orion_node=node)
        else:
            if properties_need_update(node, update_properties):
                orion.swis.update(node['uri'], **update_properties)
                updated_node = orion.get_node()
                module.exit_json(changed=True, orion_node=updated_node)
            else:
                module.exit_json(changed=False, orion_node=node)
    except Exception as OrionException:
        module.fail_json(msg='Failed to update node: {0}'.format(str(OrionException)))
        
if __name__ == "__main__":
    main()