# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Josh M. Eisenbath <j.m.eisenbath@gmail.com>
# Copyright: (c) 2019, Jarett D. Chaiken <jdc@salientcg.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from dateutil.parser import parse
import re


orion_argument_spec = dict(
    hostname=dict(required=True),
    username=dict(required=True, no_log=True),
    password=dict(required=True, no_log=True),
    node_id=dict(required=False),
    ip_address=dict(required=False),
    name=dict(required=False, aliases=['caption']),
)


class OrionModule:

    def __init__(self, module, swis):
        self.module = module
        self.swis = swis

    def swis_query(self, query):
        results = self.swis.query(query)
        if results['results']:
            return results['results']

    def get_node(self):
        node = {}
        fields = """NodeID, Caption, Unmanaged, UnManageFrom, UnManageUntil, Uri,
                  ObjectSubType, IP_Address, Status, StatusDescription"""

        if self.module.params['node_id']:
            results = self.swis.query(
                "SELECT {0} FROM Orion.Nodes WHERE NodeID = '{1}'".format(fields, self.module.params['node_id'])
            )
        elif self.module.params['ip_address']:
            results = self.swis.query(
                "SELECT {0} FROM Orion.Nodes WHERE IPAddress = '{1}'".format(fields, self.module.params['ip_address'])
            )
        elif self.module.params['name']:
            results = self.swis.query(
                "SELECT {0} FROM Orion.Nodes WHERE Caption = '{1}'".format(fields, self.module.params['name'])
            )

        if results['results']:
            node['nodeid'] = results['results'][0]['NodeID']
            node['caption'] = results['results'][0]['Caption']
            node['netobjectid'] = 'N:{0}'.format(node['nodeid'])
            node['unmanaged'] = results['results'][0]['Unmanaged']
            node['unmanagefrom'] = parse(results['results'][0]['UnManageFrom']).isoformat()
            node['unmanageuntil'] = parse(results['results'][0]['UnManageUntil']).isoformat()
            node['uri'] = results['results'][0]['Uri']
            node['objectsubtype'] = results['results'][0]['ObjectSubType']
            node['ipaddress'] = results['results'][0]['IP_Address']
            node['status'] = results['results'][0]['Status']
            node['statusdescription'] = results['results'][0]['StatusDescription']
        return node

    def add_custom_property(self, node, prop_name, prop_value):
        custom_property = {prop_name: prop_value}
        self.swis.update(node['uri'] + '/CustomProperties', **custom_property)

    def get_node_custom_property_value(self, node, prop_name):
        custom_property_query = self.swis.query(
            "SELECT {0} FROM Orion.NodesCustomProperties WHERE NodeId = {1}".format(prop_name, node['nodeid'])
        )
        return prop_name, custom_property_query['results'][0][prop_name]

    def get_poller(self, net_object_type, net_object_id, poller_name):
        net_obj = '{0}:{1}'.format(net_object_type, net_object_id)
        poller_query = self.swis.query(
            "SELECT PollerType, Enabled, Uri FROM Orion.Pollers "
            "WHERE NetObject = '{0}' AND PollerType = '{1}'".format(net_obj, poller_name)
        )

        if poller_query['results']:
            return poller_query['results'][0]

    def add_poller(self, net_object_type, net_object_id, poller_name, enabled):
        poller = {
            'PollerType': poller_name,
            'NetObject': '{0}:{1}'.format(net_object_type, net_object_id),
            'NetObjectType': net_object_type,
            'NetObjectID': net_object_id,
            'Enabled': enabled
        }

        get_poller = self.get_poller(net_object_type, net_object_id, poller_name)

        if not get_poller:
            self.swis.create('Orion.Pollers', **poller)
        elif get_poller['Enabled'] != enabled:
            self.swis.update(get_poller['Uri'], **poller)

    def remove_poller(self, net_object_type, net_object_id, poller_name):
        get_poller = self.get_poller(net_object_type, net_object_id, poller_name)

        if get_poller:
            self.swis.delete(get_poller['Uri'])

    def get_custom_poller_id(self, poller_name):
        custom_poller_id = self.swis.query(
            "SELECT CustomPollerID FROM Orion.NPM.CustomPollers WHERE UniqueName = '{0}'".format(poller_name)
        )

        if custom_poller_id['results']:
            return custom_poller_id['results'][0]['CustomPollerID']

    def get_custom_poller_uri(self, node, poller_name):
        node_id = str(node['nodeid'])
        custom_poller_uri = self.swis.query(
            "SELECT Uri FROM Orion.NPM.CustomPollerAssignment "
            "WHERE NodeID = '{0}' and CustomPollerName = '{1}'".format(node_id, poller_name)
        )

        if custom_poller_uri['results']:
            return custom_poller_uri['results'][0]['Uri']

    def add_custom_poller(self, node, poller_name):
        node_id = str(node['nodeid'])
        custom_poller_id = self.get_custom_poller_id(poller_name)

        custom_poller_uri = self.get_custom_poller_uri(node, poller_name)

        if not custom_poller_uri:
            poller_properties = {
                'NodeID': node_id,
                'customPollerID': custom_poller_id
            }
            self.swis.create('Orion.NPM.CustomPollerAssignmentOnNode', **poller_properties)

    def remove_custom_poller(self, node, poller_name):
        custom_poller_uri = self.get_custom_poller_uri(node, poller_name)

        if custom_poller_uri:
            self.swis.delete(custom_poller_uri)

    def get_volume(self, node, volume):
        volume_info = {}
        fields = """volumeid, displayname, volumeindex, status, type, caption, pollinterval,
                    statcollection, rediscoveryinterval, volumedescription, icon, uri"""

        volume_query = self.swis.query(
            "SELECT {0} FROM Orion.Volumes WHERE nodeid = '{1}' AND caption = '{2}'".format(
                fields, str(node['nodeid']), str(volume['name'])
            )
        )

        if volume_query['results']:
            volume_info['volumeid'] = volume_query['results'][0]['volumeid']
            volume_info['displayname'] = volume_query['results'][0]['displayname']
            volume_info['volumeindex'] = volume_query['results'][0]['volumeindex']
            volume_info['status'] = volume_query['results'][0]['status']
            volume_info['type'] = volume_query['results'][0]['type']
            volume_info['caption'] = volume_query['results'][0]['caption']
            volume_info['pollinterval'] = volume_query['results'][0]['pollinterval']
            volume_info['statcollection'] = volume_query['results'][0]['statcollection']
            volume_info['rediscoveryinterval'] = volume_query['results'][0]['rediscoveryinterval']
            volume_info['volumedescription'] = volume_query['results'][0]['volumedescription']
            volume_info['icon'] = volume_query['results'][0]['icon']
            volume_info['uri'] = volume_query['results'][0]['uri']
        return volume_info

    def add_volume(self, node, volume):
        max_index = 0
        volume_type_id = {
            "Other": 1,
            "RAM": 2,
            "Virtual Memory": 3,
            "Fixed Disk": 4,
        }

        volume_max_index_query = self.swis.query(
            "SELECT MAX(VolumeIndex) as max_index FROM Orion.Volumes WHERE nodeid = '{0}'".format(
                str(node['nodeid'])
            )
        )

        if volume_max_index_query['results'][0]['max_index']:
            max_index = volume_max_index_query['results'][0]['max_index']

        if not volume['volumeDescription']:
            volume['volumeDescription'] = volume['name']

        volume_data = {
            'NodeID': str(node['nodeid']),
            'VolumeType': volume['volumeType'],
            'VolumeTypeID': volume_type_id[volume['volumeType']],
            'Icon': volume['volumeIcon'],
            'VolumeIndex': max_index + 1,
            'Caption': volume['name'],
            'VolumeDescription': volume['volumeDescription'],
            'PollInterval': volume['pollInterval'],
            'StatCollection': volume['statCollection'],
            'RediscoveryInterval': volume['rediscoveryInterval'],
            'VolumeResponding': 'Y',
        }

        self.swis.create('Orion.Volumes', **volume_data)

    def remove_volume(self, node, volume):
        volume_info = self.get_volume(node, volume)

        if volume_info['uri']:
            self.swis.delete(volume_info['uri'])

    def discover_interfaces(self, node):

        discovered_interfaces = self.swis.invoke('Orion.NPM.Interfaces', 'DiscoverInterfacesOnNode', node['nodeid'])

        return discovered_interfaces['DiscoveredInterfaces']

    def get_interface(self, node, interface_name):
        interface_uri = self.swis.query(
            "SELECT Uri FROM Orion.NPM.Interfaces "
            "WHERE NodeID = '{0}' AND InterfaceName = '{1}'".format(node['nodeid'], interface_name)
        )

        if interface_uri['results']:
            return interface_uri['results'][0]['Uri']

    def add_interface(self, node, interface_name, regex, discovered_interfaces):
        added_interfaces = []
        if regex:
            discovered_interface = [
                x for x
                in discovered_interfaces
                if re.search(interface_name, x['Caption'])
            ]
        else:
            discovered_interface = [
                x for x
                in discovered_interfaces
                if interface_name == x['Caption']
            ]

        if discovered_interface:
            for interface in discovered_interface:
                if interface['InterfaceID'] == 0:
                    add = self.swis.invoke('Orion.NPM.Interfaces', 'AddInterfacesOnNode', node['nodeid'], discovered_interface, 'AddDefaultPollers')
                    added_interfaces = add['DiscoveredInterfaces']
                    break

        return added_interfaces

    def remove_interface(self, node, interface_name):
        interface_uri = self.get_interface(node, interface_name)

        if interface_uri:
            self.swis.delete(interface_uri)

    def get_application_template_id(self, application_template_name):

        app_template_id = self.swis.query(
            "select ApplicationTemplateID from Orion.APM.ApplicationTemplate where name = '{0}'".format(application_template_name)
        )

        if app_template_id['results']:
            return app_template_id['results'][0]['ApplicationTemplateID']

    def get_apm_credential_id(self, credential_name):

        credential_id = self.swis.query(
            "select ID from Orion.Credential where CredentialOwner = 'APM' and Name = '{0}'".format(credential_name)
        )

        if credential_id['results']:
            return credential_id['results'][0]['ID']

    def get_application_id(self, node, application_name):

        application = self.swis.query(
            "select ApplicationID from Orion.APM.Application where nodeid = '{0}' and Name = '{1}'".format(node['nodeid'], application_name)
        )

        if application['results']:
            return application['results'][0]['ApplicationID']

    def add_application_template_to_node(self, node, application_template_id, credential_set_id, skip_if_duplicate):

        application = self.swis.invoke(
            'Orion.APM.Application', 'CreateApplication', node['nodeid'], application_template_id, credential_set_id, skip_if_duplicate
        )

        if application:
            self.swis.invoke('Orion.APM.Application', 'PollNow', application)

        return application

    def remove_application_template_from_node(self, application_id):

        application = self.swis.invoke(
            'Orion.APM.Application', 'DeleteApplication', application_id
        )

        return application

    def get_least_used_polling_engine(self):
        queryengines = self.swis.query("SELECT count(EngineId) as NumEngines FROM Orion.Engines")
        totalpollingengines = int(queryengines['results'][0]['NumEngines'])

        if totalpollingengines > 1:
            queryleast = self.swis.query(
                "SELECT TOP 1 Nodes, EngineID FROM Orion.Engines WHERE EngineID != 1 ORDER BY Nodes asc"
            )
            leastusedpollingengine = queryleast['results'][0]['EngineID']
            return leastusedpollingengine
        else:
            return "1"

    def get_ncm_node(self, node):
        cirrus_node_query = self.swis.query(
            "SELECT NodeID from Cirrus.Nodes WHERE CoreNodeID = '{0}'".format(node['nodeid'])
        )
        if cirrus_node_query['results']:
            return cirrus_node_query['results'][0]['NodeID']

    def add_node_to_ncm(self, node):
        self.swis.invoke('Cirrus.Nodes', 'AddNodeToNCM', node['nodeid'])

    def remove_node_from_ncm(self, node):
        cirrus_node_id = self.get_ncm_node(node)

        self.swis.invoke('Cirrus.Nodes', 'RemoveNode', cirrus_node_id)
