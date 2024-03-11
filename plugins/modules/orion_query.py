#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Josh M. Eisenbath <j.m.eisenbath@gmail.com>
# Copyright: (c) 2024, Andrew  Bailey
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: orion_query
short_description: Queries the Solarwinds Orion database
description:
    - "Run a query to get info from the Solarwinds Orion database."
    - "Will return the query results as a json object, which can be registered and used with other modules."
    - "Optionally can also save results into a csv."
version_added: "1.3.0"
author: 
    - "Josh M. Eisenbath (@jeisenbath)"
    - "Andrew  Bailey (@andyjb8)"
options:
    query:
        description:
            - SWQL query
        required: true
        type: str
    csv_path:
        description:
            - The path to save the output CSV file.
        required: false
        type: str
extends_documentation_fragment:
    - solarwinds.orion.orion_auth_options
requirements:
    - orionsdk
    - requests
    - csv
'''

EXAMPLES = r'''
---

- name: Run a query for the top 10 nodes in Orion.Nodes
  solarwinds.orion.orion_query:
    hostname: "{{ solarwinds_server }}"
    username: "{{ solarwinds_user }}"
    password: "{{ solarwinds_pass }}"
    query: |
      SELECT
        TOP 10 N.NodeID, N.Caption, N.IP_Address, N.MachineType, N.Vendor, N.StatusIcon, N.IOSVersion, N.IOSImage, CP.City, CP.Department
      FROM
        Orion.Nodes AS N
      LEFT JOIN Orion.NodesCustomProperties AS CP ON N.NodeID = CP.NodeID
    csv_path: ./results.csv
  delegate_to: localhost

'''

RETURN = r'''
results:
    description: Results of SWQL query.
    returned: always
    type: list
    sample: [
        {
            "Caption": "localhost",
            "City": "Villa Straylight",
            "Department": null,
            "IOSImage": "",
            "IOSVersion": "",
            "IP_Address": "127.0.0.1",
            "MachineType": "net-snmp - Linux",
            "NodeID": 12345,
            "StatusIcon": "Up.gif                                  ",
            "Vendor": "net-snmp"
        }
    ]

'''

import requests
import csv
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.solarwinds.orion.plugins.module_utils.orion import OrionModule

try:
    from orionsdk import SwisClient
    HAS_ORION = True
except Exception as OrionSdkImport:
    HAS_ORION = False

requests.packages.urllib3.disable_warnings()


def write_to_csv(nodes, csv_file_path):
    headers = nodes[0].keys() if nodes else []
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for node in nodes:
            writer.writerow(node)


def main():
    argument_spec = dict(
        hostname=dict(required=True),
        username=dict(required=True, no_log=True),
        password=dict(required=True, no_log=True),
        query=dict(required=True, type=str),
        csv_path=dict(required=False, type=str),
    )
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
    )

    options = {
        'hostname': module.params['hostname'],
        'username': module.params['username'],
        'password': module.params['password'],
    }

    __SWIS__ = SwisClient(**options)

    try:
        __SWIS__.query('SELECT uri FROM Orion.Environment')
    except Exception as AuthException:
        module.fail_json(
            msg='Failed to query Orion. '
                'Check Hostname, Username, and/or Password: {0}'.format(str(AuthException))
        )

    orion = OrionModule(module, __SWIS__)

    results = orion.swis_query(module.params['query'])
    if module.params['csv_path']:
        write_to_csv(results, module.params['csv_path'])

    module.exit_json(changed=False, results=results)


if __name__ == "__main__":
    main()
