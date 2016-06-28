from cloudify_tester.steps.git_steps import git_clone_and_checkout

from behave import step, given
import yaml

import os


@step('I create inputs file {inputs_file} from template {template_name}')
def cfy_create_inputs(context, inputs_file, template_name):
    template_path = os.path.join('templates', template_name)
    with open(template_path) as template_handle:
        inputs = template_handle.read().format(**context.tester_conf)

    inputs = yaml.load(inputs)

    context._env.cfy.create_inputs(inputs_dict=inputs,
                                   inputs_name=inputs_file)


@step('I init a local env using {blueprint} with inputs from {inputs_path}')
def cfy_local_init(context, blueprint, inputs_path):
    context._env.cfy.local.init(
        blueprint_path=blueprint,
        inputs_path=inputs_path,
        install_plugins=True,
    )


@step('I execute the local {workflow} workflow')
def cfy_local_exec(context, workflow):
    context._env.cfy.local.execute(workflow=workflow)


@step('I init the cloudify environment')
def cfy_init(context):
    context._env.cfy.init()


@given('I have a manager created from {blueprint} from a checkout of '
       '{checkout} on {git_repo} with inputs from template {template_name}')
def cfy_bootstrap_once(context, blueprint, checkout, git_repo, template_name):
    if context._env.manager_bootstrap_completed:
        print('I did this earlier!')
        return

    git_clone_and_checkout(
        context,
        repo=git_repo,
        destination='manager_blueprints',
        checkout=checkout,
    )
    cfy_create_inputs(
        context,
        inputs_file='bootstrap.yaml',
        template_name=template_name,
    )
    context._env.cfy.init()
    context._env.cfy.bootstrap(
        blueprint_path=os.path.join('manager_blueprints', blueprint),
        inputs_path='bootstrap.yaml',
        install_plugins=True,
    )
    context._env.manager_bootstrap_completed = True
    context._env.add_cleanup(
        context._env.cfy.teardown,
    )


@step('I have uploaded the blueprint {blueprint_path} as {blueprint_id}')
def cfy_blueprints_upload(context, blueprint_path, blueprint_id,
                          warn_if_existing=False):
    if blueprint_id in context._env.blueprints and not warn_if_existing:
        return
    context._env.cfy.blueprints.upload(
        blueprint_path=blueprint_path,
        blueprint_id=blueprint_id,
    )
    context._env.blueprints.append(blueprint_id)
    context._env.add_cleanup(
        context._env.cfy.blueprints.delete,
        kwargs={
            'blueprint_id': blueprint_id,
        },
    )


@step('I have created a deployment called {deployment_id} from the blueprint '
      '{blueprint_id} with inputs from {inputs_path}')
def cfy_deployments_create(context, deployment_id, blueprint_id, inputs_path,
                           warn_if_existing=False):
    if deployment_id in context._env.deployments and not warn_if_existing:
        return
    context._env.cfy.deployments.create(
        blueprint_id=blueprint_id,
        deployment_id=deployment_id,
        inputs_path=inputs_path,
    )
    context._env.deployments.append(deployment_id)
    context._env.add_cleanup(
        context._env.cfy.deployments.delete,
        kwargs={
            'deployment_id': deployment_id,
        },
    )


@step('I execute the {workflow} workflow on the {deployment_id} deployment')
def cfy_executions_start(context, workflow, deployment_id):
    context._env.cfy.executions.start(
        workflow=workflow,
        deployment_id=deployment_id,
        timeout=1800,
    )
    if workflow == 'install':
        context._env.add_cleanup(
            context._env.cfy.executions.start,
            kwargs={
                'workflow': 'uninstall',
                'deployment_id': deployment_id,
                'timeout': 1800,
            },
        )


@given('I have a deployment called {deployment_name} from {blueprint} from a '
       'checkout of {checkout} on {git_repo} with inputs from template '
       '{template_name}')
def cfy_upload_create_and_deploy_once(context, deployment_name, blueprint,
                                      checkout, git_repo, template_name):
    if deployment_name in context._env.blueprints:
        # We've already done this
        # TODO: Fix git cloning and then stop using this
        return
    blueprints_path = '{deployment}_blueprints'.format(
        deployment=deployment_name,
    )
    git_clone_and_checkout(
        context,
        repo=git_repo,
        destination=blueprints_path,
        checkout=checkout,
    )
    inputs_file_name = '{deployment}.yaml'.format(
        deployment=deployment_name,
    )
    cfy_create_inputs(
        context,
        inputs_file='nodecellar.yaml',
        template_name=template_name,
    )
    # TODO: This can probably be done using the cfy install(?) command
    cfy_blueprints_upload(
        context,
        blueprint_path=os.path.join(blueprints_path, blueprint),
        blueprint_id=deployment_name,
    )
    cfy_deployments_create(
        context,
        deployment_id=deployment_name,
        blueprint_id=deployment_name,
        inputs_path=inputs_file_name,
    )
    cfy_executions_start(
        context,
        workflow='install',
        deployment_id=deployment_name,
    )
