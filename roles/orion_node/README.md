Role Name
=========

Adds an node to be monitored in Solarwinds.

Requirements
------------

solarwinds.orion collection

Role Variables
--------------

defaults/main.yml
orion_node_solarwinds_server - Defaults to variable {{ solarwinds_server }}
orion_node_solarwinds_username - Defaults to variable {{ solarwinds_username }}
orion_node_solarwinds_password - Defaults to variable {{ solarwinds_password }}
orion_node_caption_name - Default {{ ansible_facts.nodename }}, override if you aren't gathering facts or for custom caption
orion_node_ip_address - Default {{ ansible_facts.default_ipv4.address }}, override if you aren't gathering facts
orion_node_polling_method - Default ICMP
orion_node_snmp_pollers - list, elements are dicts (name, enabled(bool)). Default is only CPU and Memory pollers.
orion_node_discover_interfaces - Default false, whether to discover and add all interfaces when polling method is SNMP

Optional variables
orion_node_snmp_version - required when orion_node_polling method is SNMP, set which version of SNMP (choices: 2, 3)
orion_node_ro_community_string - required when SNMP version is 2
orion_node_snmpv3_credential_set - required when SNMP version is 3
orion_node_snmpv3_username - required when SNMP version is 3
orion_node_snmpv3_auth_key - required when SNMP version is 3
orion_node_snmpv3_priv_key - required when SNMP version is 3
orion_node_snmp_port - override default SNMP port
orion_node_snmp_allow_64 - override default "True" value of device supporting 64 bit counters

orion_node_custom_pollers - list, additional custom UnDP pollers
orion_node_interfaces - list, interfaces to monitor
orion_node_volumes - list, volumes to monitor
orion_node_applications - list, APM templates to add to node
orion_node_custom_properties - list, elements are dicts (name, value), custom property names and values to set


Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - name: Add servers to Solarwinds as simple ICMP nodes
      hosts: servers
      gather_facts: true
      vars:
        solarwinds_server: 127.0.0.1
        solarwinds_username: admin
        solarwinds_password: changeme2345
      roles:
         - { role: solarwinds.orion.orion_node }

License
-------

GPL-3.0-or-later

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
