# Copyright (c) 2011 OpenStack, LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Handles configuration options for the tests."""

import json
import os
from collections import Mapping

#TODO(tim.simpson): I feel like this class already exists somewhere in core
#                   Python.
class FrozenDict(Mapping):

    def __init__(self, original):
        self.original = original

    def __len__(self):
        return self.original.__len__()

    def __iter__(self, *args, **kwargs):
        return self.original.__iter__(self, *args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        return self.original.__getitem__(*args, **kwargs)

    def __str__(self):
        return self.original.__str__()


class TestConfig(object):
    """
    Holds test configuration values which can be accessed as attributes
    or using the values dictionary.
    """

    def __init__(self):
        """
        Create TestConfig, and set default values. These will be overwritten by
        the "load_from" methods below.
        """
        self._values = {
            'clean_slate': os.environ.get("CLEAN_SLATE", "False") == "True",
            'fake_mode': os.environ.get("FAKE_MODE", "False") == "True",
            'nova_auth_url':"http://localhost:5000/v2.0",
            'reddwarf_auth_url':"http://localhost:5000/v2.0/tokens",
            'dbaas_url': "http://localhost:8775/v1.0/dbaas",
            'version_url': "http://localhost:8775/",
            'nova_url': "http://localhost:8774/v1.1",
            'instance_create_time': 16 * 60,
            'dbaas_image': None,
            'typical_nova_image_name': None,
            'white_box': False,
            'test_mgmt': False,
            'use_local_ovz':False,
        }
        self._frozen_values = FrozenDict(self._values)
        self._users = None

    def load_from_line(self, line):
        index = line.find("=")
        if index >= 0:
            key = line[:index]
            value = line[index + 1:]
            self._values[key] = value

    def load_from_file(self, file_path):
        file_contents = open(file_path, "r").read()
        try:
            contents = json.loads(file_contents)
            self._values.update(contents)
        except Exception as exception:
            raise RuntimeError("Error loading conf file \"" + file_path + "\".",
                               exception)

    def __getattr__(self, name):
        if name not in self._values:
            raise AttributeError('Configuration value "%s" not found.' % name)
        else:
            return self._values[name]

    def python_cmd_list():
        """The start of a command list to use when running Python scripts."""
        commands = []
        if self.use_venv:
            commands.append("%s/tools/with_venv.sh" % self.nova_code_root)
            return list
        commands.append("python")
        return commands

    @property
    def users(self):
        if self._users is None:
            from tests.util.users import Users
            self._users = Users(self.values['users'])
        return self._users

    @property
    def values(self):
        return self._frozen_values


CONFIG = TestConfig()
del TestConfig.__init__