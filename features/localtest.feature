Feature: Local blueprint testing

  Scenario: Use Funkyhat's blueprint
    Given I can clone https://github.com/funkyhat/cloudify-system-tests.git to funkyhat with git and checkout pytest-poc
      And I create inputs file test.yaml with inputs
      """
        target_path: /tmp/ilikecake
        target_file_name: test.yaml
      """
    When I init a local env using funkyhat/suites/local/simple_blueprint/blueprint.yaml with inputs from test.yaml
     And I execute the local install workflow
    Then I see the file /tmp/ilikecake exists

