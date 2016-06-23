# TODO: Actually make a logger
import logging

from behave.log_capture import capture
from cloudify_tester import config as cloudify_tester_config
from cloudify_tester.helpers.env import TestEnvironment


# Use the capture decorator to ensure we output warnings logged loading config
@capture
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

    context.env = TestEnvironment()
    cli_version = tester_conf['cli_version']
    context.env.start(cloudify_version=cli_version)

@capture
def after_all(context):
    if context.failed:
        if context.tester_conf['cleanup_on_failure']:
            cleanup = True
        else:
            cleanup = False
    else:
        cleanup = context.tester_conf['cleanup_on_success']
    context.env.teardown(run_cleanup=cleanup)
