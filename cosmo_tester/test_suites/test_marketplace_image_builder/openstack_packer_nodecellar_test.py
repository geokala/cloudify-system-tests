########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

import time

from requests import ConnectionError
from cosmo_tester.framework.util import create_rest_client
from cosmo_tester.test_suites.test_blueprints.nodecellar_test\
    import NodecellarAppTest
from cosmo_tester.test_suites.test_marketplace_image_builder\
    .abstract_packer_test import AbstractPackerTest


class OpenstackNodecellarTest(NodecellarAppTest, AbstractPackerTest):

    def setUp(self):
        super(OpenstackNodecellarTest, self).setUp()

    def test_nodecellar_single_host(self):
        self.build_with_packer(only='openstack')
        self.deploy_image_openstack()

        self.client = create_rest_client(
            self.openstack_manager_public_ip
        )

        response = {'status': None}
        attempt = 0
        max_attempts = 40
        while response['status'] != 'running':
            try:
                response = self.client.manager.get_status()
            except ConnectionError:
                pass
            attempt += 1
            if attempt >= max_attempts:
                raise RuntimeError('Manager did not start in time')
            else:
                time.sleep(3)

        conf = self.env.cloudify_config
        self.openstack_nodecellar_inputs = {
            'user_ssh_key': conf['openstack_ssh_keypair_name'],
            'agents_security_group_name': 'system-tests-security-group',
            'agents_keypair_name': 'system-tests-keypair-name',
            'agents_user': conf.get('openstack_agents_user', 'ubuntu'),
            'openstack_username': conf['keystone_username'],
            'openstack_password': conf['keystone_password'],
            'openstack_auth_url': conf['keystone_url'],
            'openstack_tenant_name': conf['keystone_tenant_name'],
            'openstack_region': conf['region'],
        }

        time.sleep(90)
        # We have to retry this a few times, as even after the manager is
        # accessible we still see failures trying to create deployments
        deployment_created = False
        attempt = 0
        max_attempts = 40
        while not deployment_created:
            attempt += 1
            try:
                self.client.deployments.create(
                    blueprint_id='CloudifySettings',
                    deployment_id='config',
                    inputs=self.openstack_nodecellar_inputs,
                )
                deployment_created = True
            except Exception as err:
                # TODO: This should be a more specific exception
                if attempt >= max_attempts:
                    raise err

        self.client.executions.start(
            deployment_id='simple-blueprint.yaml',
            workflow_id='install',
        )

        self._test_nodecellar_impl('simple-blueprint.yaml')

    def get_public_ip(self, nodes_state):
        return self.openstack_manager_public_ip

    def get_inputs(self):
        conf = self.env.cloudify_config
        return {
            'agent_user': conf.get('openstack_agents_user', 'ubuntu'),
            'agent_private_key_path': '{0}/{1}-keypair.pem'.format(
                self.workdir,
                self.prefix
            ),
            'host_ip': self.openstack_manager_private_ip,
        }

    @property
    def expected_nodes_count(self):
        return 4

    @property
    def host_expected_runtime_properties(self):
        return []

    @property
    def entrypoint_node_name(self):
        return 'host'

    @property
    def entrypoint_property_name(self):
        return 'ip'
