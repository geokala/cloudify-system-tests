########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

from cosmo_tester.test_suites.test_blueprints import nodecellar_test


class EC2NodeCellarTest(nodecellar_test.NodecellarAppTest):

    def test_ec2_nodecellar(self):
        self._test_nodecellar_impl('ec2-blueprint.yaml')

    def get_inputs(self):

        return {
            'image': self.env.ubuntu_agent_ami,
            'size': self.env.medium_instance_type,
            'agent_user': 'ubuntu'
        }
