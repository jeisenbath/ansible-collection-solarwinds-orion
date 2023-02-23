# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Josh M. Eisenbath <j.m.eisenbath@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r"""
options:
    node_id:
        description:
            - Node ID of the node.
            - One of I(ip_address), I(node_id), or I(name) is required.
        required: false
        type: str
    name:
        description:
            - Name of the node.
            - One of I(ip_address), I(node_id), or I(name) is required.
        required: false
        type: str
        aliases: [ 'caption' ]
    ip_address:
        description:
            - IP Address of the node.
            - One of I(ip_address), I(node_id), or I(name) is required.
        required: false
        type: str
"""
