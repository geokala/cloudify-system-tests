from cloudify_tester import cleanups

from behave import then

import os

@then('I see the file {path} exists')
def file_exists_on_local_system(context, path):
    assert os.path.exists(path)


@then('after I finish I will remove {filename} and its '
      'parent directory {path}')
def clean_up_funkyhat_test(context, filename, path):
     context.env.add_cleanup(
         function=cleanups.clean_up_the_cake,
         kwargs={'filename':filename, 'path':path},
     )
