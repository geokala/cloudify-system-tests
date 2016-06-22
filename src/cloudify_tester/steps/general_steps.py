from behave import then

import os

@then('I see the file {path} exists')
def file_exists_on_local_system(context, path):
    assert os.path.exists(path)
