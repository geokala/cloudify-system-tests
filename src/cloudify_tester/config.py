import yaml

import atexit
import os
import pkg_resources

class SchemaError(Exception):
    pass


class NotSet(object):
    def __repr__(self):
        return 'not set'


class Config(object):
    schema = {}
    raw_config = {}

    def __init__(self, config_files, config_schema_files, logger):
        self.logger = logger

        # Load all initially supplied schemas
        for schema in config_schema_files:
            self.update_schema(schema)
        # We'll be pretty useless if we allow no config
        if len(self.schema) == 0:
            raise SchemaError('No valid config entries loaded from schemas.')

        # Load config
        for config in config_files:
            self.update_config(config)

    def update_config(self, config_file):
        with open(config_file) as config_handle:
            raw_config = yaml.load(config_handle.read())
        self.raw_config.update(raw_config)
        self.check_config_is_valid()

    def update_schema(self, schema_file):
        with open(schema_file) as schema_handle:
            schema = yaml.load(schema_handle.read())

        # Make sure the schema is entirely valid- every entry must have a
        # description
        healthy_schema = True
        for key, value in schema.items():
            if 'description' not in value.keys():
                self.logger.error(
                    '{key} in schema does not have description. '
                    'Please add a description for this schema entry.'.format(
                        key=key,
                    )
                )
                healthy_schema = False
        if not healthy_schema:
            raise SchemaError(
                'Schema "{filename}" is not viable. Please correct logged '
                'errors.'.format(filename=schema_file)
            )

        self.schema.update(schema)
        self.check_config_is_valid()

    def check_config_is_valid(self):
        # Allow the existence of, but warn about, config keys that aren't in
        # the schema.
        # They will not be usable.
        for key in self.raw_config.keys():
            if key not in self.schema.keys():
                self.logger.warn(
                    '{key} is in config, but not defined in the schema. '
                    'This key will not be usable until correctly defined in '
                    'the schema.'.format(key=key)
                )
        # Currently, if we can load it then it's valid.
        return True

    def _generate_config(self):
        config = {
            k: v.get('default', NotSet)
            for k, v in self.schema.items()
        }
        for key, value in self.raw_config.items():
            if key in config.keys():
                config[key] = value
        return config

    def __getitem__(self, item):
        config = self._generate_config()
        if item in config.keys():
            return config[item]
        else:
            if item in self.raw_config.keys():
                raise KeyError(
                    'Config entry {key} was supplied but was not in the '
                    'schema. Please update the schema to use this config '
                    'entry.'.format(key=item)
                )
            else:
                raise KeyError(
                    'Config entry {key} was not supplied and is not in '
                    'schema.'.format(key=item)
                )

    def keys(self):
        return self._generate_config().keys()

    def values(self):
        return self._generate_config().values()

    def items(self):
        return self._generate_config().items()

default_schemas = [
    pkg_resources.resource_filename(
        'cloudify_tester',
        os.path.join('schemas', schema),
    )
    for schema in pkg_resources.resource_listdir('cloudify_tester', 'schemas')
]
atexit.register(pkg_resources.cleanup_resources)
