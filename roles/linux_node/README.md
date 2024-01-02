Role Name
=========

Adds a linux server node to be monitored in Solarwinds.

Requirements
------------

solarwinds.orion collection

Role Variables
--------------

defaults/main.yml
linux_node_standard_snmp_pollers - Default list of required pollers for basic load average, cpu, memory polling. Override at your own risk!
linux_node_polling_method - Default ICMP
linux_node_solarwinds_server - Defaults to variable {{ solarwinds_server }}
linux_node_solarwinds_username - Defaults to variable {{ solarwinds_username }}
linux_node_solarwinds_password - Defaults to variable {{ solarwinds_password }}
linux_node_caption_name - Default {{ ansible_facts.nodename }}, override if you aren't gathering facts or for custom caption
linux_node_ip_address - Default {{ ansible_facts.default_ipv4.address }}, override if you aren't gathering facts
linux_node_discover_interfaces - Default false, whether to discover and add all interfaces when polling method is SNMP

Optional variables
linux_node_snmp_version - required when linux_node_polling method is SNMP, set which version of SNMP (choices: 2, 3)
linux_node_ro_community_string - required when SNMP version is 2
linux_node_snmpv3_credential_set - required when SNMP version is 3
linux_node_snmpv3_username - required when SNMP version is 3
linux_node_snmpv3_auth_key - required when SNMP version is 3
linux_node_snmpv3_priv_key - required when SNMP version is 3
linux_node_snmp_port - override default SNMP port
linux_node_snmp_allow_64 - override default "True" value of device supporting 64 bit counters
linux_node_snmp_pollers - list, elements are dicts (name, enabled(bool)), additional standard orion pollers to add and enable/disable
linux_node_custom_pollers - list, additional custom UnDP pollers
linux_node_interfaces - list, interfaces to monitor
linux_node_volumes - list, volumes to monitor
linux_node_applications - list, APM templates to add to node
linux_node_custom_properties - list, elements are dicts (name, value), custom property names and values to set


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
         - { role: solarwinds.orion.linux_node }

License
-------

GPL-3.0-or-later

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
