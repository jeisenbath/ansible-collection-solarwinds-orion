
#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: orion_node_update_snmpv3
short_description: Update SNMPv3 credentials for a node in SolarWinds Orion
description:
    - Update SNMPv3 credentials for an existing node in SolarWinds Orion.
    - This module retrieves the current SNMPv3 credential record, updates any provided fields, and calls the SWIS API to update the entire credential set.
    - **Important:** The SWIS API requires that you provide the complete set of SNMPv3 credential parameters. Even if you only want to update the username, you must supply all other fields.
version_added: "3.1.0"
author:
    - "Your Name (@yourhandle)"
extends_documentation_fragment:
    - jeisenbath.solarwinds.orion_auth_options
    - jeisenbath.solarwinds.orion_node_options
requirements:
    - orionsdk
    - requests
options:
    snmpv3_username:
        description:
            - SNMPv3 username.
        required: false
        type: str
    snmpv3_auth_key:
        description:
            - SNMPv3 authentication key.
        required: false
        type: str
        no_log: true
    snmpv3_auth_method:
        description:
            - SNMPv3 authentication method.
        required: false
        type: str
        choices: [SHA1, MD5]
    snmpv3_priv_key:
        description:
            - SNMPv3 privacy key.
        required: false
        type: str
        no_log: true
    snmpv3_priv_method:
        description:
            - SNMPv3 privacy method.
        required: false
        type: str
        choices: [DES56, AES128, AES192, AES256]
    priv_key_is_password:
        description:
            - Indicates if the privacy key is a password.
        required: false
        type: bool
    context:
        description:
            - SNMPv3 context.
        required: false
        type: str
'''

EXAMPLES = r'''
- name: Update SNMPv3 credentials - full update (all values provided)
  jeisenbath.solarwinds.orion_node_update_snmpv3:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_password }}"
    name: "my-node-name"
    snmpv3_username: "new_snmp_user"
    snmpv3_auth_key: "new_auth_key"
    snmpv3_auth_method: "SHA1"
    snmpv3_priv_key: "new_priv_key"
    snmpv3_priv_method: "AES128"
    priv_key_is_password: True
    context: "new_context"
  delegate_to: localhost

- name: Partial update - only update the SNMPv3 username
  jeisenbath.solarwinds.orion_node_update_snmpv3:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_password }}"
    ip_address: "192.168.1.10"
    snmpv3_username: "snmp_test_user"
  delegate_to: localhost
'''

RETURN = r'''
orion_node:
    description: Info about the updated Orion node.
    returned: always
    type: dict
    sample: {
        "caption": "my-node-name",
        "ipaddress": "192.168.1.10",
        "lastsystemuptimepollutc": "2025-02-28T18:34:20.7630000Z",
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
except Exception as e:
    raise e

def main():
    # Merge common Orion arguments with SNMPv3-specific options.
    argument_spec = orion_argument_spec()
    argument_spec.update(
        snmpv3_username=dict(required=False, type='str'),
        snmpv3_auth_key=dict(required=False, type='str', no_log=True),
        snmpv3_auth_method=dict(required=False, type='str', choices=['SHA1', 'MD5']),
        snmpv3_priv_key=dict(required=False, type='str', no_log=True),
        snmpv3_priv_method=dict(required=False, type='str', choices=['DES56', 'AES128', 'AES192', 'AES256']),
        priv_key_is_password=dict(required=False, type='bool'),
        context=dict(required=False, type='str'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[('name', 'node_id', 'ip_address')],
    )

    # Initialize the Orion module.
    orion = OrionModule(module)

    # Retrieve the node.
    node = orion.get_node()
    if not node:
        module.fail_json(msg="Node not found")

    # Query for current SNMPv3 credentials for this node.
    cred_query = """
    SELECT 
        c.ID as CredentialID,
        c.Name as CredentialName,
        m.Username,
        m.AuthenticationKey,
        m.AuthenticationKeyIsPassword,
        m.AuthenticationMethod,
        m.Context,
        m.PrivacyKey,
        m.PrivacyKeyIsPassword,
        m.PrivacyMethod
    FROM Orion.Nodes n
    JOIN Orion.NodeSettings s ON n.NodeID = s.NodeID AND s.SettingName = 'ROSNMPCredentialID'
    JOIN Orion.Credential c ON c.ID = s.SettingValue
    JOIN Orion.SNMPv3Credentials m ON m.NodeID = n.NodeID
    WHERE n.NodeID = {0}
    """.format(node['nodeid'])
    try:
        cred_result = orion.swis.query(cred_query)
    except Exception as e:
        module.fail_json(msg="Failed to query SNMPv3 credentials: {0}".format(e))

    if not cred_result['results']:
        module.fail_json(msg="SNMPv3 credentials not found for this node")

    current_creds = cred_result['results'][0]

    # Build a complete set of credential values from current values.
    updated = {
        'Name': current_creds['CredentialName'],
        'Username': current_creds['Username'],
        'Context': current_creds['Context'],
        'AuthenticationMethod': current_creds['AuthenticationMethod'],
        'AuthenticationKey': current_creds['AuthenticationKey'],
        'AuthenticationKeyIsPassword': current_creds['AuthenticationKeyIsPassword'],
        'PrivacyMethod': current_creds['PrivacyMethod'],
        'PrivacyKey': current_creds['PrivacyKey'],
        'PrivacyKeyIsPassword': current_creds['PrivacyKeyIsPassword']
    }

    changed = False

    # Update each parameter if a new value is provided.
    if module.params.get('snmpv3_username') is not None and module.params['snmpv3_username'] != current_creds['Username']:
        updated['Username'] = module.params['snmpv3_username']
        changed = True

    if module.params.get('context') is not None and module.params['context'] != current_creds['Context']:
        updated['Context'] = module.params['context']
        changed = True

    if module.params.get('snmpv3_auth_method') is not None and module.params['snmpv3_auth_method'] != current_creds['AuthenticationMethod']:
        updated['AuthenticationMethod'] = module.params['snmpv3_auth_method']
        changed = True

    if module.params.get('snmpv3_auth_key') is not None and module.params['snmpv3_auth_key'] != current_creds['AuthenticationKey']:
        updated['AuthenticationKey'] = module.params['snmpv3_auth_key']
        changed = True

    if module.params.get('snmpv3_priv_method') is not None and module.params['snmpv3_priv_method'] != current_creds['PrivacyMethod']:
        updated['PrivacyMethod'] = module.params['snmpv3_priv_method']
        changed = True

    if module.params.get('snmpv3_priv_key') is not None and module.params['snmpv3_priv_key'] != current_creds['PrivacyKey']:
        updated['PrivacyKey'] = module.params['snmpv3_priv_key']
        changed = True

    if module.params.get('priv_key_is_password') is not None and module.params['priv_key_is_password'] != current_creds['PrivacyKeyIsPassword']:
        updated['PrivacyKeyIsPassword'] = module.params['priv_key_is_password']
        changed = True

    # Call the API to update SNMPv3 credentials.
    if changed and not module.check_mode:
        try:
            orion.swis.invoke(
                'Orion.Credential',
                'UpdateSNMPv3Credentials',
                current_creds['CredentialID'],
                updated['Name'],
                updated['Username'],
                updated['Context'],
                updated['AuthenticationMethod'],
                updated['AuthenticationKey'],
                updated['AuthenticationKeyIsPassword'],
                updated['PrivacyMethod'],
                updated['PrivacyKey'],
                updated['PrivacyKeyIsPassword']
            )
        except Exception as e:
            module.fail_json(msg="Failed to update SNMPv3 credentials: {0}".format(e))

    module.exit_json(changed=changed, orion_node=node)

if __name__ == '__main__':
    main()
