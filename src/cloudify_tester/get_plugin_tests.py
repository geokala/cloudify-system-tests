from cloudify_tester.helpers.logger import TestLogger
from cloudify_tester.helpers.git import GitHelper
from cloudify_tester.helpers.pip import PipHelper
from cloudify_tester.helpers.executor import Executor

import click

import os

@click.command()
@click.argument('git_repo')
@click.option('--checkout', default='master',
              help='What to git checkout from the repo.')
def get_plugin_tests(git_repo, checkout):
    """
        Install the extra system tests from a given git repo.
        This repo must be able to be cloned by git clone <repo>.
        This repo is expected to contain:
          - system_tests/setup.py- pip install will be run in the system tests
            folder
          - a system_tests/features folder containing any features for this
            plugin. These will be copied to the system tests features path
    """
    logger = TestLogger(
        log_path=None,
        logger_name='plugin-test-retriever',
    )

    git_executor = Executor(
        workdir=os.getcwd(),
        logger=logger,
    ).executor
    git = GitHelper(
        workdir=os.getcwd(),
        executor=git_executor,
    )

    executor = Executor(
        workdir='.get_plugin/system_tests',
        logger=logger,
    ).executor
    pip = PipHelper(
        workdir='.get_plugin/system_tests',
        executor=executor,
    )

    git.clone(
        repository=git_repo,
        clone_to='.get_plugin',
    )
    git.checkout(
        repo_path='.get_plugin',
        checkout=checkout,
    )

    pip.install('.')

    # Get features
    features_path = os.path.join(os.getcwd(), 'features')
    executor(['cp', 'features/*.feature', features_path])

    # Get templates
    templates_path = os.path.join(os.getcwd(), 'templates')
    executor(['cp', 'templates/*', templates_path])
