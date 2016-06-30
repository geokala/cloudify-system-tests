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
@click.option(
    '--name',
    default=None,
    help=(
        'Where to clone the plugin to. Otherwise this will be inferred from '
        'the git repository name.'
    ),
)
def get_plugin_tests(git_repo, checkout, name):
    """
        Install the extra system tests from a given git repo.
        This repo must be able to be cloned by git clone <repo>.
        This repo is expected to contain:
          - a system_tests/features folder containing any features for this
            plugin
          - a system_tests/features/steps folder containing code for any extra
            steps this plugin provides/uses
            This steps folder should also contain the steps.py file provided
            in the base system tests, as this imports the default steps
          - a system_tests/features/environment.py, a copy of the one provided
            in the base system tests, as this sets up the environment for
            behave
        This repo may also contain:
          - a system_tests/templates folder containing any templates, e.g. for
            inputs
          - a system_tests/schemas folder containing one or more schemas for
            any extra configuration entries this plugin will use
          - a system_tests/setup.py file, which will cause pip install to be
            run on this path
    """
    logger = TestLogger(
        log_path=None,
        logger_name='plugin-test-retriever',
        log_format='%(message)s'
    )
    logger.console_logging_set_level('debug')

    executor = Executor(
        workdir=os.getcwd(),
        logger=logger,
        generate_env_files=False,
    )
    git = GitHelper(
        workdir=os.getcwd(),
        executor=executor,
    )

    # Guess name if it's not supplied
    if name is None:
        name = git_repo.split('/')[-1]
        if name.endswith('.git'):
            name = name[:-4]

    git.clone(
        repository=git_repo,
        clone_to=name,
    )
    git.checkout(
        repo_path=name,
        checkout=checkout,
    )

    plugin_tests_path = os.path.join(
        os.getcwd(), name, 'system_tests',
    )

    # Generate behave configuration to automatically find feature files
    if not os.path.exists('.behaverc'):
        with open('.behaverc', 'w') as conf_handle:
            conf_handle.write('[behave]\n')
            conf_handle.write('paths=features\n')
            conf_handle.write(
                'paths={plugin}/system_tests/features\n'.format(
                    plugin=name,
                )
            )
    else:
        this_features_path = 'paths={plugin}/system_tests/features\n'.format(
            plugin=name,
        )

        with open('.behaverc') as conf_handle:
            current_conf = conf_handle.readlines()

        if this_features_path not in current_conf:
            with open('.behaverc', 'a') as conf_handle:
                conf_handle.write(this_features_path)

    if os.path.isfile(os.path.join(plugin_tests_path, 'setup.py')):
        pip = PipHelper(
            workdir=os.getcwd(),
            executor=executor,
        )
        pip.install(plugin_tests_path)
