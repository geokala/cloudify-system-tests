from cloudify_tester import config as cloudify_tester_config
from cloudify_tester.helpers.env import TestEnvironment
from cloudify_tester.helpers.logger import TestLogger

from behave.log_capture import capture

import time


behave_env_logger = TestLogger(
    log_path=None,
    logger_name='config_logger',
    log_format='%(message)s',
)
behave_env_logger.console_logging_set_level('debug')


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
        logger=behave_env_logger,
    )

    context.tester_conf = tester_conf


@capture
def before_feature(context, feature):
    # Make a somewhat helpful prefix for the tempdir
    feature_name = context.feature.name
    feature_name = ''.join([
        char if char.isalnum() else '_' for char in feature_name
    ][:10])
    workdir_prefix = '{prefix}_{feature}_{time}_'.format(
        prefix='cloudify_tester',
        feature=feature_name,
        time=time.strftime('%d%b%H.%M'),
    )

    context._env = TestEnvironment()

    context._env.start(
        logging_level=context.tester_conf['logging']['level'],
        log_to_console=context.tester_conf['logging']['to_console'],
        workdir_prefix=workdir_prefix,
    )


@capture
def after_feature(context, feature):
    behave_env_logger.info('Executing cleanup functions')
    behave_env_logger.info(
        'Output will be absent if logging.to_console is false'
    )
    if context.failed:
        cleanup = context.tester_conf['cleanup']['on_failure']
        remove_workdir = (
            context.tester_conf['cleanup']['remove_workdir_on_failure']
        )
    else:
        cleanup = context.tester_conf['cleanup']['on_success']
        remove_workdir = (
            context.tester_conf['cleanup']['remove_workdir_on_success']
        )
    context._env.teardown(run_cleanup=cleanup, remove_workdir=remove_workdir)
    if not remove_workdir:
        behave_env_logger.info('Workdir remains in {location}'.format(
            location=context._env.workdir,
        ))
