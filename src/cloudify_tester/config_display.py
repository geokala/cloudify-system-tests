from cloudify_tester.config import Config, default_schemas, SchemaError
from cloudify_tester.helpers.logger import TestLogger

import click

# Note: While config files are in yaml, using yaml.dump adds a newline with an
# ellipsis. JSON will be compatible, but doesn't add fluff.
import json
import sys


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
        log_format='%(message)s'
    )
    logger.console_logging_set_level('debug')

    try:
        config = Config(
            config_files=[],
            config_schema_files=default_schemas,
            logger=logger,
        )
    except SchemaError as e:
        print(e.message)
        sys.exit(1)

    show_entries(config.schema, generate_sample_config)


def show_entries(schema, generate_sample_config=False, indent=''):
    sorted_config_entries = schema.keys()
    sorted_config_entries = [
        entry for entry in sorted_config_entries
        if isinstance(schema[entry], dict)
    ]
    sorted_config_entries.sort()

    namespaces = [
        entry for entry in sorted_config_entries
        if schema[entry].get('.is_namespace', False)
    ]
    root_config_entries = [
        entry for entry in sorted_config_entries
        if entry not in namespaces
    ]

    for config_entry in root_config_entries:
        details = schema[config_entry]
        if generate_sample_config:
            if 'default' in details.keys():
                print(indent + '{entry}: {default}'.format(
                    entry=config_entry,
                    default=json.dumps(details['default'])
                ))
            else:
                print(indent + '{entry}: '.format(entry=config_entry))
        else:
            line = '{entry}: {description}'
            if 'default' in schema[config_entry].keys():
                line = line + ' (Default: {default})'
            line = line.format(
                entry=config_entry,
                description=details['description'],
                default=json.dumps(details.get('default')),
            )
            print(indent + line)

    for namespace in namespaces:
        print(indent + namespace + ':')
        show_entries(
            schema[namespace],
            generate_sample_config,
            indent + '  ',
        )
