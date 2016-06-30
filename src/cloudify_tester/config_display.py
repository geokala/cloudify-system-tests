from cloudify_tester.config import (
    Config,
    default_schemas,
    SchemaError,
    NotSet,
)
from cloudify_tester.helpers.logger import TestLogger

import click
from jinja2 import Template

# Note: While config files are in yaml, using yaml.dump adds a newline with an
# ellipsis. JSON will be compatible, but doesn't add fluff.
import json
import sys


@click.command()
@click.option('--generate-sample-config', is_flag=True, default=False,
              help='Generate a sample config instead of showing options.')
@click.option('--validate', is_flag=True, default=False,
              help='Validate the test config (should be test_config.yaml.')
@click.option('--parse-template', default=None,
              help='Output parsed template based on the test config.')
def show_config_schema(generate_sample_config, validate, parse_template):
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
        if validate or parse_template:
            config_files = ['test_config.yaml']
        else:
            config_files = []
        config = Config(
            config_files=config_files,
            config_schema_files=default_schemas,
            logger=logger,
        )
    except SchemaError as e:
        print(e.message)
        sys.exit(1)
    except IOError:
        sys.stderr.write('Could not find test_config.yaml\n')
        sys.exit(2)

    if parse_template is not None:
        with open(parse_template) as template_handle:
            template = Template(template_handle.read())
        print(template.render(config))
    elif validate:
        namespaces = config.namespaces
        not_set_message = '{key} is not set and has no default!\n'
        for namespace in namespaces:
            if namespace is None:
                check = config.items()
            else:
                check = config[namespace].items()
            for key, value in check:
                display_key = key
                if namespace is not None:
                    display_key = '.'.join([namespace, key])
                if key not in namespaces:
                    if value is NotSet:
                        sys.stderr.write(not_set_message.format(
                            key=display_key,
                        ))
    else:
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
