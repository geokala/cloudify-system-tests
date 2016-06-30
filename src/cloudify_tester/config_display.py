from cloudify_tester.config import Config, default_schemas
from cloudify_tester.helpers.logger import TestLogger

import click

# Note: While config files are in yaml, using yaml.dump adds a newline with an
# ellipsis. JSON will be compatible, but doesn't add fluff.
import json


@click.command()
@click.option('--generate-sample-config', is_flag=True, default=False,
              help='Generate a sample config instead of showing options.')
def show_config_schema(generate_sample_config):
    """
        Show all acceptable config entries according to the schema.
    """
    logger = TestLogger(
        log_path=None,
        logger_name='config',
    )
    logger.console_logging_set_level('debug')

    config = Config(
        config_files=[],
        config_schema_files=default_schemas,
        logger=logger,
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
