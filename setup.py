from setuptools import setup, find_packages

setup(
    name="cloudify_tester",
    version="0.1.0",
    package_dir={'': 'src'},
    packages=find_packages('src'),
    package_data={'cloudify_tester': [
        'schemas/*.yaml',
    ]},
    install_requires=[
        'behave==1.2.5',
        'PyYAML==3.11',
        'click==6.6',
    ],
    entry_points={
        'console_scripts': [
            'show_config_schema = '
            'cloudify_tester.config_display:show_config_schema',
            'get_plugin_tests = '
            'cloudify_tester.get_plugin_tests:get_plugin_tests',
        ],
    },
)
