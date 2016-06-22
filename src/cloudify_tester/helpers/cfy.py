import os
from subprocess import check_output

import yaml


class CfyHelper(object):
    def __init__(self, workdir):
        self.workdir = workdir

    def _exec(self, command, install_plugins=False):
        prepared_command = ['bin/cfy']
        if install_plugins:
            prepared_command.append('--install-plugins')
        prepared_command.extend(command)
        check_output(prepared_command, cwd=self.workdir)

    def create_inputs(self, inputs_dict, inputs_name='inputs.yaml'):
        inputs_yaml = yaml.dump(inputs_dict)
        with open(os.path.join(self.workdir, inputs_name)) as inputs_handle:
            inputs_handle.write(inputs_yaml)

    def local_init(self, blueprint_path, inputs_path, install_plugins=False):
        return self._exec(
            [
                'local', 'init',
                '--blueprint-path', blueprint_path,
                '--inputs', inputs_path,
            ],
            install_plugins=install_plugins,
        )

    def local_execute(self, workflow):
        return self._exec(['local', 'execute', '--workflow', workflow])
