import os
import subprocess

pytest_plugins = (
    'cloudify_tester.steps',
    'cloudify_tester.fixtures',
    #'helpers.steps',
)

def pytest_configure(config):
    base_path = os.path.split(__file__)[0]

    feature_files_path = os.path.join(
        base_path,
        'features',
    )

    generated_features_path = os.path.join(
        base_path,
        'generated_features',
    )
    init_path = os.path.join(
        generated_features_path,
        '__init__.py',
    )

    subprocess.check_call(['rm', '-rf', generated_features_path])
    os.mkdir(generated_features_path)
    with open(init_path, 'w') as init_handle:
        init_handle.write('')

    feature_number = 0
    for feature_file in os.listdir(feature_files_path):
        feature_module_name = 'test_{}'.format(feature_number)
        feature_module_py = '{}.py'.format(feature_module_name)
        generated_feature_path = os.path.join(
            generated_features_path,
            feature_module_py,
        )

        feature = """from pytest_bdd import scenarios

scenarios('{}')""".format(os.path.join(feature_files_path, feature_file))

        with open(generated_feature_path, 'w') as feature_handle:
            feature_handle.write(feature)

        feature_number += 1

    config.args.append(generated_features_path)
