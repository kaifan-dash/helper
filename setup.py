from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name = 'helper', 
    description = 'Simplifies data handling proceedures', 
    version = '0.0.1', 
    package_dir = {'': 'src/'}, 
    packages = ['helper'], 
    author = 'Kai', 
    author_email = 'kaifan@dashmote.com', 
    include_package_data = True, 
    install_requires = required
)