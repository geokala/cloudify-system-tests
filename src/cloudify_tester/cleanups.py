import os


def clean_up_the_cake(path, filename):
    if filename == 'test.yaml' and path == '/tmp/ilikecake':
        os.unlink(os.path.join(path, filename))
        os.rmdir(path)
