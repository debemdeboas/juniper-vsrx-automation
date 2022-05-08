# Juniper vSRX automation

[This repository](https://github.com/debemdeboas/juniper-vsrx-automation) contains a script that sets up a Juniper vSRX device. It's assumed that the device can accept SSH connections.

## Methodology

The main development principle for this section of the problem is maintainability and ease of use.
The end-user doesn't need to know the inner workings of a Juniper device.
They only need to set some variables in an easy-to-read and easy-to-understand YAML file.

With that in mind, all templates included in this folder were written in a more relaxed tone for readability.

## Templates

The templates directory is called `template/` and it contains Jinja2 configuration templates for the Juniper vSRX device.

### `basic.set.j2`

This template file contains a template for `set <args>` commands in the [`set` format](https://www.juniper.net/documentation/en_US/junos-pyez/topics/task/program/junos-pyez-program-configuration-data-loading.html#task-configuration-load-format-specify).

The following has been taken from the file itself, which is documented with Jinja2 comment blocks:

```jinja
{# Create the users defined in the YAML file #}
{% for user in users %}
set system login user {{ user.name }}{% if user.admin %} class super-user{% else %} class read-only{% endif %}{% if 'password' in user %} authentication encrypted-password {{ user.password }}{% endif %}
{% endfor %}
```

The snippet iterates through the `users` list of dictionaries in the [`./data/basic_set_datavars.yml` file](data/basic_set_datavars.yml):

```yaml
users:
  - name: user
    admin: no
    # This needs to be an MD5-encrypted string literal 
    password: '$6$w8B1Butc$cvdJ9MYPue3fkHEqqgpLopaZLr4ireoXdHEwGcsHoIkj3932KGOZOu7s37Dx03iTcA4h3Chy9ynZ4oCucm6N/0'  
  - name: admin
    admin: yes
```

Each user can have up to three properties, where `name` and `admin` are required.
Setting an encrypted `password` is optional but encouraged.
A password needs to be MD5-encrypted and can be encrypted using the `password_hasher.py` script in this directory.

The `name` property refers to the remote username that will be created on the device.
The `admin` flag determines if the user should receive the `super-user` class or the `read-only` class.
The `password` property is the user's password.

The banner message is also set on this YAML file.
It is important to note the YAML multiline string format that was chosen: `'`.
Other string formats such as `>` or `|` are not compatible.

### `juniper.conf.j2`

This template file contains a template for a [`.conf` file](https://www.juniper.net/documentation/us/en/software/junos/cli/topics/topic-map/junos-configuration-files-overview.html#id-understanding-configuration-files) in the `text` format (needed for the `Config.load()` method).
Its contents are what a new JunOS vSRX configuration looks like when it's been deployed from the vLabs sandbox.

This template's corresponding [variables file](data/juniper_conf_datavars.yml) contains some default configuration values as proof of concept.

## Setup and run

It's encouraged to use Python 3.8 or greater.
First, start a virtual environment and install the required packages:

```bash
# Start a virtual environment at ./venv/
python -m venv venv
# Activate the virtual environment
source venv/bin/activate
# Install the required packages
python -m pip install -r requirements.txt
```

With the environment now ready, the script can be run with:

```bash
# Get prompted for the desired username/password
python juniper.py
# Or you can use the default Juniper CLI user/password
python juniper.py --default_login
```