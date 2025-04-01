#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Josh M. Eisenbath <j.m.eisenbath@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: orion_custom_property
short_description: Manage custom properties on Node in Solarwinds Orion NPM
description:
    - Adds or removes a custom property on Node in Solarwinds Orion NPM.
    - This module requires the custom property to already exist in Solarwinds settings.
version_added: "1.0.0"
author: "Josh M. Eisenbath (@jeisenbath)"
options:
    state:
        description:
            - Desired state of the custom property on the node.
            - When I(state=absent), sets value of property for the node to None.
        required: True
        type: str
        choices:
            - present
            - absent
    property_name:
        description:
            - Name of the custom property for the node.
        required: True
        type: str
    property_value:
        description:
            - Value to set for the custom property on the node.
            - Required if I(state=present).
        required: False
        type: str
extends_documentation_fragment:
    - jeisenbath.solarwinds.orion_auth_options
    - jeisenbath.solarwinds.orion_node_options
requirements:
    - orionsdk
    - requests
'''

EXAMPLES = r'''
---

- name: Set the custom property Timezone to EST for node
  jeisenbath.solarwinds.orion_custom_property:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    name: "{{ node_name }}"
    state: present
    property_name: Timezone
    property_value: EST
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
        "lastsystemuptimepollutc": "2024-09-25T18:34:20.7630000Z",
        "netobjectid": "N:12345",
        "nodeid": "12345",
        "objectsubtype": "SNMP",
        "status": 1,
        "statusdescription": "Node status is Up.",
        "unmanaged": false,
        "unmanagefrom": "1899-12-30TO00:00:00+00:00",
        "unmanageuntil": "1899-12-30TO00:00:00+00:00",
        "uri": "swis://host.domain.com/Orion/Orion.Nodes/NodeID=12345"
    }
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.jeisenbath.solarwinds.plugins.module_utils.orion import OrionModule, orion_argument_spec
try:
    import requests
    HAS_REQUESTS = True
    requests.packages.urllib3.disable_warnings()
except ImportError:
    HAS_REQUESTS = False
except Exception:
    raise Exception


def main():
    argument_spec = orion_argument_spec()
    argument_spec.update(
        state=dict(required=True, choices=['present', 'absent']),
        property_name=dict(required=True, type='str'),
        property_value=dict(required=False, type='str')
    )
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        required_one_of=[('name', 'node_id', 'ip_address')],
        required_if=[
            ('state', 'present', ['property_value'])
        ]
    )

    orion = OrionModule(module)

    node = orion.get_node()
    if not node:
        module.fail_json(skipped=True, msg='Node not found')

    changed = False
    if module.params['state'] == 'present':
        try:
            prop_name, prop_value = orion.get_node_custom_property_value(node, module.params['property_name'])
            if prop_value != module.params['property_value']:
                if not module.check_mode:
                    orion.add_custom_property(node, module.params['property_name'], module.params['property_value'])
                changed = True
        except Exception as OrionException:
            module.fail_json(msg='Failed to add custom properties: {0}'.format(OrionException))
    elif module.params['state'] == 'absent':
        try:
            prop_name, prop_value = orion.get_node_custom_property_value(node, module.params['property_name'])
            if prop_value:
                if not module.check_mode:
                    orion.add_custom_property(node, module.params['property_name'], None)
                changed = True
        except Exception as OrionException:
            module.fail_json(msg='Failed to remove custom property from node: {0}'.format(OrionException))

    module.exit_json(changed=changed, orion_node=node)


if __name__ == "__main__":
    main()
