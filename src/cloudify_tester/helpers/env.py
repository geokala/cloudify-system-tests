from cloudify_tester.helpers.git import GitHelper
from cloudify_tester.helpers.cfy import CfyHelper
from cloudify_tester.helpers.pip import PipHelper

from copy import copy
import os
import subprocess
import tempfile
import time


class DangerousBugError(Exception):
    pass


class TestEnvironment(object):
    cfy = None
    git = None
    pip = None
    _cleanups = []
    manager_bootstrap_completed = False
    blueprints = []
    deployments = []
    deployments_outputs = {}

    def start(self, cloudify_version=None):
        self.workdir = tempfile.mkdtemp()
        self.cfy = CfyHelper(workdir=self.workdir, executor=self.executor)
        self.git = GitHelper(workdir=self.workdir, executor=self.executor)
        self.pip = PipHelper(workdir=self.workdir, executor=self.executor)

        self.executor(['virtualenv', '.'])
        if cloudify_version:
            cloudify = 'cloudify=={version}'.format(
                version=cloudify_version
            )
        else:
            cloudify = 'cloudify'
        self.pip.install(cloudify)

    def add_cleanup(self, function, args=None, kwargs=None):
        cleanup = {
            'function': function,
        }
        if args is not None:
            cleanup['args'] = args
        if kwargs is not None:
            cleanup['kwargs'] = kwargs
        self._cleanups.append(cleanup)

    def teardown(self, run_cleanup=True):
        # TODO:
        # run_cleanup == False should cause cleanup functions to just say what
        # they were trying to do into a file in the workdir, but for now we'll
        # just abort if it's set
        # TODO: Have separate flag to keep workdir, as that's where we'll dump
        # logs (as well as stdout depending on config setting)
        if not run_cleanup:
            return

        # Cleanups should be run in reverse to clean up the last entity that
        # was added to the stack first
        for cleanup in reversed(self._cleanups):
            func = cleanup['function']
            args = cleanup.get('args', [])
            kwargs = cleanup.get('kwargs', {})
            func(*args, **kwargs)

        # This will break on a Mac (and Windows), so should have a better
        # check, but it probably wants something just to avoid major pain on
        # a single typo in a later commit
        if not self.workdir.startswith('/tmp/'):
            raise DangerousBugError(
                'An attempt was made to delete something not in a temp '
                'directory. Target was: {path}'.format(
                    path=self.workdir,
                )
            )
        else:
            self.executor(['rm', '-rf', self.workdir], cwd='/tmp')

    def executor(self, command, path_prepends=None, env_var_overrides=None,
                 retries=3, retry_delay=3, cwd=None):
        if env_var_overrides is None:
            env_var_overrides = {}
        if path_prepends is None:
            path_prepends = []
        if cwd is None:
            cwd = self.workdir

        # TODO: Split this impenetrable block up a bit
        # Env modifications
        os_env = copy(os.environ)
        # Update path
        path = os_env.get('PATH')
        path = path.split(':')
        new_path = path_prepends
        new_path.extend(path)
        new_path = ':'.join(new_path)
        os_env['PATH'] = new_path
        # TODO: Fix horrible naming (and I think this can be one linered)
        for k, v in env_var_overrides.items():
            os_env[k] = v
        # TODO: Dump current env vars to a file that can be dot sourced

        for i in range(0, retries):
            try:
                process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    env=os_env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                while process.returncode is None:
                    # TODO: This should use logger
                    for line in process.stdout.readlines():
                        print(line.rstrip())
                    for line in process.stderr.readlines():
                        print(line.rstrip())
                    process.poll()
                for line in process.stdout.readlines():
                    print(line.rstrip())
                for line in process.stderr.readlines():
                    print(line.rstrip())
                return process.returncode
            except:
                time.sleep(retry_delay)
