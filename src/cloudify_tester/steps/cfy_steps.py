from behave import given, when, then
import yaml

@given('I create inputs file {inputs_file} with inputs')
def cfy_create_inputs(context, inputs_file):
    inputs = yaml.load(context.text)

    context.env.cfy.create_inputs(inputs_dict=inputs,
                                  inputs_name=inputs_file)

@when('I init a local env using {blueprint} with inputs from {inputs_path}')
def cfy_local_init(context, blueprint, inputs_path):
    context.env.cfy.local_init(
        blueprint_path=blueprint,
        inputs_path=inputs_path,
        install_plugins=True,
    )

@when('I execute the local {workflow} workflow')
def cfy_local_exec(context, workflow):
    context.env.cfy.local_execute(workflow=workflow)
