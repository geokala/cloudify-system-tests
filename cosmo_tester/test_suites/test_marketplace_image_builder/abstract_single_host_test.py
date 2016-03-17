########
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

import os

from fabric import api as fabric_api

from cloudify.workflows import local
from cloudify_cli import constants as cli_constants
from cosmo_tester.framework.git_helper import clone
from cosmo_tester.framework.util import create_rest_client

DEFAULT_MARKETPLACE_IMAGE_BUILDER_REPO_URL = 'https://github.com/' \
                                             'cloudify-cosmo/' \
                                             'cloudify-image-builder.git'
DEFAULT_PACKER_URL = 'https://releases.hashicorp.com/packer/' \
                     '0.10.0/packer_0.10.0_linux_amd64.zip'
DEFAULT_PACKER_FILE = 'cloudify.json'
DEFAULT_CLOUDIFY_VERSION = '3.3.1'
DEFAULT_AMI = "ami-91feb7fb"
SUPPORTED_ENVS = [
    'aws',
    'openstack',
]


class AbstractPackerTest(object):

    # TODO: Checker to make sure that no images with name prefix exist for
    #       envs based on the setting of self.only (aws or openstack for now)
    # TODO: cleanup for base_temp_dir
    # TODO: cleanup for image


    def _find_images(self):
        finders = {
            'aws': self._find_image_aws,
            'openstack': self._find_image_openstack,
        }
        for environment in self.images.keys():
            self.images[environment] = finders[environment]()

    def _get_conn_aws(self):
        return boto.ec2.EC2Connection(
            aws_access_key_id=self.env.aws_access_key,
            aws_secret_access_key=self.env.aws_secret_access_key,
        )

    def _find_image_aws(self):
        conn = self.get_conn_aws()

        image_id = None

        images = conn.get_all_images(owners='self')

        for image in images:
            if image.name.startswith(self.name_prefix):
                image_id = image.id
                break

        return image_id

    def _deploy_image_aws
        # TODO

    def _delete_image_aws(self, image_id):
        conn = self.get_conn_aws()
        image = conn.get_all_images(image_ids=[image_id])[0]
        image.deregister()

    def _get_conn_openstack
        return novaclient.Client(
            username=self.env.openstack_username,
            api_key=self.env.openstack_password,
            auth_url=self.env.openstack_identity_url,
            project_id=self.env.openstack_tenant_name,
            region=self.env.openstack_region,
        )

    def _find_image_openstack(self):
        conn = self._get_conn_openstack()

        image_id = None

        my_tenant_id = conn.client.tenant_id

        images = conn.images.list()
        images = [image.to_dict() for image in images]
        # Get just the images belonging to this tenant
        images = [
            image for image in images
            if 'owner_id' in image['metadata'].keys()
            and image['metadata']['owner_id'] == my_tenant_id
        ]
        # Filter for the prefix
        for image in images:
            if image['name'].startswith(self.name_prefix):
                image_id = image['id']
                break

        return image['id']

    def _deploy_image_openstack
        # TODO

    def _delete_image_openstack(self, image_id):
        conn = self._get_conn_openstack()
        image = conn.images.find(id=image_id)
        image.delete()

    def _get_packer(self, destination)
        wget_command = [
            'wget',
            self.env.packer_url or DEFAULT_PACKER_URL,
        ]
        wget_status = subprocess.call(
            wget_command,
            cwd=destination,
        )
        assert wget_status == 0

        unzip_command = [
            'unzip',
            os.path.split(self.env.packer_url)[1],
        ]
        unzip_status = subprocess.call(
            unzip_command,
            cwd=destination,
        )
        assert unzip_status == 0

        return os.path.join(destination, 'packer')

    def _get_marketplace_image_builder_repo(self):
        self.base_temp_dir = tempfile.mkdtemp()

        git.clone(
            url=self.env.image_builder_url \
                or DEFAULT_MARKETPLACE_IMAGE_BUILDER_REPO_URL,
            basedir = self.base_temp_dir,
        )

        self.addCleanup(self.clean_tempdir)

        actual_marketplace_path = os.path.join(
            
        )

    def _build_inputs(self, destination_path, name_prefix):
        inputs = {
            "name_prefix": name_prefix,
            "cloudify_version": self.env.marketplace_cloudify_version \
                                or DEFAULT_CLOUDIFY_VERSION,
            "aws_access_key": self.env.aws_access_key,
            "aws_secret_key": self.env.aws_secret_key,
            "aws_source_ami": self.env.marketplace_source_ami \
                              or DEFAULT_AMI,
            "openstack_ssh_keypair_name": self.env.openstack_ssh_keypair,
            "openstack_availability_zone": (
                self.env.openstack_marketplace_availability_zone
            ),
            "openstack_image_flavor": self.env.marketplace_openstack_flavor,
            "openstack_identity_endpoint": self.env.openstack_identity_url,
            "openstack_source_image_id": (
                self.env.marketplace_openstack_source_image
            ),
            "openstack_username": self.env.openstack_username,
            "openstack_password": self.env.openstack_password,
            "openstack_tenant_name": self.env.openstack_tenant_name,
            "openstack_floating_ip_pool_name": (
                self.env.openstack_floating_ip_pool_name
            ),
            "openstack_network": self.env.openstack_network,
            "openstack_security_group": self.env.openstack_security_group,
        }
        inputs = json.dumps(inputs)
        with open(destination_path) as inputs_handle:
            inputs_handle.write(inputs)

    def build_with_packer(self, name_prefix='system-tests', only=None):
        self.name_prefix = name_prefix
        if only is None:
            self.images = {environment: None for environment in SUPPORTED_ENVS}
        else:
            self.images = {only: None}

        _check_for_images(should_exist=False)

        image_builder_repo_path = self._get_marketplace_image_builder_repo()

        marketplace_path = os.path.join(
            image_builder_repo_path,
            'cloudify_marketplace',
        )

        packer_bin = self._get_packer(marketplace_path)

        inputs_file_name = 'system-test-inputs.json'
        self._build_inputs(
            destination_path=os.path.join(
                marketplace_path,
                inputs_file_name
            ),
            name_prefix=name_prefix,
        )

        self.only = only

        # Build the packer command
        command = [
            packer_bin,
            '--var-file={inputs}'.format(inputs=inputs_file_name),
        ]
        if self.env.only is not None:
            command.append('--only={only}'.format(only=only))
        command.append(self.env.packer_file or DEFAULT_PACKER_FILE)

        # Run packer
        build_status = subprocess.call(
            command
            cwd=marketplace_path,
        )
        assert build_status == 0

        _check_for_images()

        self.add_cleanup(self.delete_images)

    def _check_for_images(self, should_exist=True):
        _find_images()
        for env, image in self.images.items():
            if should_exist:
                fail = 'Image for {env} not found!'.format(env=env)
                assert image is not None, fail
            else:
                fail = 'Image for {env} already exists!'.format(env=env)
                assert image is None, fail
