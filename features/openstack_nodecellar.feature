Feature: Testing nodecellar on an openstack manager
  @openstack 
  Scenario: Check nodecellar is up
    Given I have a manager created from openstack-manager-blueprint.yaml from a checkout of 3.3.1-openstack-dns on https://github.com/geokala/cloudify-manager-blueprints.git with inputs
      """
        keystone_username: '{openstack_username}'
        keystone_password: '{openstack_password}'
        keystone_tenant_name: '{openstack_tenant}'
        keystone_url: '{openstack_keystone_url}'
        region: '{openstack_region}'
        manager_public_key_name: '{resources_prefix}-manager-key'
        agent_public_key_name: '{resources_prefix}-agent-key'
        image_id: '{openstack_centos_7_image_id}'
        flavor_id: '{openstack_large_flavor_id}'
        external_network_name: '{openstack_external_network}'
        management_network_name: '{resources_prefix}-management-network'
        management_subnet_name: '{resources_prefix}-management-network-subnet'
        management_router: '{resources_prefix}-management-router'
        manager_security_group_name: '{resources_prefix}-manager-sg'
        agents_security_group_name: '{resources_prefix}-agents-sg'
        manager_port_name: '{resources_prefix}-manager-port'
        agents_user: '{openstack_centos_agents_user}'
      """
      And I have a deployment called nodecellar from openstack-nova-net-blueprint.yaml from a checkout of 3.3.1 on https://github.com/cloudify-cosmo/cloudify-nodecellar-example.git with inputs
      """
        image: '{openstack_ubuntu_14_04_image_id}'
        flavor: '{openstack_large_flavor_id}'
        agent_user: '{openstack_ubuntu_agents_user}'
      """
    When I try to access the nodecellar URL
    Then I find the nodecellar page contains the word nodecellar

  @openstack
  Scenario: Check nodecellar has monitoring data on the manager
    # TODO: This should probably be drawing from configuration settings, and the inputs template should probably be in the settings as well
    Given I have a manager created from openstack-manager-blueprint.yaml from a checkout of 3.3.1-openstack-dns on https://github.com/geokala/cloudify-manager-blueprints.git with inputs
      """
        keystone_username: '{openstack_username}'
        keystone_password: '{openstack_password}'
        keystone_tenant_name: '{openstack_tenant}'
        keystone_url: '{openstack_keystone_url}'
        region: '{openstack_region}'
        manager_public_key_name: '{resources_prefix}-manager-key'
        agent_public_key_name: '{resources_prefix}-agent-key'
        image_id: '{openstack_centos_7_image_id}'
        flavor_id: '{openstack_large_flavor_id}'
        external_network_name: '{openstack_external_network}'
        management_network_name: '{resources_prefix}-management-network'
        management_subnet_name: '{resources_prefix}-management-network-subnet'
        management_router: '{resources_prefix}-management-router'
        manager_security_group_name: '{resources_prefix}-manager-sg'
        agents_security_group_name: '{resources_prefix}-agents-sg'
        manager_port_name: '{resources_prefix}-manager-port'
        agents_user: '{openstack_centos_agents_user}'
      """
      And I have a deployment called nodecellar from openstack-nova-net-blueprint.yaml from a checkout of 3.3.1 on https://github.com/cloudify-cosmo/cloudify-nodecellar-example.git with inputs
      """
        image: '{openstack_ubuntu_14_04_image_id}'
        flavor: '{openstack_large_flavor_id}'
        agent_user: '{openstack_ubuntu_agents_user}'
      """
    When I try to get monitoring data for the nodecellar deployment
    Then I see some monitoring data
