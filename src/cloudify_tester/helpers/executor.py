import os
import subprocess
import time


class RetriesExceededError(Exception):
    pass


class Executor(object):
    _env_cache = {}

    def __init__(self, workdir, logger):
        self.workdir = workdir
        self.logger = logger

    def __call__(self, command, path_prepends=None, env_var_overrides=None,
                 retries=3, retry_delay=3, cwd=None, fake=False,
                 expected_return_codes=(0,)):
        if env_var_overrides is None:
            env_var_overrides = {}
        if path_prepends is None:
            path_prepends = []
        if cwd is None:
            cwd = self.workdir

        # Get current env to modify
        os_env = os.environ.copy()

        # Update env vars
        os_env.update(env_var_overrides)

        # Update path
        path = os_env.get('PATH')
        path = path.split(':')
        new_path = path_prepends
        new_path.extend(path)
        new_path = ':'.join(new_path)
        os_env['PATH'] = new_path

        # See if we have already cached this env for user troubleshooting
        cache_file = None
        for dotfile, cached_env in self._env_cache.items():
            if cached_env == os_env:
                # We have, get the file name for logging
                cache_file = dotfile
        if cache_file is None:
            # We haven't. Cache it for user troubleshooting.
            cache_file = self._generate_dotfile(command, os_env)

        if fake:
            # We were asked to fake_run it, return an equivalent to what we
            # would have done so that it can be recreated
            fake_message = 'cd {path} && . "{env}" && {command}'
            return fake_message.format(
                command=' '.join(command),
                path=cwd,
                env=cache_file,
            )

        run_message = 'Running {command} in {path} with env vars from {env}'
        for attempt in range(0, retries):
            try:
                self.logger.info(
                    run_message.format(
                        command=' '.join(command),
                        path=cwd,
                        env=cache_file,
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
                    # It worked!
                    break
                elif attempt == retries:
                    raise RetriesExceededError(
                        'Retries exceeded for command {command} with final '
                        'return code {code}.'.format(
                            command=' '.join(command),
                            code=process.returncode,
                        )
                    )
                else:
                    # Not too good on that attempt, try again
                    self.logger.warn(
                        'Command {command} failed with return code {code}, '
                        'retrying.'.format(
                            command=' '.join(command),
                            code=process.returncode,
                        )
                    )
                    time.sleep(retry_delay)
            except:
                self.logger.exception(
                    'Command {command} failed:'.format(
                        command=' '.join(command),
                    )
                )
                raise
        return process

    def _log_process_output(self, process):
        for line in process.stdout.readlines():
            self.logger.info(line.rstrip('\n'))
        for line in process.stderr.readlines():
            self.logger.error(line.rstrip('\n'))

    def _generate_dotfile(self, command, env):
        candidate_filename = 'env_' + ''.join(command[:3])
        candidate_filename = candidate_filename.replace('/', '_')
        candidate_filename = candidate_filename.replace('"', '_')

        base_filename = candidate_filename
        suffix = 1
        candidate_filename = base_filename + '_{}'.format(suffix)

        while candidate_filename in self._env_cache.keys():
            suffix += 1
            candidate_filename = base_filename + '_{}'.format(suffix)

        env_file_path = os.path.join(self.workdir, candidate_filename)
        with open(env_file_path, 'w') as env_file_handle:
            for env_var, value in env.items():
                env_file_handle.write('{var}="{value}"\n'.format(
                    var=env_var,
                    value=value,
                ))
        self._env_cache[candidate_filename] = env

        return candidate_filename
