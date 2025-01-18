#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Josh M. Eisenbath <j.m.eisenbath@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: orion_node_ncm
short_description: Manages a node in Solarwinds NCM
description:
    - Adds or removes an existing Orion node to NCM.
version_added: "1.3.0"
author: "Josh M. Eisenbath (@jeisenbath)"
options:
    state:
        description:
            - Desired state the node.
        required: True
        type: str
        choices:
            - present
            - absent
    profile_name:
        description:
            - Connection Profile Name Predefined on Orion NCM.
        default: '-1'
        required: false
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

- name: Add Node to NCM
  jeisenbath.solarwinds.orion_node_ncm:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    name: "{{ node_name }}"
    state: present
    profile_name: "{{ profile_name }}"
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
        "unmanagefrom": "1899-12-30T00:00:00+00:00",
        "unmanageuntil": "1899-12-30T00:00:00+00:00",
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


def index_connection_profiles(orion_module):
    """Takes an Orion module object and enumerates all available connection profiles for later use. Returns a dictionary."""
    profile_list = orion_module.swis_get_ncm_connection_profiles()
    profile_dict = {}
    for k in range(0, len(profile_list)):
        profile_name = profile_list[k]['Name']
        profile_id = profile_list[k]['ID']
        # create a mapping between the profile name (i.e. "Juniper_NCM") and the back-end numeric ID number
        profile_dict.update({profile_name: profile_id})
    return profile_dict


def main():
    # start with generic Orion arguments
    argument_spec = orion_argument_spec()
    # add desired fields to list of module arguments
    argument_spec.update(
        state=dict(required=True, choices=['present', 'absent']),
        profile_name=dict(required=False, type='str', default='-1'),  # required field unless user wants to unset a connection profile
    )
    # initialize the custom Ansible module
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        required_one_of=[('name', 'node_id', 'ip_address')],
    )

    # create an OrionModule object using our custom Ansible module
    orion = OrionModule(module)

    node = orion.get_node()
    if not node:
        # if get_node() returns None, there's no node
        module.fail_json(skipped=True, msg='Node not found')

    if module.params['state'] == 'present':
        try:
            ncm_node = orion.get_ncm_node(node)
            if ncm_node:
                profile_dict = index_connection_profiles(orion)
                if module.check_mode:
                    if orion.get_ncm_node_object(ncm_node)['ConnectionProfile'] != profile_dict[module.params['profile_name']]:
                        module.exit_json(changed=True, orion_node=node, msg="Check mode: no changes made.")
                    else:
                        module.exit_json(changed=False, orion_node=node)
                was_changed = orion.update_ncm_node_connection_profile(profile_dict, module.params['profile_name'], ncm_node)
                if was_changed:
                    module.exit_json(changed=True, orion_node=node)
                else:
                    module.exit_json(changed=False, orion_node=node)
            else:
                # if the node is not already in NCM, add the node and update the connection profile
                if module.check_mode:
                    module.exit_json(changed=False, orion_node=node)
                else:
                    # add the node to NCM
                    orion.add_node_to_ncm(node)
                    # collect the NCM node ID of the node
                    ncm_node = orion.get_ncm_node(node)
                    profile_dict = index_connection_profiles(orion)
                    # update the connection profile
                    was_changed = orion.update_ncm_node_connection_profile(profile_dict, module.params['profile_name'], ncm_node)
                    module.exit_json(changed=True, orion_node=node)
                    if was_changed:
                        module.exit_json(changed=True, orion_node=node)
                    else:
                        module.exit_json(changed=False, orion_node=node)
        except Exception as OrionException:
            module.fail_json(msg='Failed to add or update node in NCM: {0}'.format(OrionException))

    elif module.params['state'] == 'absent':
        try:
            ncm_node = orion.get_ncm_node(node)
            if ncm_node:
                if module.check_mode:
                    module.exit_json(changed=True, orion_node=node)
                else:
                    orion.remove_node_from_ncm(node)
                    module.exit_json(changed=True, orion_node=node)
            else:
                module.exit_json(changed=False, orion_node=node)
        except Exception as OrionException:
            module.fail_json(msg='Failed to remove application from node: {0}'.format(OrionException))

    module.exit_json(changed=False)


if __name__ == "__main__":
    main()
