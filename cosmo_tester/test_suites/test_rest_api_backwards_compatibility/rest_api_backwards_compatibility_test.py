########
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
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


import json
import os
import shutil
import subprocess
import pkg_resources
import cosmo_tester
from jinja2.environment import Template

from cosmo_tester.framework.testenv import TestCase


SHELL_SCRIPT_TEMPLATE = 'run_old_rest_client_in_shell.template'
PYTHON_SCRIPT_TEMPLATE = 'use_old_rest_client.template'
SHELL_SCRIPT_NAME = 'test_old_client.sh'
PYTHON_SCRIPT_NAME = 'test_old_client.py'
VENV_NAME = 'cfy_32_cli_env'
VENV_FOLDER = '/tmp'
CFY_CLIENT_VERSION = '3.2'


class RestApiBackwardsCompatibilityTest(TestCase):

    def setUp(self):
        super(RestApiBackwardsCompatibilityTest, self).setUp()
        self._render_python_script()
        self._render_shell_script()

    def tearDown(self):
        venv_path = os.path.join(VENV_FOLDER, VENV_NAME)
        if os.path.exists(venv_path):
            shutil.rmtree(venv_path)

        if os.path.exists(PYTHON_SCRIPT_NAME):
            os.remove(PYTHON_SCRIPT_NAME)

        if os.path.exists(SHELL_SCRIPT_NAME):
            os.remove(SHELL_SCRIPT_NAME)

        super(RestApiBackwardsCompatibilityTest, self).tearDown()

    def _render_python_script(self):
        python_script_template = pkg_resources.resource_string(
            cosmo_tester.__name__,
            'resources/scripts/{0}'.format(PYTHON_SCRIPT_TEMPLATE)
        )
        rendered_python_script = Template(python_script_template). \
            render(cfy_manager_ip=self.env.management_ip)
        with open(PYTHON_SCRIPT_NAME, 'w') as f:
            f.write(rendered_python_script)

    def _render_shell_script(self):
        shell_script_template = pkg_resources.resource_string(
            cosmo_tester.__name__,
            'resources/scripts/{0}'.format(SHELL_SCRIPT_TEMPLATE)
        )
        template_values = {'venv_name': VENV_NAME,
                           'venv_folder': VENV_FOLDER,
                           'client_version': CFY_CLIENT_VERSION,
                           'python_script_name': PYTHON_SCRIPT_NAME}
        rendered_shell_script = Template(shell_script_template).\
            render(template_values)
        with open(SHELL_SCRIPT_NAME, 'w') as f:
            f.write(rendered_shell_script)

        # set permission to execute file
        permissions = os.stat(SHELL_SCRIPT_NAME)
        os.chmod(SHELL_SCRIPT_NAME, permissions.st_mode | 0111)

    def test_old_client_vs_new_server(self):
        output = subprocess.check_output(
            '/bin/bash {0}'.format(SHELL_SCRIPT_NAME), shell=True)
        print('output: {0}'.format(output))
        result = json.loads(output)
        self.assertEqual(result.get('exit_code'), 0,
                         'Failed to get manager status from old client, '
                         'error: {0}'.format(result.get('details')))
