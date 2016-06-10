from behave import given, when, then

@given('that I have a cloudify config')
def have_cloudify_config(context):
    print(dir(context))
    assert hasattr(context, 'tester_conf')

@then('it has some values')
def tester_conf_has_values(context):
    print(context.tester_conf.keys())
