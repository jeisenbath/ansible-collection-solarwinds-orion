==============================
Solarwinds.Orion Release Notes
==============================

.. contents:: Topics


v1.3.2
======

Release Summary
---------------

Released 2024-04-17

Minor Changes
-------------

- inventory plugin orion_nodes_inventory - add ansible vault support for the password parameter

v1.3.1
======

Release Summary
---------------

Released 2024-03-11

Minor Changes
-------------

- orion_node_interface - refactored to try and make as idempotent as possible, and return 'discovered' and 'interface'

v1.3.0
======

Release Summary
---------------

Released 2024-03-07

Major Changes
-------------

- Add module orion_node_ncm - Adds/Removes an existing node to be managed in NCM.
- Add module orion_node_poller_info - Gets pollers assigned to a node and their enabled status.
- Add module orion_query - Runs a SWQL query against Orion database, outputs to json and optional CSV.

New Modules
-----------

- solarwinds.orion.orion_node_ncm - Manages a node in Solarwinds NCM
- solarwinds.orion.orion_node_poller_info - Gets info about pollers assigned to a Node in Solarwinds Orion NPM
- solarwinds.orion.orion_query - Queries the Solarwinds Orion database

v1.2.0
======

Release Summary
---------------

Released 2024-03-01

Major Changes
-------------

- Added a role orion_node
- Updated the example playbook to use the new role

v1.1.0
======

Release Summary
---------------

| Released 2023-12-1


Major Changes
-------------

- Add dynamic inventory plugin solarwinds.orion.orion_nodes_inventory

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
