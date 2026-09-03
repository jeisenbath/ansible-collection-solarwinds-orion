#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: orion_discover_node
short_description: Discover nodes in Orion NPM.
description:
    - "Run Discovery on an IP Address."
version_added: "3.3.0"
author:
    - "Josh M. Eisenbath (@jeisenbath)"
options:
    allow_duplicate_nodes:
        description:
            - Discovery profile "AllowDuplicateNodes" parameter.
        required: false
        type: bool
        default: false
    auto_import:
        description:
            - Discovery profile "IsAutoImport" parameter.
        required: false
        type: bool
        default: true
    delay:
        description:
            - Delay, in seconds, between discovery status checks.
        required: false
        type: int
        default: 1
    delete_discovery_profile:
        description:
            - Discovery profile "IsHidden" parameter.
        required: false
        type: bool
        default: true
    discovery_hop_count:
        description:
            - Discovery profile "HopCount" parameter.
        required: false
        type: int
        default: 0
    disable_icmp:
        description:
            - Discovery profile "DisableIcmp" parameter.
        required: false
        type: bool
        default: false
    job_timeout_seconds:
        description:
            - Discovery profile "JobTimeoutSeconds" parameter.
        required: false
        type: int
        default: 3600
    name:
        description:
            - Name of the node.
        required: false
        aliases: [ 'caption' ]
        type: str
    interface_statuses:
        description:
            - Interface statuses to include in discovery.
        required: false
        type: list
        elements: str
        choices:
            - Up
            - Down
            - Shutdown
        default: ['Up']
    interface_filter:
        description:
            - Filter for interface discovery.
            - Interfaces much match all filters to be discovered.
        type: list
        elements: dict
        suboptions:
            prop:
                description:
                    - Property to filter on.
                required: false
                type: str
                default: 'Descr'
                choices:
                    - 'Type'
                    - 'Name'
                    - 'Descr'
                    - 'Alias'
                    - 'Node'
                    - 'All'
                    - 'Vlan'
            op:
                description:
                    - Match operator.
                required: false
                type: str
                default: '!Regex'
                choices:
                    - 'All'
                    - '!All'
                    - 'Any'
                    - '!Any'
                    - 'Equals'
                    - '!Equals'
                    - 'Regex'
                    - '!Regex'
                    - '#All'
                    - '!#All'
                    - '#Any'
                    - '!#Any'
            val:
                description:
                    - Value of filter.
                type: str
                required: false
    ip_address:
        description:
            - IP Address of the node.
        required: true
        type: str
    polling_engine:
        description:
            - ID of polling engine that NPM will use to poll this device.
            - If not passed, will query for the Polling Engine with least nodes assigned.
        required: false
        type: str
    polling_method:
        description:
            - Polling method to use.
        choices:
            - SNMP
            - WMI
        default: SNMP
        required: false
        type: str
    retries:
        description:
            - Number of retries to check discovery status until timeout.
        required: false
        type: int
        default: 60
    search_timeout:
        description:
            - Discovery profile "SearchTimeoutMiliseconds" parameter.
        required: false
        type: int
        default: 5000
    snmp_credential_set:
        description:
            - Credential set name for SNMP credentials.
        type: str
        required: false
    snmp_port:
        description:
            - Port that SNMP server listens on.
        required: false
        default: "161"
        type: str
    snmp_timeout:
        description:
            - Discovery profile "SnmpTimeoutMiliseconds" parameter.
        required: false
        type: int
        default: 5000
    snmp_version:
        description:
            - SNMPv2c or SNMPv3 for snmp polling.
        choices:
            - "2"
            - "3"
        default: "3"
        required: false
        type: str
    wmi_credential_set:
        description:
            - 'Credential Name already configured in NPM  Found under "Manage Windows Credentials" section of the Orion website (Settings).'
            - Required if I(polling_method=wmi).
        required: false
        type: str
    virtual_types:
        description:
            - Interface virtual types to discover.
        required: false
        type: list
        elements: str
        choices: ['Physical', 'Virtual', 'Unknown']
        default: ['Physical', 'Virtual', 'Unknown']
    vlan_port_types:
        description:
            - Interface port types to discover.
        required: false
        type: list
        elements: str
        default: ['Trunk', 'Access', 'Unknown']
        choices: ['Trunk', 'Access', 'Unknown']
extends_documentation_fragment:
    - jeisenbath.solarwinds.orion_auth_options
requirements:
    - orionsdk
    - requests
'''

EXAMPLES = '''
---
- name: Discover one SNMPv3 IP Address, exclude loopback interface
  orion_discover_node: &discover_snmp_node
    hostname: "{{ orion_test_solarwinds_server }}"
    username: "{{ orion_test_solarwinds_username }}"
    password: "{{ orion_test_solarwinds_password }}"
    ip_address: "{{ orion_test_node_ip_address }}"
    polling_method: SNMP
    snmp_version: 3
    snmp_credential_set: "{{ orion_test_node_snmpv3_credential_set }}"
    interface_filter:
      - op: '!Regex'
        val: '^lo'
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
        "uri": "swis://host.domain.com/Orion/Orion.Nodes/NodeID=12345",
        "snmp_validation_passed": false,
        "snmp_validation_error": "SNMP validation failed - device did not respond to SNMP poll"
    }
'''


from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.jeisenbath.solarwinds.plugins.module_utils.orion import OrionModule
from ansible_collections.jeisenbath.solarwinds.plugins.module_utils.credential import get_credentials
from time import sleep
from datetime import datetime, timezone
try:
    import requests
    HAS_REQUESTS = True
    requests.packages.urllib3.disable_warnings()
except ImportError:
    HAS_REQUESTS = False
except Exception:
    raise


def discovery_status(module, orion, profileId, retries, delay):
    statusQuery = 'SELECT Status FROM Orion.DiscoveryProfiles WHERE ProfileID = {0}'.format(profileId)
    statusMap = {
        0: "Unknown",
        1: "InProgress",
        2: "Finished",
        3: "Error",
        4: "NotScheduled",
        5: "Scheduled",
        6: "NotCompleted",
        7: "Canceling",
        8: "ReadyForImport",
    }
    # profile gets deleted too quick to check if status is no longer running
    status = 1
    i = 0
    if module.params['delete_discovery_profile']:
        while status and i <= retries:
            i += 1
            sleep(delay)
            status = orion.swis_query(statusQuery)
        status = 2
    else:
        while status == 1 and i <= retries:
            i += 1
            sleep(delay)
            status = int(orion.swis_query(statusQuery)[0]['Status'])
    return statusMap[status]


def build_interface_plugin_conf(module, orion):
    # Always filter null and empty
    expressionFilters = [
        {"Prop": "Descr", "Op": "!Any", "Val": "null"},
        {"Prop": "Descr", "Op": "!Regex", "Val": "^$"},
    ]
    if 'interface_filter' in module.params and module.params["interface_filter"]:
        expressionFilters += module.params["interface_filter"]

    interfacesPluginContext = {
        "AutoImportStatus": module.params['interface_statuses'],
        "AutoImportVlanPortTypes": module.params['vlan_port_types'],
        "AutoImportVirtualTypes": module.params['virtual_types'],
        "AutoImportExpressionFilter": expressionFilters,
        "UseDefaults": False,
    }

    interfacesPluginConfig = orion.swis.invoke(
        "Orion.NPM.Interfaces",
        "CreateInterfacesPluginConfiguration",
        interfacesPluginContext,
    )
    return interfacesPluginConfig


def discover_node(module, orion):
    if module.params['polling_engine']:
        pollingEngine = module.params['polling_engine']
    else:
        pollingEngine = orion.get_least_used_polling_engine()

    credential = get_credentials(orion, module.params['snmp_credential_set'])

    corePluginContext = {
        'BulkList': [{'Address': module.params['ip_address']}],
        'Credentials': [{'CredentialID': credential['ID'], 'Order': 1}],
        'WmiRetriesCount': 0,
        'WmiRetryIntervalMiliseconds': 1000
    }
    try:
        corePluginConfig = orion.swis.invoke('Orion.Discovery', 'CreateCorePluginConfiguration', corePluginContext)
    except Exception:
        raise

    if module.params['snmp_version'] == 2:
        snmp_version = 'SNMP2c'
    else:
        snmp_version = 'SNMP3'

    interfacesPluginConfig = build_interface_plugin_conf(module, orion)
    discoveryProfile = {
        'Name': f"ansible_orion_discover_node: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}",
        'EngineID': pollingEngine,
        'JobTimeoutSeconds': module.params['job_timeout_seconds'],
        'SearchTimeoutMiliseconds': module.params['search_timeout'],
        'SnmpTimeoutMiliseconds': module.params['snmp_timeout'],
        'SnmpRetries': 2,
        'RepeatIntervalMiliseconds': 1800,
        'SnmpPort': module.params['snmp_port'],
        'HopCount': module.params['discovery_hop_count'],
        'PreferredSnmpVersion': snmp_version,
        'DisableIcmp': module.params['disable_icmp'],
        'AllowDuplicateNodes': module.params['allow_duplicate_nodes'],
        'IsAutoImport': module.params['auto_import'],
        'IsHidden': module.params['delete_discovery_profile'],
        'PluginConfigurations': [
            {'PluginConfigurationItem': corePluginConfig},
            {'PluginConfigurationItem': interfacesPluginConfig}
        ]
    }
    try:
        result = int(orion.swis.invoke('Orion.Discovery', 'StartDiscovery', discoveryProfile))
    except Exception:
        raise
    return result


def get_discovered(orion, profileId):
    dlogQuery = "SELECT Result, ResultDescription, ErrorMessage, BatchID FROM Orion.DiscoveryLogs WHERE ProfileID = {0}".format(profileId)
    dlogResult = orion.swis_query(dlogQuery)
    dlogItemsQuery = "SELECT EntityType, DisplayName, NetObjectID FROM Orion.DiscoveryLogItems WHERE BatchID = \'{0}\'".format(dlogResult[0]['BatchID'])
    dlogItems = orion.swis_query(dlogItemsQuery)
    return dlogItems


def main():
    argument_spec = dict(
        hostname=dict(fallback=(env_fallback, ['SOLARWINDS_SERVER']), required=False),
        username=dict(fallback=(env_fallback, ['SOLARWINDS_USERNAME']), required=False, no_log=True),
        password=dict(fallback=(env_fallback, ['SOLARWINDS_PASSWORD']), required=False, no_log=True),
        port=dict(required=False, type='str', default='17774'),
        verify=dict(required=False, type='bool', default=False),
        ip_address=dict(required=True, type='str'),
        name=dict(required=False, aliases=['caption']),
        allow_duplicate_nodes=dict(required=False, type='bool', default=False),
        auto_import=dict(required=False, type='bool', default=True),
        delete_discovery_profile=dict(required=False, type='bool', default=True),
        delay=dict(required=False, type='int', default=1),
        disable_icmp=dict(required=False, type='bool', default=False),
        discovery_hop_count=dict(required=False, type='int', default=0),
        interface_statuses=dict(required=False, type='list', elements='str', default=['Up'], choices=['Up', 'Down', 'Shutdown']),
        interface_filter=dict(required=False, type='list', elements='dict', options=dict(
            prop=dict(default='Descr', type='str', choices=['Type', 'Name', 'Descr', 'Alias', 'Node', 'All', 'Vlan']),
            op=dict(default='!Regex', type='str', choices=[
                'All', '!All', 'Any', '!Any', 'Equals', '!Equals', 'Regex', '!Regex', '#All', '!#All', '#Any', '!#Any'
            ]),
            val=dict(type='str'),
        )),
        job_timeout_seconds=dict(required=False, type='int', default=3600),
        search_timeout=dict(required=False, type='int', default=5000),
        snmp_timeout=dict(required=False, type='int', default=5000),
        polling_method=dict(required=False, default='SNMP', choices=['SNMP', 'WMI']),
        retries=dict(required=False, type='int', default=60),
        snmp_version=dict(required=False, default='3', choices=['2', '3']),
        snmp_credential_set=dict(required=False, default=None, type='str'),
        snmp_port=dict(required=False, default='161'),
        wmi_credential_set=dict(required=False, no_log=True),
        polling_engine=dict(required=False),
        virtual_types=dict(required=False, type='list', elements='str', default=['Physical', 'Virtual', 'Unknown'], choices=['Physical', 'Virtual', 'Unknown']),
        vlan_port_types=dict(required=False, type='list', elements='str', default=['Trunk', 'Access', 'Unknown'], choices=['Trunk', 'Access', 'Unknown']),
    )
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        required_if=[
            ('polling_method', 'SNMP', ['snmp_version', 'snmp_credential_set']),
            ('polling_method', 'WMI', ['wmi_credential_set']),
        ],
    )
    orion = OrionModule(module)
    node = orion.get_node()
    changed = False
    discovered = None
    if not node:
        if not module.check_mode:
            discoveryProfileId = discover_node(module, orion)
            discoveredStatus = discovery_status(module, orion, discoveryProfileId, module.params['retries'], module.params['delay'])
            if discoveredStatus == 'Error':
                module.fail_json(msg='Discovery completed with Error status.')
            elif discoveredStatus == 'Finished':
                node = orion.get_node()
                discovered = get_discovered(orion, discoveryProfileId)
            else:
                module.fail_json('Discovery timed out, status is {0}'.format(discoveredStatus))
        changed = True

    response = {'changed': changed, 'orion_node': node}
    if discovered:
        response['discovered'] = discovered
    module.exit_json(**response)


if __name__ == "__main__":
    main()
