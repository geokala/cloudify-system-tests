from behave import given


@given('I can clone {repo} to {destination} with git and checkout {checkout}')
def git_clone_and_checkout(context, repo, destination, checkout):
    context._env.git.clone(repo, clone_to=destination)
    context._env.git.checkout(destination, checkout)
