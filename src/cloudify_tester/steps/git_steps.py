from behave import given, when, then

@given('I can clone {repo} to {destination} with git and checkout {checkout}')
def git_clone_and_checkout(context, repo, destination, checkout):
    context.env.git.clone(repo, clone_to=destination)
    context.env.git.checkout(destination, checkout)
