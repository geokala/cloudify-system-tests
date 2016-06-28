import os


class GitHelper(object):
    def __init__(self, workdir, executor):
        self.workdir = workdir
        self._executor = executor

    def _exec(self, command, repo_path):
        prepared_command = ['git']
        prepared_command.extend(command)

        repo_path = os.path.join(self.workdir, repo_path)

        self._executor(prepared_command, cwd=repo_path)

    def clone(self, repository, clone_to=None):
        if not clone_to:
            # Clone to the repo name if no clone_to is provided
            clone_to = os.path.split(repository)[-1]

        path = os.path.join(self.workdir, clone_to)
        # This might want to be an is_dir check to give better error messages
        if not os.path.exists(path):
            os.mkdir(path)

        # We clone to 'current dir' in the repo path to simplify self._exec
        self._exec(['clone', repository, '.'], repo_path=clone_to)

    def checkout(self, repo_path, checkout):
        self._exec(['checkout', checkout], repo_path=repo_path)
