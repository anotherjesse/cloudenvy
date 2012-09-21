# vim: tabstop=4 shiftwidth=4 softtabstop=4

import argparse
import getpass
import os
import os.path
import yaml


from cloudenvy.envy import Envy


CONFIG_DEFAULTS = {
    'keypair_name': getpass.getuser(),
    'keypair_location': os.path.expanduser('~/.ssh/id_rsa.pub'),
    'flavor_name': 'm1.small',
    'sec_group_name': 'cloudenvy',
    'remote_user': 'ubuntu',
    'auto_provision': False,
}


class BaseCommand(object):

    def __init__(self, args, subparsers):

        config = self._get_config(args)

        # if user defines -n in cli, append name to project name.
        if args.name:
            config['project_config']['name'] = '%s-%s' % (
                config['project_config']['name'], args.name)
        self.config = config
        self.envy = Envy(self.config)
        self.subparsers = subparsers

    def _get_config(self, args):
        user_config_path = os.path.expanduser('~/.cloudenvy')
        project_config_path = './Envyfile'

        self._check_config_files(user_config_path, project_config_path)

        user_config = {'cloudenvy': CONFIG_DEFAULTS}
        user_yaml = yaml.load(open(user_config_path))['cloudenvy']
        user_config.update({'cloudenvy': user_yaml})
        project_config = yaml.load(open(project_config_path))

        config = dict(project_config.items() + user_config.items())

        # Updae config dict with which cloud to use.
        if args.cloud:
            if args.cloud in config['cloudenvy']['clouds'].keys():
                config['cloudenvy'].update(
                    {'cloud': ['cloudenvy']['clouds'][args.cloud]})
        else:
            config['cloudenvy'].update(
                {'cloud': config['cloudenvy']['clouds'].itervalues().next()})
        # Exits if there are issues with configuration.
        self._validate_config(config)

        return config

    def _validate_config(self, config):
        for item in ['name', 'flavor_name']:
            config_item = config['project_config'].get(item)
            if config_item == None:
                raise SystemExit('Missing Configuration: Make sure `%s` is '
                                 'set in your project\'s Envyfile')

        # If credentials config is not set, send output to user.
        for item in ['username', 'password', 'tenant_name', 'auth_url']:
            config_name = 'os_%s' % item
            config_item = config['cloudenvy']['cloud'].get(config_name)

            if config_item == None:
                raise SystemExit('Missing Credentials: Make sure `%s` is set '
                                 'in ~/.cloudenvy' % config_name)

    def _check_config_files(self, user_config_path, project_config_path):
        if not os.path.exists(user_config_path):
            raise SystemExit('Could not read ~/.cloudenvy. Please make sure '
                             '~/.cloudenvy has the proper configuration.')

        if not os.path.exists(project_config_path):
            raise SystemExit('Could not read ./Envyfile. Please make sure you'
                             'have an EnvyFile in your current directory.')
