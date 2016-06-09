# TODO: Actually make a logger
import logging

from cloudify_tester import config as cloudify_tester_config


def before_all(context):
    conf_file_path = context.config.userdata.get('config', 'test_config.yaml')
    schema_paths = context.config.userdata.get('schemas', None)

    schemas = cloudify_tester_config.default_schemas
    if schema_paths is not None:
        schemas.extend(schema_paths.split(','))

    tester_conf = cloudify_tester_config.Config(
        config_files=[conf_file_path],
        config_schema_files=schemas,
        logger=logging,
    )

    context.tester_conf = tester_conf
