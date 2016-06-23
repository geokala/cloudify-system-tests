import os
from subprocess import check_output

import yaml


class CfyHelperBase(object):
    def __init__(self, workdir):
        self.workdir = workdir

    def _exec(self, command, install_plugins=False):
        prepared_command = ['bin/cfy']
        prepared_command.extend(command)
        if install_plugins:
            prepared_command.append('--install-plugins')
        # TODO: Logging
        print(' '.join(prepared_command))
        check_output(prepared_command, cwd=self.workdir)


class CfyHelper(CfyHelperBase):
    def __init__(self, workdir):
        super(CfyHelper, self).__init__(workdir=workdir)
        self.local = _CfyLocalHelper(workdir=workdir)
        self.blueprints = _CfyBlueprintsHelper(workdir=workdir)
        self.deployments = _CfyDeploymentsHelper(workdir=workdir)
        self.executions = _CfyExecutionsHelper(workdir=workdir)

    def create_inputs(self, inputs_dict, inputs_name='inputs.yaml'):
        inputs_yaml = yaml.dump(inputs_dict)
        with open(os.path.join(self.workdir, inputs_name),
                  'w') as inputs_handle:
            inputs_handle.write(inputs_yaml)

    def init(self):
        return self._exec(['init'])

    def bootstrap(self, blueprint_path, inputs_path, install_plugins=False):
        return self._exec(
            [
                'bootstrap',
                '--blueprint-path', blueprint_path,
                '--inputs', inputs_path,
            ],
            install_plugins=install_plugins,
        )

    def teardown(self, ignore_deployments=False):
        command = ['teardown', '-f']
        if ignore_deployments:
            command.append('--ignore-deployments')
        return self._exec(command)


class _CfyLocalHelper(CfyHelperBase):
    def init(self, blueprint_path, inputs_path, install_plugins=False):
        return self._exec(
            [
                'local', 'init',
                '--blueprint-path', blueprint_path,
                '--inputs', inputs_path,
            ],
            install_plugins=install_plugins,
        )

    def execute(self, workflow):
        return self._exec(['local', 'execute', '--workflow', workflow])


class _CfyBlueprintsHelper(CfyHelperBase):
    def upload(self, blueprint_path, blueprint_id, validate=False):
        command = [
            'blueprints', 'upload',
            '--blueprint-path', blueprint_path,
            '--blueprint-id', blueprint_id,
        ]
        if validate:
            command.append('--validate')
        return self._exec(command)

    def delete(self, blueprint_id):
        return self._exec([
            'blueprints', 'delete',
            '--blueprint-id', blueprint_id,
        ])


class _CfyDeploymentsHelper(CfyHelperBase):
    def create(self, blueprint_id, deployment_id, inputs_path=None):
        command = [
            'deployments', 'create',
            '--blueprint-id', blueprint_id,
            '--deployment-id', deployment_id,
        ]
        if inputs_path is not None:
            command.extend(['--inputs', inputs_path])
        return self._exec(command)

    def delete(self, deployment_id, ignore_live_nodes=False):
        command = [
            'deployments', 'delete',
            '--deployment-id', deployment_id,
        ]
        if ignore_live_nodes:
            command.append('--ignore-live-nodes')
        return self._exec(command)


class _CfyExecutionsHelper(CfyHelperBase):
    def start(self, deployment_id, workflow, timeout=900):
        command = [
            'executions', 'start',
            '--deployment-id', deployment_id,
            '--workflow', workflow,
            '--timeout', timeout,
        ]
        self._exec(command)
