from cloudify_tester.helpers.logger import TestLogger
from cloudify_tester.helpers.git import GitHelper
from cloudfiy_tester.helpers.pip import PipHelper

import click


@click.command()
@click.argument('git_repo')
@click.option('--checkout', default='master',
              help='What to git checkout from the repo.')
def get_plugin_tests(git_repo):
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

    

    sorted_config_entries = config.schema.keys()
    sorted_config_entries.sort()

    for config_entry in sorted_config_entries:
        details = config.schema[config_entry]
        if generate_sample_config:
            if 'default' in details.keys():
                print('{entry}: {default}'.format(
                    entry=config_entry,
                    default=json.dumps(details['default'])
                ))
            else:
                print('{entry}: '.format(entry=config_entry))
        else:
            line = '{entry}: {description}'
            if 'default' in config.schema[config_entry].keys():
                line = line + ' (Default: {default})'
            line = line.format(
                entry=config_entry,
                description=details['description'],
                default=json.dumps(details.get('default')),
            )
            print(line)
