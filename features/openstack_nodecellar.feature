Feature: Testing nodecellar on an openstack manager
  @openstack 
  Scenario: Check nodecellar is up
    Given I have a manager created from openstack-manager-blueprint.yaml from a checkout of 3.3.1-openstack-dns on https://github.com/geokala/cloudify-manager-blueprints.git with inputs from template openstack-bootstrap-inputs
      And I have a deployment called nodecellar from openstack-nova-net-blueprint.yaml from a checkout of 3.3.1 on https://github.com/cloudify-cosmo/cloudify-nodecellar-example.git with inputs from template openstack-nodecellar-inputs
    When I try to access the nodecellar URL
    Then I find the nodecellar page contains the word nodecellar

  @openstack
  Scenario: I run all of the tests even if one of them fails
    Given I have a manager created from openstack-manager-blueprint.yaml from a checkout of 3.3.1-openstack-dns on https://github.com/geokala/cloudify-manager-blueprints.git with inputs from template openstack-bootstrap-inputs
      And I have a deployment called nodecellar from openstack-nova-net-blueprint.yaml from a checkout of 3.3.1 on https://github.com/cloudify-cosmo/cloudify-nodecellar-example.git with inputs from template openstack-nodecellar-inputs
     Then I fail a step

  @openstack
  Scenario: Check nodecellar has monitoring data on the manager
    Given I have a manager created from openstack-manager-blueprint.yaml from a checkout of 3.3.1-openstack-dns on https://github.com/geokala/cloudify-manager-blueprints.git with inputs from template openstack-bootstrap-inputs
      And I have a deployment called nodecellar from openstack-nova-net-blueprint.yaml from a checkout of 3.3.1 on https://github.com/cloudify-cosmo/cloudify-nodecellar-example.git with inputs from template openstack-nodecellar-inputs
    When I try to get monitoring data for the nodecellar deployment
    Then I see some monitoring data
