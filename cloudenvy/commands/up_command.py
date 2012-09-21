import logging

from base_command import BaseCommand

import fabric.api
import fabric.operations

from cloudenvy import exceptions
from cloudenvy.envy import Envy
# from cloudenvy.commands import provision


class UpCommand(BaseCommand):
    """Create a server and show its IP."""

    def __str__(self):
        return self.__class__.__name__.split('Command')[0].lower()

    def arguments(self):
        subparser.add_argument('-n', '--name', action='store', default='',
                               help='specify custom name for an ENVy')

        subparser.add_argument('-u', '--userdata', action='store',
                               help='specify the location of userdata')

    def run(self, args):
        if not self.envy.server():
            logging.info('Building environment.')
            try:
                self.envy.build_server()
            except exceptions.ImageNotFound:
                logging.error('Could not find image.')
                return
            except exceptions.NoIPsAvailable:
                logging.error('Could not find free IP.')
                return
        if self.envy.auto_provision:
            self.provision(args)
        if self.envy.ip():
            print self.envy.ip()
        else:
            print 'Environment has no IP.'
