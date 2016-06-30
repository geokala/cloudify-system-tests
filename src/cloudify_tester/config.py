import yaml

import os


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

    def _nest_dotted_key(self, root_dict, key_path, value):
        this_key = key_path.pop(0)

        if len(key_path) == 0:
            root_dict[this_key] = value
        else:
            if this_key not in root_dict.keys():
                root_dict[this_key] = {}
            self._nest_dotted_key(
                root_dict[this_key],
                key_path=key_path,
                value=value,
            )

    def update_config(self, config_file):
        with open(config_file) as config_handle:
            raw_config = yaml.load(config_handle.read())
        processed_config = {}
        for key in raw_config.keys():
            key_path = key.split('.')
            self._nest_dotted_key(
                processed_config,
                key_path,
                raw_config.pop(key),
            )
        self.raw_config.update(processed_config)
        self.check_config_is_valid()

    def update_schema(self, schema_file):
        with open(schema_file) as schema_handle:
            schema = yaml.load(schema_handle.read())

        namespace = None
        if 'namespace' in schema.keys():
            namespace = schema['namespace']
            if namespace in self.schema.keys():
                if not self.schema[namespace]['.is_namespace']:
                    raise SchemaError(
                        'Attempted to define namespace {namespace} but this '
                        'is already a configuration entry!'.format(
                            namespace=namespace,
                        )
                    )
            else:
                self.schema[namespace] = {'.is_namespace': True}
            schema.pop('namespace')

        # Make sure the schema is entirely valid- every entry must have a
        # description
        healthy_schema = True
        for key, value in schema.items():
            display_key = key
            if namespace is not None:
                display_key = '.'.join([namespace, key])
            if '.' in key:
                self.logger.error(
                    '{key} is not a valid name for a configuration entry. '
                    'Keys must not contain dots as this will interfere with '
                    'processing in input substituation.'.format(
                        key=display_key,
                    )
                )
                healthy_schema = False
            if 'description' not in value.keys():
                self.logger.error(
                    '{key} in schema does not have description. '
                    'Please add a description for this schema entry.'.format(
                        key=display_key,
                    )
                )
                healthy_schema = False
        if not healthy_schema:
            raise SchemaError(
                'Schema "{filename}" is not viable. Please correct logged '
                'errors.'.format(filename=schema_file)
            )

        if namespace is None:
            self.schema.update(schema)
        else:
            self.schema[namespace].update(schema)
        self.check_config_is_valid()

    def check_config_is_valid(self, namespace=None):
        # Allow the existence of, but warn about, config keys that aren't in
        # the schema.
        # They will not be usable.
        if namespace is None:
            schema = self.schema
            config = self.raw_config
        else:
            schema = self.schema[namespace]
            config = self.raw_config.get(namespace, {})
        for key in config.keys():
            if namespace is None:
                display_key = key
            else:
                display_key = '.'.join([namespace, key])
            if key not in schema.keys():
                self.logger.warn(
                    '{key} is in config, but not defined in the schema. '
                    'This key will not be usable until correctly defined in '
                    'the schema.'.format(key=display_key)
                )
            if key in schema.keys() and schema[key].get('.is_namespace',
                                                        False):
                self.check_config_is_valid(namespace=key)
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
        if '.' in item:
            raise KeyError(
                'Config entry {key} is invalid. Config entries may not be '
                'retrieved using dotted notation. Please use nested dicts '
                'instead.'.format(key=item)
            )
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


def find_default_schemas():
    schemas = []

    candidate_paths = ['./schemas']
    candidate_paths.extend([
        os.path.join(path, 'system_tests', 'schemas')
        for path in os.listdir('.')
        if os.path.isdir(path)
    ])
    for path in candidate_paths:
        if os.path.isdir(path):
            for schema in os.listdir(path):
                if schema.endswith('.yaml'):
                    schemas.append(os.path.join(path, schema))

    return schemas

default_schemas = find_default_schemas()
