from pytest_bdd import when, parsers

from cloudify_tester.steps.cfy import (
    render_named_blueprint_and_inputs,
    install_plugin_in_env,
    local_init_blueprint,
    local_install,
    use_manager,
    check_manager_is_healthy,
)


# TODO: Add versioned manager deploys, and support pre 4.0-<4.3
@when(parsers.parse(
    "I deploy a manager on {platform}"
))
def deploy_manager_on_platform(environment, tester_conf, platform):
    # TODO: Docstring
    platform_config = tester_conf['system_tests_platforms']

    assert '{platform}_plugin'.format(platform=platform) in platform_config, (
        'Platform {platform} was not available in the configuration. '
        'Available platforms: {available}'.format(
            platform=platform,
            available=', '.join([
                key for key in platform_config.keys()
                if key.endswith('_plugin')
            ]),
        )
    )

    # Generate the VM the manager will be installed on
    #render_named_blueprint_and_inputs(
    #    '{platform}_manager_vm'.format(platform=platform),
    #    environment,
    #    tester_conf,
    #)

    # Install the required platform plugin
    install_plugin_in_env(
        platform_config['{platform}_plugin'.format(platform=platform)],
        environment,
    )

    # Prepare the local blueprint for the manager VM and deploy it
    #local_init_blueprint(
    #    blueprint='{platform}_manager_vm.yaml'.format(platform=platform),
    #    inputs='{platform}_manager_vm_inputs.yaml'.format(platform=platform),
    #    environment=environment,
    #)
    #local_install(environment)

    # TODO: Install manager (with SSL enabled)

    environment.managers = {'fake1': []}
    # Make the local cfy profile use the manager
    use_manager('wrong_manager_name', environment)
    check_manager_is_healthy(environment)
