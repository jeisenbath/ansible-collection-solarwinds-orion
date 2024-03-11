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
"""
