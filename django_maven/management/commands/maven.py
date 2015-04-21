import sys
from optparse import OptionParser

from django.conf import settings
from django.core.management import get_commands, load_command_class
from django.core.management.base import (BaseCommand, handle_default_options,
                                         CommandError)

from raven import Client

from django_maven.compat import OutputWrapper


class Command(BaseCommand):

    help = 'Capture exceptions and send in Sentry'
    args = '<command>'

    def _get_subcommand_class(self, command):
        commands = get_commands()
        app_name = commands[command]
        return load_command_class(app_name, command)

    def _write_error_in_stderr(self, exc):
        stderr = getattr(self, 'stderr', OutputWrapper(sys.stderr,
                                                       self.style.ERROR))
        stderr.write('%s: %s' % (exc.__class__.__name__, exc))
        sys.exit(1)

    def usage(self, subcommand):
        usage = 'Usage: %s %s [command options]' % (subcommand, self.args)
        if self.help:
            return '%s\n\n%s' % (usage, self.help)
        else:
            return usage

    def create_parser(self, prog_name, subcommand, subcommand_class):
        if not self.use_argparse:
            return OptionParser(prog=prog_name,
                                usage=subcommand_class.usage(subcommand),
                                version=subcommand_class.get_version(),
                                option_list=subcommand_class.option_list)
        else:
            return super(Command, self).create_parser(prog_name, subcommand)

    def run_from_argv(self, argv):
        if len(argv) <= 2 or argv[2] in ['-h', '--help']:
            print self.usage(argv[1])
            sys.exit(1)

        subcommand_class = self._get_subcommand_class(argv[2])
        parser = self.create_parser(argv[0], argv[2], subcommand_class)
        if self.use_argparse:
            options = parser.parse_args(argv[3:])
            cmd_options = vars(options)
            args = cmd_options.pop('args', ())
        else:
            options, args = parser.parse_args(argv[3:])
        handle_default_options(options)
        try:
            subcommand_class.execute(*args, **options.__dict__)
        except Exception as e:
            if not isinstance(e, CommandError):
                if hasattr(settings, 'SENTRY_DSN'):
                    dsn = settings.SENTRY_DSN
                elif hasattr(settings, 'RAVEN_CONFIG'):
                    dsn = settings.RAVEN_CONFIG.get('dsn')
                else:
                    raise
                sentry = Client(dsn)
                sentry.get_ident(sentry.captureException())

            self._write_error_in_stderr(e)
