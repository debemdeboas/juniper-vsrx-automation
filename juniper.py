from collections import namedtuple
from pprint import pprint
from typing import Tuple
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from getpass import getpass
import yaml
import argparse


# -----------------
# Constants

# Login information
DEFAULT_USERNAME = 'jcluser'
DEFAULT_PASSWORD = 'Juniper!1'

# Basic set-format file with 'set' commands
SET_FILE = 'template/basic.set.j2'
SET_VARS_FILE = 'data/basic_set_datavars.yml'

# Example conf-format template to be applied
CONFIG_FILE = 'template/juniper.conf.j2'
CONFIG_VARS_FILE = 'data/juniper_conf_datavars.yml'


# -----------------
# Custom types

# Use a named tuple to create a more readable code later on
ConfigurationFile = namedtuple('ConfigurationFile', 'file vars format')

# Unpack the configuration file dictionaries to make the tuple creation more explicit
configuration_files = [
    ConfigurationFile(
        **{'file': SET_FILE, 'vars': SET_VARS_FILE, 'format': 'set'}),
    ConfigurationFile(
        **{'file': CONFIG_FILE, 'vars': CONFIG_VARS_FILE, 'format': 'text'}),
]


# -----------------
# Methods

def prompt_check_commit(config: Config) -> None:
    """Prints a diff of the changes (if any) and prompts the user for committing them

    Args:
        config (Config): Configuration object used to commit or rollback the changes
    """

    config.pdiff()
    if input('Would you like to commit these changes? [y/N]: ').lower() == 'y':
        config.commit()
        print('Commit success')
    else:
        print('Skipping')
        config.rollback(0)


def prompt_hostname() -> Tuple[str, str]:
    """Prompts the user for the device hostname and port

    Returns:
        Tuple[str, str]: Tuple of (hostname,port)
    """

    try:
        hostname, port = input(
            'Device hostname (in the IP:Port format): ').split(':')
    except Exception as E:
        print(E)
        exit(1)
    return hostname, port


def prompt_login_information() -> Tuple[str, str]:
    """Prompts the user for the device login information

    This function is only called when the `--default_login` argument is not passed on the CLI

    Returns:
        Tuple[str, str]: Tuple of (username,password)
    """

    try:
        username = input('Console server username: ')
        password = getpass('Console server password: ')
    except Exception as E:
        print(E)
        exit(2)
    return username, password


def create_device(hostname: str, port: str, username: str, password: str) -> Device:
    """Create a JunOS device

    Args:
        hostname (str): Hostname of the device (IPv4 only)
        port (str): SSH Access port
        username (str): Server login username
        password (str): Server username's password

    Returns:
        Device: JunOS device with an opened connection
    """

    dev = None
    try:
        dev = Device(host=hostname, port=port,
                     user=username, password=password).open()
    except Exception as E:
        print(E)
        exit(3)
    return dev


def apply_config(dev: Device) -> None:
    """Apply the current configuration to the device

    Iterates through a list of configuration file tuples (set in `configuration_files`)
    and applies the templates accordingly

    Args:
        dev (Device): JunOS device object into which the template shall be applied
    """

    try:
        # Follow the documentation nomenclature
        with Config(dev) as cu:  # Let Python manage the lock()ing and unlock()ing
            for conf in configuration_files:  # Iterate through the configuration file tuples
                print(
                    f'Applying Jinja2 configuration template from file {conf.file}')
                # Load YML vars file
                # No try/except block is used here in order not to hide any errors from the end-user
                datavars = yaml.safe_load(open(conf.vars).read())
                # Check if the file is not empty (no vars)
                if datavars:
                    cu.load(template_path=conf.file, template_vars=datavars,
                            format=conf.format, merge=True)
                else:
                    cu.load(template_path=conf.file,
                            format=conf.format, merge=True)
                prompt_check_commit(cu)
    except Exception as E:
        print(E)
        exit(4)


# -----------------
# Main

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--default_login', action='store_true',
                        help='Use default username and password (only prompt user for hostname and port)')
    args = parser.parse_args()

    host, port = prompt_hostname()

    if args.default_login:
        login_info = (DEFAULT_USERNAME, DEFAULT_PASSWORD)
    else:
        login_info = prompt_login_information()

    dev = create_device(host, port, *login_info)
    apply_config(dev)

    print('Done')
    exit(0)
