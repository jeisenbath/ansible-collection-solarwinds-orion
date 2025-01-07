#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.solarwinds.orion.plugins.module_utils.orion import OrionModule, orion_argument_spec
try:
    import requests
    HAS_REQUESTS = True
    requests.packages.urllib3.disable_warnings()
except ImportError:
    HAS_REQUESTS = False
except Exception:
    raise Exception
try:
    import orionsdk
    from orionsdk import SwisClient
    HAS_ORION = True
except ImportError:
    HAS_ORION = False
except Exception:
    raise Exception

# Documentation
# - name: Update SNMPv3 Credentials
#   solarwinds.orion.orion_node_update_snmpv3.py:
#     hostname: "{{ solarwinds_server }}"
#     username: "{{ solarwinds_user }}"
#     password: "{{ solarwinds_password }}"
#     name: "{{ inventory_hostname }}"
#     snmpv3_username: "{{ snmpv3_user }}"
#     snmpv3_auth_key: "{{ snmpv3_auth_pass }}"
#     snmpv3_auth_method: "{{ snmpv3_auth }}{{ snmpv3_auth_level }}"
#     snmpv3_priv_key: "{{ snmpv3_priv_pass }}"
#     snmpv3_priv_method: "{{ snmpv3_priv }}{{ snmpv3_priv_level }}"
#   delegate_to: localhost


def main():

    try:

        argument_spec = orion_argument_spec()

        argument_spec.update(
            name=dict(required=True, type='str'),
            auth_password=dict(required=False, type='str', no_log=True), 
            snmpv3_auth_key=dict(required=False, type='str', no_log=True),
            snmpv3_auth_method=dict(required=False, type='str'),
            context=dict(required=False, type='str'),
            snmpv3_username=dict(required=False, type='str'),
            snmpv3_priv_method=dict(required=False, type='str'),
            snmpv3_priv_key=dict(required=False, type='str', no_log=True),
            priv_key_is_password=dict(required=False, type='bool')
        )

        module = AnsibleModule(
            argument_spec,
            supports_check_mode=True,
            required_one_of=[('snmpv3_auth_key', 'snmpv3_auth_method', 'auth_key_is_password', 'context', 'snmpv3_username', 'snmpv3_priv_method', 'snmpv3_priv_key', 'priv_key_is_password')],
        )

        if not HAS_ORION:
            module.fail_json(msg='orionsdk required for this module')

        orion = OrionModule(module)

        returnVals = orion.swis_query(
            """
            SELECT
            n.NodeID,
            n.Caption,
            c.Name,
            c.ID,
            m.Username,
            m.AuthenticationKey,
            m.AuthenticationKeyIsPassword,
            m.AuthenticationMethod,
            m.Context,
            m.PrivacyKey,
            m.PrivacyKeyIsPassword,
            m.PrivacyMethod,
            c.Uri
            FROM Orion.Nodes n
            RIGHT JOIN 
            (SELECT SettingValue, NodeID
            FROM Orion.NodeSettings  
            WHERE SettingValue NOT LIKE '%[^0-9]%') s ON n.NodeID = s.NodeID
            LEFT JOIN Orion.Credential c ON c.ID = s.SettingValue
            LEFT JOIN Orion.SNMPv3Credentials m ON m.NodeID = s.NodeID
            WHERE n.Caption LIKE '%' + '{0}' + '%'
            """.format(module.params['name'])
        )[0]

        # debug file creation
        # queryFile = open('returnVals.txt', 'w')
        # queryFile.write(str(returnVals))
        # queryFile.close()

        credId = returnVals['ID']
        nodeId = returnVals['NodeID']
        name = returnVals['Name']
        snmpUsername = returnVals['Username']
        context = returnVals['Context']
        authenticationMethod = returnVals['AuthenticationMethod']
        authenticationPassword = returnVals['AuthenticationKey']
        authenticationKeyIsPassword = returnVals['AuthenticationKeyIsPassword']
        privacyMethod = returnVals['PrivacyMethod']
        privacyPassword = returnVals['PrivacyKey']
        privacyKeyIsPassword = returnVals['PrivacyKeyIsPassword']

        if module.params['auth_password'] is not None and module.params['auth_password'] != authenticationPassword:
            authenticationPassword = module.params['auth_password']
        elif module.params['auth_method'] is not None and module.params['auth_method'] != authenticationMethod:
            authenticationMethod = module.params['auth_method']
        elif module.params['auth_key_is_password'] is not None and module.params['auth_key_is_password'] != authenticationKeyIsPassword:
            authenticationKeyIsPassword = module.params['auth_key_is_password']
        elif module.params['context'] is not None and module.params['context'] != context:
            context = module.params['context']
        elif module.params['snmp_username'] is not None and module.params['snmp_username'] != snmpUsername:
            snmpUsername = module.params['snmp_username']
        elif module.params['priv_method'] is not None and module.params['priv_method'] != privacyMethod:
            privacyMethod = module.params['priv_method']
        elif module.params['priv_password'] is not None and module.params['priv_password'] != privacyPassword:
            privacyPassword = module.params['priv_password']
        elif module.params['priv_key_is_password'] is not None and module.params['priv_key_is_password'] != privacyKeyIsPassword:
            privacyKeyIsPassword = module.params['priv_key_is_password']
        else:
            module.exit_json(changed=False)
        
        orion.swis.invoke('Orion.Credential', 'UpdateSNMPv3Credentials',
                            credId,
                            name,
                            snmpUsername,
                            context,
                            authenticationMethod,
                            authenticationPassword,
                            authenticationKeyIsPassword,
                            privacyMethod,
                            privacyPassword,
                            privacyKeyIsPassword
                            )

# Look at displaying this in playbook
    except Exception as e:
        error_file3 = open('error3.txt', 'w')
        error_file3.write(str(e))
        error_file3.close()

    module.exit_json(changed=True)

if __name__ == "__main__":
    main()