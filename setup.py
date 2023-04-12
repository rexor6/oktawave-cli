# coding: utf-8

"""
    Oktawave CLI
"""


from setuptools import setup, find_packages  # noqa: H301

NAME = "oktawave-cli"
VERSION = "0.0.1"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "certifi>=2022.12.07",
    "python-dateutil>=2.1",
    "six>=1.10",
    "urllib3>=1.23",
    "pyodk @ git+https://github.com/rexor6/pyodk.git",
    "click==7.1.2",
    "click-completion==0.5.2",
    "python-swiftclient>=3.12.0",
    "python-keystoneclient>=4.3.0",
    "progressbar2",
    "configparser",
    "requests",
    "typer"
]

setup(
    name=NAME,
    version=VERSION,
    description="Oktawave CLI client",
    author_email="marcin.jedrzejczyk@oktawave.com",
    url="",
    keywords=["Oktawave", "CLI", "Oktawave CLI Client"],
    install_requires=REQUIRES,
    entry_points={
        'console_scripts': [
            'oktawave-cli = oktawave_cli.oktawave_cli:cli',
        ],
    },
    packages=find_packages(),
    include_package_data=True,
    py_modules=["oktawave_cli.auth"],
    long_description="""
      CLI client for managing services in Oktawave Cloud
    """
)
