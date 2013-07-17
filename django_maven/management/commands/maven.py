import sys
from optparse import OptionParser

from django.conf import settings
from django.core.management import get_commands, load_command_class
from django.core.management.base import (BaseCommand, handle_default_options,
                                         CommandError, OutputWrapper)

from raven import Client


class Command(BaseCommand):

    def _get_subcommand_class(self, command):
        commands = get_commands()
        app_name = commands[command]
        return load_command_class(app_name, command)

    def create_parser(self, prog_name, subcommand, subcommand_class):
        return OptionParser(prog=prog_name,
                            usage=subcommand_class.usage(subcommand),
                            version=subcommand_class.get_version(),
                            option_list=subcommand_class.option_list)

    def run_from_argv(self, argv):
        subcommand_class = self._get_subcommand_class(argv[2])

        parser = self.create_parser(argv[0], argv[2], subcommand_class)
        options, args = parser.parse_args(argv[3:])
        handle_default_options(options)
        try:
            subcommand_class.execute(*args, **options.__dict__)
        except Exception as e:
            if options.traceback or not isinstance(e, CommandError):
                raise
            else:
                sentry = Client(settings.SENTRY_DSN)
                sentry.get_ident(sentry.captureException())

            # self.stderr is not guaranteed to be set here
            stderr = getattr(self, 'stderr', OutputWrapper(sys.stderr,
                                                           self.style.ERROR))
            stderr.write('%s: %s' % (e.__class__.__name__, e))
            sys.exit(1)
