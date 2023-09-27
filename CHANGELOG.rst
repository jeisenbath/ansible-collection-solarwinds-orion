==============================
Solarwinds.Orion Release Notes
==============================

.. contents:: Topics


v1.0.4
======

Release Summary
---------------

| Released 2023-09-26


Major Changes
-------------

- orion_node_interface module - add param 'regex' to explicitly state if you want to do pattern matching in interface name

Bugfixes
--------

- orion_node module - fix functionality for adding External nodes

v1.0.3
======

Release Summary
---------------

| Released 2023-08-27


Minor Changes
-------------

- orion_node module - add support for using credential sets for SNMPv3 nodes, updated documentation with params that are required for SNMPv3

Bugfixes
--------

- orion.py get_least_used_polling_engine - convert the query count to an int, to fix an issue with a deployment with only one poller

v1.0.2
======

Release Summary
---------------

| Released 2023-08-10


Minor Changes
-------------

- orion_node_interface module - add support for removing all interfaces if one is not specified

Bugfixes
--------

- orion.py add_interface function - only regex pattern match if exact interface name is not found
- orion_node module - don't set snmpv3 properties for node unless parameters are passed
- orion_node_application module - typo with param name 'skip_duplicates'
- orion_node_interface - add to documentation and examples to clarify regex pattern matching is supported

v1.0.1
======

Release Summary
---------------

| Released 2023-07-14


Minor Changes
-------------

- orion_node module - use datetime.now() instead of datetime.utcnow() for muting and unmanaging. utcnow() works fine for managing, but for muting the time needs to match server time to work correctly.

Bugfixes
--------

- orion_node module - add snmp_version required_if polling_method == 'SNMP'
- orion_node module - fix typo in logic for state 'managed'
- orion_node module - unset default for snmp version in parameters, to fix issue 2

v1.0.0
======

Release Summary
---------------

| Released 2023-03-18


New Modules
-----------

- solarwinds.orion.orion_custom_property - Manage custom properties on Node in Solarwinds Orion NPM
- solarwinds.orion.orion_node - Created/Removes/Edits Nodes in Solarwinds Orion NPM
- solarwinds.orion.orion_node_application - Manages APM application templates assigned to nodes.
- solarwinds.orion.orion_node_custom_poller - Creates/Removes custom pollers to a Node in Solarwinds Orion NPM
- solarwinds.orion.orion_node_info - Gets info about a Node in Solarwinds Orion NPM
- solarwinds.orion.orion_node_interface - Manage interfaces on Nodes in Solarwinds Orion NPM
- solarwinds.orion.orion_node_poller - Manage Pollers on Nodes in Solarwinds Orion NPM
- solarwinds.orion.orion_update_node - Updates Node in Solarwinds Orion NPM
- solarwinds.orion.orion_volume - Manage Volumes on Nodes in Solarwinds Orion NPM
- solarwinds.orion.orion_volume_info - Gets info about a Volume in Solarwinds Orion NPM
