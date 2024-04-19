# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Josh M. Eisenbath <j.m.eisenbath@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r"""
options:
    hostname:
        description:
            - Name of Orion host running SWIS service.
        required: true
        type: str
    username:
        description:
            - Orion Username.
            - Active Directory users must use DOMAIN\\username format.
        required: true
        type: str
    password:
        description:
            - Password for Orion user.
        required: true
        type: str
    port:
        description:
            - Port to connect to the Solarwinds Information Service API.
            - Solarwinds ver. 2024.1.0 and on has a new API on port 17774, with legacy supported on 17778.
            - This argument was introduced in orionsdk 0.4.0 to support connecting to either API.
            - If using an older version of Solarwinds with orionsdk 0.4.0, define this as port 17778.
        required: false
        default: 17774
        type: str
    verify:
        description:
            - Verify SSL Certificate for Solarwinds Information Service API.
            - Requires orionsdk >= 0.4.0
        required: false
        default: false
        type: bool
"""
