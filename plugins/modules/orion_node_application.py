#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Josh M. Eisenbath <j.m.eisenbath@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: orion_node_application
short_description: Manages APM application templates assigned to nodes.
description:
    - Adds or removes an APM Appliction Template to Node in Solarwinds Orion NPM.
    - This module requires the Application Template to already exist in Solarwinds APM.
    - If the Application Template required credentials, they also need to already exist.
version_added: "1.0.0"
author: "Josh M. Eisenbath (@jeisenbath)"
options:
    state:
        description:
            - Desired state of the application on the node.
        required: True
        type: str
        choices:
            - present
            - absent
    application_template_name:
        description:
            - Name of the application template.
        required: True
        type: str
    credential_name:
        description:
            - Name of the credentials to use for the application template.
            - If not passed, will Inherit credentials from template.
        required: False
        type: str
    skip_duplicates:
        description:
            - Option to allow duplicate APM Application Template assigned to node.
        required: False
        default: True
        type: bool
extends_documentation_fragment:
    - jeisenbath.solarwinds.orion_auth_options
    - jeisenbath.solarwinds.orion_node_options
requirements:
    - orionsdk
    - requests
'''

EXAMPLES = r'''
---

- name: Add APM Application Template to Node
  jeisenbath.solarwinds.orion_node_application:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    name: "{{ node_name }}"
    state: present
    application_template_name: "{{ APM_application_name }}"
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
        application_template_name=dict(required=True, type='str'),
        credential_name=dict(required=False, type='str'),
        skip_duplicates=dict(required=False, default=True, type='bool')
    )
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        required_one_of=[('name', 'node_id', 'ip_address')],
    )

    orion = OrionModule(module)

    node = orion.get_node()
    if not node:
        module.fail_json(skipped=True, msg='Node not found')

    changed = False
    if module.params['state'] == 'present':
        try:
            application_template_id = orion.get_application_template_id(module.params['application_template_name'])

            credential_id = "-4"
            if module.params['credential_name']:
                try:
                    credential_id = orion.get_apm_credential_id(module.params['credential_name'])
                except Exception as OrionException:
                    module.fail_json(msg='Failed to query credential name: {0}'.format(OrionException))

            application_id = orion.get_application_id(node, module.params['application_template_name'])
            if not application_id:
                if not module.check_mode:
                    orion.add_application_template_to_node(node, application_template_id, credential_id, module.params['skip_duplicates'])
                changed = True
        except Exception as OrionException:
            module.fail_json(msg='Failed to add application to node: {0}'.format(OrionException))

    elif module.params['state'] == 'absent':
        try:
            application_id = orion.get_application_id(node, module.params['application_template_name'])

            if application_id:
                if not module.check_mode:
                    orion.remove_application_template_from_node(application_id)
                changed = True
        except Exception as OrionException:
            module.fail_json(msg='Failed to remove application from node: {0}'.format(OrionException))

    module.exit_json(changed=changed, orion_node=node)


if __name__ == "__main__":
    main()
