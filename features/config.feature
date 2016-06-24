Feature: Config testing
  @test_framework
  Scenario: Config is in context
    Given that I have a cloudify config
     Then it has some values
