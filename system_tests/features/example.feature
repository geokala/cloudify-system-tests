Feature: Example deployment on manager
  @manager
  Scenario: Installing manager
    Given I can use the specified system tests platform
    When I have installed cfy
    And I deploy a manager called test_manager

#  @manager @openstack @manager_deployment @install
#  Scenario: Create example deployment
#    Given no tests have failed in this feature
#     When I have example blueprint and inputs from templates
#      And I upload blueprint example.yaml as example
#      And I create deployment example from blueprint example
#      And I install deployment example
#     Then on the manager I find file /tmp/example containing text: example_string

#  @manager @openstack @manager_deployment @uninstall
#  Scenario: Remove example deployment
#    Given no tests have failed in this feature
#     When I uninstall deployment example
#     Then on the manager I do not find file /tmp/example
