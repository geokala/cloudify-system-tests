from cloudify_tester import cleanups

from behave import then, step

import os


@then('I see the file {path} exists')
def file_exists_on_local_system(context, path):
    assert os.path.exists(path)


@then('after I finish I will remove {filename} and its '
      'parent directory {path}')
def clean_up_funkyhat_test(context, filename, path):
    context._env.add_cleanup(
        function=cleanups.clean_up_the_cake,
        kwargs={'filename': filename, 'path': path},
    )

@then('I like cake')
def do_thing(context):
    context._env.blueprints.append('cake')
    print(context._env.blueprints)
    print(context._env.cloudify_bootstrap_completed)
    context._env.cloudify_bootstrap_completed = True
    print(context._env.cloudify_bootstrap_completed)

@then('I like biscuits')
def do_other(context):
    context._env.blueprints.append('biscuits')
    print(context._env.blueprints)
    print(context._env.cloudify_bootstrap_completed)
    assert False

@step('I fail a step')
def fail_step(context):
    assert False
