# vim: tabstop=4 shiftwidth=4 softtabstop=4

import argparse

COMMANDS = [up, provision, snapshot, ip, ssh, destroy, scp]


def _build_parser():
    parser = argparse.ArgumentParser(
        description='Launch a virtual machine in an openstack environment.')
    parser.add_argument('-v', '--verbosity', action='count',
                        help='increase output verbosity')
    parser.add_argument('-c', '--cloud', action='store',
                        help='specify which cloud to use')

    subparsers = parser.add_subparsers(title='Available commands:')

    for cmd in COMMANDS:
        cmd_name = cmd.func_name
        helptext = getattr(cmd, '__doc__', '')
        subparser = subparsers.add_parser(cmd_name, help=helptext)
        subparser.set_defaults(func=cmd)

        # NOTE(termie): add some specific options, if this ever gets too
        #               large we should probably switch to manually
        #               specifying each parser
        if cmd_name in ('up', 'provision', 'snapshot', 'ip', 'scp', 'ssh',
                        'destroy'):
            subparser.add_argument('-n', '--name', action='store',
                           help='specify custom name for an ENVy',
                           default='')

        if cmd_name in ('provision', 'up'):
            subparser.add_argument('-u', '--userdata', action='store',
                                   help='specify the location of userdata')
        if cmd_name in ('provision'):
            subparser.add_argument('-r', '--remote_user', action='store',
                                   help='remote user to provision',
                                   default=None)
        if cmd_name in ('up'):
            subparser.add_argument('-p', '--provision', action='store_true',
                                   help='supply userdata at server creation',
                                   default=False)
        if cmd_name in ('scp'):
            subparser.add_argument('source')
            subparser.add_argument('target')

    return parser


def main():
    parser = _build_parser()
    args = parser.parse_args()

    if args.verbosity == 3:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('novaclient').setLevel(logging.DEBUG)
    elif args.verbosity == 2:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('novaclient').setLevel(logging.INFO)
    elif args.verbosity == 1:
        logging.getLogger().setLevel(logging.INFO)

    args.func(args)
