class PipHelper(object):
    def __init__(self, workdir, executor):
        self.workdir = workdir
        self._executor = executor

    def _exec(self, command, install_plugins=False):
        prepared_command = ['bin/pip']
        prepared_command.extend(command)
        self._executor(prepared_command)

    def install(self, packages):
        if not isinstance(packages, list):
            packages = [packages]
        command = ['install']
        command.extend(packages)
        self._exec(command)
