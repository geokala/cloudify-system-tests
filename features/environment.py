from behave.log_capture import capture

from cloudify_tester import config as cloudify_tester_config
from cloudify_tester.helpers.env import TestEnvironment
from cloudify_tester.helpers.logger import TestLogger


# Use the capture decorator to ensure we output warnings logged loading config
@capture
def before_all(context):
    conf_logger = TestLogger(
        log_path=None,
        logger_name='config_logger',
    )
    conf_logger.console_logging_set_level('debug')

    conf_file_path = context.config.userdata.get('config', 'test_config.yaml')
    schema_paths = context.config.userdata.get('schemas', None)

    schemas = cloudify_tester_config.default_schemas
    if schema_paths is not None:
        schemas.extend(schema_paths.split(','))

    tester_conf = cloudify_tester_config.Config(
        config_files=[conf_file_path],
        config_schema_files=schemas,
        logger=conf_logger,
    )

    context.tester_conf = tester_conf


@capture
def before_feature(context, feature):
    context._env = TestEnvironment()
    cli_version = context.tester_conf['cli_version']
    context._env.start(
        cloudify_version=cli_version,
        logging_level=context.tester_conf['logging_level'],
        log_to_console=context.tester_conf['log_to_console'],
    )


@capture
def after_feature(context, feature):
    print('Executing cleanup functions')
    print('Output will be absent if log_to_console is false')
    if context.failed:
        cleanup = context.tester_conf['cleanup_on_failure']
        remove_workdir = context.tester_conf['remove_workdir_on_failure']
    else:
        cleanup = context.tester_conf['cleanup_on_success']
        remove_workdir = context.tester_conf['remove_workdir_on_success']
    context._env.teardown(run_cleanup=cleanup, remove_workdir=remove_workdir)
