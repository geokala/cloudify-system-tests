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
    logger.console_logging_set_level('debug')

    executor = Executor(
        workdir=os.getcwd(),
        logger=logger,
    ).executor
    git = GitHelper(
        workdir=os.getcwd(),
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

    plugin_tests_path = os.path.join(
        os.getcwd(), '.get_plugin', 'system_tests',
    )

    pip = PipHelper(
        workdir=os.getcwd(),
        executor=executor,
    )
    pip.install(plugin_tests_path)

    # Get features
    new_features_path = os.path.join(plugin_tests_path, 'features')
    features_path = os.path.join(os.getcwd(), 'features')
    for new_feature in os.listdir(new_features_path):
        if new_feature.endswith('.feature'):
            new_feature = os.path.join(new_features_path, new_feature)
            executor(['cp', new_feature, features_path])

    # Get templates
    new_templates_path = os.path.join(plugin_tests_path, 'templates')
    templates_path = os.path.join(os.getcwd(), 'templates')
    for new_template in os.listdir(new_templates_path):
        new_template = os.path.join(new_templates_path, new_template)
        executor(['cp', new_template, templates_path])

    # Clean up downloaded plugin
    executor(['rm', '-rf', '.get_plugin'])
