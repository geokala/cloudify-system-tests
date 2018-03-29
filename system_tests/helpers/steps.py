import random
import string

from pytest_bdd import given, when, parsers

from cloudify_tester.steps.cfy import (
    render_named_blueprint_and_inputs,
    install_plugin_in_env,
    local_init_blueprint,
    local_install,
    use_manager,
    check_manager_is_healthy,
)
from cloudify_tester.steps.general import (
    download_file_on_host,
    run_command_on_host,
    scp_file,
)


MANAGER_CONFIG = """manager:
  private_ip: {int_ip}
  public_ip: {ext_ip}
  security:
    ssl_enabled: true
    admin_username: {admin_username}
    admin_password: {admin_password}"""


@given('I can use the specified system tests platform')
def platform_exists(tester_conf):
    """
        Allow failing fast if a missing platform is provided.
    """
    _check_platform(
        tester_conf['system_tests']['platform'],
        tester_conf['system_tests_platforms'],
    )


# TODO: Add versioned manager deploys, and support pre 4.0-<4.3
@when(parsers.parse(
    "I deploy a manager called {manager_name}"
))
def deploy_manager_on_platform(manager_name,
                               environment,
                               tester_conf):
    # TODO: Docstring
    platform = tester_conf['system_tests']['platform']
    platform_config = tester_conf['system_tests_platforms']

    _check_platform(platform, platform_config)

    # Generate the VM the manager will be installed on
    render_named_blueprint_and_inputs(
        '{platform}_manager_vm'.format(platform=platform),
        environment,
        tester_conf,
    )

    # Install the required platform plugin
    install_plugin_in_env(
        platform_config['{platform}_plugin'.format(platform=platform)],
        environment,
    )

    # Filthy hack to make cfy able to work with local openstack plugin
    base_path = 'lib/python2.7/site-packages/'
    bad_requirements = [
        base_path + 'cloudify_dsl_parser-4.3-py2.7.egg-info/requires.txt',
        base_path + 'cloudify-4.3-py2.7.egg-info/requires.txt',
    ]
    for path in bad_requirements:
        environment.executor(['sed', '-i', 's/PyYAML==3.10/PyYAML==3.12/',
                              path])
        environment.executor(['sed', '-i', 's/pyyaml==3.10/pyyaml==3.12/',
                              path])

    blueprint_name = '{platform}_manager_vm.yaml'.format(platform=platform)
    # Prepare the local blueprint for the manager VM and deploy it
    local_init_blueprint(
        blueprint=blueprint_name,
        inputs='{platform}_manager_vm_inputs.yaml'.format(platform=platform),
        environment=environment,
    )
    local_install(blueprint_name, environment)

    # Get the manager's IP
    node_instances = environment.cfy.node_instances(blueprint_name)
    external_ip_instances = [
        instance for instance in node_instances
        if instance['node_id'] == platform_config[
            '{platform}_ip_node_name'.format(platform=platform)]
    ]
    internal_ip_instances = [
        instance for instance in node_instances
        if instance['node_id'] == 'vm'
    ]
    # There should only be one node instance
    manager_external_props = external_ip_instances[0]['runtime_properties']
    manager_internal_props = internal_ip_instances[0]['runtime_properties']
    manager_external_ip = manager_external_props[platform_config[
        '{platform}_ip_runtime_property'.format(platform=platform)]]
    manager_internal_ip = manager_internal_props['ip']

    # Generate connection string
    manager_user = tester_conf['system_tests']['manager_ssh_user']
    conn_string = '{user}@{host}'.format(
        user=manager_user,
        host=manager_external_ip,
    )

    # Install manager (with SSL enabled)
    download_location = '/tmp/manager_install.rpm'
    download_file_on_host(
        url=tester_conf['system_tests']['manager_install_rpm_url'],
        user_at_host=conn_string,
        filepath=download_location,
        environment=environment,
        tester_conf=tester_conf,
    )
    admin_username = _get_random_string()
    admin_password = _get_random_string()
    cert_path = 'manager_{manager_name}.cert'.format(
        manager_name=manager_name,
    )
    manager_install_config = MANAGER_CONFIG.format(
        int_ip=manager_internal_ip,
        ext_ip=manager_external_ip,
        admin_username=admin_username,
        admin_password=admin_password,
    )
    for command in (
        'sudo yum install -y {loc}'.format(loc=download_location),
        'sudo echo "{conf}" | tee /etc/cloudify/config.yaml'.format(
            conf=manager_install_config,
        ),
        'sudo cfy_manager install',
    ):
        run_command_on_host(
            command=command,
            user_at_host=conn_string,
            environment=environment,
            tester_conf=tester_conf,
        )
    scp_file(
        source_path='/etc/cloudify/ssl/cloudify_external_cert.pem',
        user_at_host=conn_string,
        destination_path=cert_path,
        environment=environment,
        tester_conf=tester_conf,
    )

    # Register the manager in the environment
    if not hasattr(environment, 'managers'):
        environment.managers = {}
    environment.managers[manager_name] = {
        'ip': manager_external_ip,
        'username': admin_username,
        'password': admin_password,
        'certificate_path': cert_path,
    }

    # Make the local cfy profile use the manager
    use_manager(manager_name, environment)
    check_manager_is_healthy(environment)


def _get_random_string(length=20):
    return ''.join([
        random.choice(string.letters+string.digits)
        for i in range(length)
    ])


def _check_platform(platform, platform_config):
    assert '{platform}_plugin'.format(platform=platform) in platform_config, (
        'Platform {platform} was not available in the configuration. '
        'Available platforms: {available}'.format(
            platform=platform,
            available=', '.join([
                key[:-7] for key in platform_config.keys()
                if key.endswith('_plugin')
            ]),
        )
    )
