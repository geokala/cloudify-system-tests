Feature: Testing nodecellar on an openstack manager

  Background: Get a manager with nodecellar
    Given I can clone https://github.com/cloudify-cosmo/cloudify-manager-blueprints.git to manager-blueprints with git and checkout 3.3.1
      And I can clone https://github.com/cloudify-cosmo/cloudify-nodecellar-example.git to nodecellar-blueprints with git and checkout 3.3.1
      And I create inputs file bootstrap.yaml with inputs
      """
        keystone_username: '{openstack_username}'
        keystone_password: '{openstack_password}'
        keystone_tenant_name: '{openstack_tenant}'
        keystone_url: '{openstack_url}'
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
      And I create inputs file nodecellar.yaml with inputs
      """
        image: '{openstack_ubuntu_14_04_image_id}'
        flavor: '{openstack_large_flavor_id}'
        agent_user: '{openstack_ubuntu_agents_user}'
      """
      When I init the cloudify environment
       And I bootstrap using manager-blueprints/openstack-manager-blueprint.yaml with inputs from bootstrap.yaml
       And I allow access to influxdb on the manager security group specified in bootstrap.yaml
       And I upload the blueprint nodecellar-blueprints/openstack-nova-net-blueprint.yaml as nodecellar
       And I create a deployment called nodecellar from the blueprint nodecellar with inputs from nodecellar.yaml
       And I execute the install workflow on the nodecellar deployment
      # TODO: No, put the cleanups into the steps where the thing to be cleaned up is created
      Then after I finish I will uninstall nodecellar
       And after I finish I will delete the nodecellar deployment
       And after I finish I will teardown the manager

  Scenario: Check nodecellar is up
   Given I can get a URL from the nodecellar deployment
    When I try to access the nodecellar URL
    Then I find the nodecellar page contained the word nodecellar

  Scenario: Check nodecellar has monitoring data on the manager
   Given I can access monitoring data on the manager
    When I try to get monitoring data for the nodecellar deployment
    Then I see some monitoring data
