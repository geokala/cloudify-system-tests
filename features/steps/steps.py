# This is horrible, but we have to do it because behave doesn't support
# multiple step libraries even when it reads in multiple feature libraries.
# Thanks, behave.
with open('.step_modules') as module_handle:
    modules = module_handle.readlines()

modules = [module.rstrip() for module in modules]

for module in modules:
    exec('from {module}.steps import *'.format(module=module))
