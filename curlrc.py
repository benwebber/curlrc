#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Treat curl configuration files as commands.
"""

from __future__ import print_function

import argparse
import collections
import glob
import json
import os
import os.path
import re
import sys

__version__ = '0.2.1'

CURL_HOME = os.getenv('CURL_HOME', os.path.expanduser('~/.curl'))
CURLRC_EXTENSION = '.rc'
# Split option lines on this pattern.
CURLRC_OPTION_EXPR = re.compile(r'\s?[\s=:]\s?')
# Match %{variable} strings in format.
CURLRC_FORMAT_STRING_EXPR = re.compile(r'%{[\w]+}')
OUTPUT_FORMATS = ('csv', 'json', 'table')


class CurlConfig(object):
    """
    A curl configuration.
    """
    def __init__(self, name, path=None, description=None, **options):
        self.name = name
        self.path = path
        self.description = description
        self.options = options

    @classmethod
    def from_file(cls, path):
        """
        Load a curl configuration from a file.

        Args:
            path: path to curl configuration file

        Returns: CurlConfig
        """
        name = os.path.basename(path).replace(CURLRC_EXTENSION, '')
        description = None
        options = {}
        with open(path) as config:
            # Extract description from first line if it is a comment.
            first_line = config.readline().strip()
            if first_line.startswith('#'):
                description = first_line.split('#')[1].strip()
            # Collect options as a dictionary.
            options = dict(cls.split_line(line.strip())
                           for line in config if not line.startswith('#'))
        return cls(name, path, description, **options)

    @property
    def template(self):
        """
        Retrieve the format string specified in the configuration file.

        Returns: str or None
        """
        return self.options.get('-w', self.options.get('--write-out'))

    @staticmethod
    def split_line(line):
        """
        Split curl option lines into key-value pairs.

        Args:
            line: curl configuration option line

        Returns: list of [option, value]
        """
        option = re.split(CURLRC_OPTION_EXPR, line, maxsplit=1)
        # Handle boolean flags (e.g., -s).
        if len(option) < 2:
            option.append(True)
        return option


class CurlTemplate(object):
    """
    A curl output template.
    """
    def __init__(self, replacements):
        self._map = replacements

    @classmethod
    def from_str(cls, template):
        """
        Load the template from a template string.
        """
        chars_to_remove = '%{}'
        _map = collections.OrderedDict()
        for tmpl in re.findall(CURLRC_FORMAT_STRING_EXPR, template):
            _map[''.join(c for c in tmpl if c not in chars_to_remove)] = tmpl
        return cls(_map)

    def as_csv(self, pretty=True):
        """
        Output the template as comma-separated values.
        """
        output = ''
        if pretty:
            output = ','.join(self._map.keys())
            output += '\n'
        output += ','.join(self._map.values())
        return output + '\n'

    def as_json(self, pretty=True):
        """
        Output the template as a JSON hash.
        """
        indent = 2 if pretty else None
        return json.dumps(self._map, indent=indent) + '\n'

    def as_table(self, pretty=True):
        """
        Output the template as a tab-separated table.
        """
        lines = []
        for field, value in self._map.items():
            if pretty:
                lines.append('{}\t{}'.format(field, value))
            else:
                lines.append(value)
        output = '\n'.join(lines)
        return output + '\n'


def curl_configs(path=None, pattern=None):
    """
    Locate curl configurations in a directory.

    Args:
        path: directory containing configuration files (default: CURL_HOME)
        pattern: glob pattern to match (default: *.rc)

    Returns: list of files
    """
    path = path if path else CURL_HOME
    pattern = pattern if pattern else '*{}'.format(CURLRC_EXTENSION)
    return glob.glob(os.path.join(path, pattern))


def parse_args(argv):
    """
    Parse command-line arguments.

    Returns: argparse.Namespace
    """
    usage_template = '{} {} [OPTION...] -- [CURL ARGS...]'.format

    parser = argparse.ArgumentParser(
        usage=usage_template('%(prog)s', 'COMMAND'),
        version='%(prog)s {}'.format(__version__),
    )

    # Define common arguments for subcommands.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        '-f', '--format',
        choices=OUTPUT_FORMATS,
        help='output format',
    )
    # Control pretty-printing.
    pretty = common.add_mutually_exclusive_group()
    pretty.add_argument(
        '--pretty',
        action='store_true', default=True,
        help='pretty-print output [%(default)s]',
    )
    pretty.add_argument(
        '--no-pretty',
        action='store_false', default=False, dest='pretty',
        help='do not pretty-print output [%(default)s]',
    )
    # Pass the rest of the arguments to curl.
    common.add_argument(
        'curl_args',
        nargs='*', metavar='CURL ARGS',
        help='arguments passed to curl',
    )

    # Extract command names from .curlrc files.
    subparsers = parser.add_subparsers(
        title='commands', dest='command',
        # hide {command1,command2} output
        metavar='',
    )
    # Python 3.3 introduced a regression that makes subparsers optional:
    # <http://bugs.python.org/issue9253>
    # This is a no-op in Python 2.
    subparsers.required = True
    commands = [CurlConfig.from_file(c) for c in curl_configs()]
    for command in commands:
        subparsers.add_parser(
            command.name,
            help=command.description, parents=[common],
            # %(prog)s evaluates to the top-level parser's usage string.
            usage=usage_template(os.path.basename(sys.argv[0]), command.name)
        )

    return parser.parse_args(argv)


def main(argv=None):
    argv = argv if argv else sys.argv[1:]
    args = parse_args(argv)

    config = CurlConfig.from_file(
        os.path.join(CURL_HOME, '{}{}'.format(args.command, CURLRC_EXTENSION))
    )

    # If the user specified a format, override the format specified
    # in the configuration file.
    if args.format and config.template:
        tmpl = CurlTemplate.from_str(config.template)
        formats = {
            'csv': tmpl.as_csv,
            'json': tmpl.as_json,
            'table': tmpl.as_table,
        }
        override_format = formats[args.format](args.pretty)
        curl_args = ['-w', override_format]
        curl_args.extend(args.curl_args)
    else:
        curl_args = args.curl_args

    os.execlp('curl', 'curl', '-K', config.path, *curl_args)


if __name__ == '__main__':
    main()
