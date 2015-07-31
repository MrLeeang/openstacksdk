# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
test_rebuild_server
----------------------------------

Tests for the `rebuild_server` command.
"""

from mock import patch, Mock
import os_client_config
from shade import meta
from shade import OpenStackCloud
from shade.exc import (OpenStackCloudException, OpenStackCloudTimeout)
from shade.tests.unit import base


class TestRebuildServer(base.TestCase):

    def setUp(self):
        super(TestRebuildServer, self).setUp()
        config = os_client_config.OpenStackConfig()
        self.client = OpenStackCloud(cloud_config=config.get_one_cloud())

    def test_rebuild_server_rebuild_exception(self):
        """
        Test that an exception in the novaclient rebuild raises an exception in
        rebuild_server.
        """
        with patch("shade.OpenStackCloud"):
            config = {
                "servers.rebuild.side_effect": Exception("exception"),
            }
            OpenStackCloud.nova_client = Mock(**config)
            self.assertRaises(
                OpenStackCloudException, self.client.rebuild_server, "a", "b")

    def test_rebuild_server_server_error(self):
        """
        Test that a server error while waiting for the server to rebuild
        raises an exception in rebuild_server.
        """
        with patch("shade.OpenStackCloud"):
            config = {
                "servers.rebuild.return_value": Mock(status="REBUILD"),
                "servers.get.return_value": Mock(status="ERROR")
            }
            OpenStackCloud.nova_client = Mock(**config)
            self.assertRaises(
                OpenStackCloudException,
                self.client.rebuild_server, "a", "b", wait=True)

    def test_rebuild_server_timeout(self):
        """
        Test that a timeout while waiting for the server to rebuild raises an
        exception in rebuild_server.
        """
        with patch("shade.OpenStackCloud"):
            config = {
                "servers.rebuild.return_value": Mock(status="REBUILD"),
                "servers.get.return_value": Mock(status="REBUILD")
            }
            OpenStackCloud.nova_client = Mock(**config)
            self.assertRaises(
                OpenStackCloudTimeout,
                self.client.rebuild_server, "a", "b", wait=True, timeout=0.001)

    def test_rebuild_server_no_wait(self):
        """
        Test that rebuild_server with no wait and no exception in the
        novaclient rebuild call returns the server instance.
        """
        with patch("shade.OpenStackCloud"):
            mock_server = Mock(status="ACTIVE")
            config = {
                "servers.rebuild.return_value": mock_server
            }
            OpenStackCloud.nova_client = Mock(**config)
            self.assertEqual(meta.obj_to_dict(mock_server),
                             self.client.rebuild_server("a", "b"))

    def test_rebuild_server_wait(self):
        """
        Test that rebuild_server with a wait returns the server instance when
        its status changes to "ACTIVE".
        """
        with patch("shade.OpenStackCloud"):
            mock_server = Mock(status="ACTIVE")
            config = {
                "servers.rebuild.return_value": Mock(status="REBUILD"),
                "servers.get.return_value": mock_server
            }
            OpenStackCloud.nova_client = Mock(**config)
            self.assertEqual(meta.obj_to_dict(mock_server),
                             self.client.rebuild_server("a", "b", wait=True))
