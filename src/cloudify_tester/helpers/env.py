from cloudify_tester.helpers.git import GitHelper
from cloudify_tester.helpers.cfy import CfyHelper
from cloudify_tester.helpers.pip import PipHelper
from cloudify_tester.helpers.logger import TesterLogger

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

    def start(self,
              cloudify_version=None,
              logging_level='debug',
              log_to_console=False):
        self.workdir = tempfile.mkdtemp()

        # Set up logger
        self.logger = TesterLogger(self.workdir)
        self.logger.file_logging_set_level(logging_level)
        if log_to_console:
            self.logger.console_logging_set_level(logging_level)
        else:
            self.logger.console_logging_disable()

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

    def teardown(self, run_cleanup=True, remove_workdir=True):
        # Cleanups should be run in reverse to clean up the last entity that
        # was added to the stack first
        for cleanup in reversed(self._cleanups):
            func = cleanup['function']
            args = cleanup.get('args', [])
            kwargs = cleanup.get('kwargs', {})
            kwargs['fake_run'] = not run_cleanup
            result = func(*args, **kwargs)
            if not run_cleanup:
                cleanup_intent_path = os.path.join(self.workdir,
                                                   'cleanup_intent.log')
                with open(cleanup_intent_path, 'a') as cleanup_intent_handle:
                    cleanup_intent_handle.write('{command}\n'.format(
                        command=result,
                    ))

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
            fake = not remove_workdir
            self.executor(['rm', '-rf', self.workdir], cwd='/tmp', fake=fake)

    def executor(self, command, path_prepends=None, env_var_overrides=None,
                 retries=3, retry_delay=3, cwd=None, fake=False,
                 expected_return_codes=(0,)):
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

        run_message = 'Running {command} in {directory} with {env}'
        if fake:
            run_message = 'Asked for: ' + run_message
            return run_message.format(
                command=' '.join(command),
                directory=cwd,
                env=os_env,
            )

        for i in range(0, retries):
            try:
                self.logger.info(
                    run_message.format(
                        command=' '.join(command),
                        directory=cwd,
                        env=os_env,
                    )
                )
                process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    env=os_env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                while process.returncode is None:
                    self._log_process_output(process)
                    process.poll()
                self._log_process_output(process)
                if process.returncode in expected_return_codes:
                    break
                else:
                    time.sleep(retry_delay)
            except:
                self.logger.exception('Command {command} failed:'.format(
                    command=' '.join(command),
                ))
                raise
        return process.returncode

    def _log_process_output(self, process):
        for line in process.stdout.readlines():
            self.logger.info(line.rstrip('\n'))
        for line in process.stderr.readlines():
            self.logger.error(line.rstrip('\n'))
