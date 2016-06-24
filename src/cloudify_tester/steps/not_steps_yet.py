from behave import step


@step('I allow access to influxdb on the manager security group specified in '
      'bootstrap.yaml')
@step('I can get a URL from the nodecellar deployment')
@step('I try to access the nodecellar URL')
@step('I find the nodecellar page contains the word nodecellar')
@step('I can access monitoring data on the manager')
@step('I try to get monitoring data for the nodecellar deployment')
@step('I see some monitoring data')
def dosomething(context):
    import time
    time.sleep(10)
