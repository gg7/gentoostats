#!/usr/bin/env python
#
# Copyright 2011 Vikraman Choudhury <vikraman.choudhury@gmail.com>
# Copyright 2012 G. Gaydarov <ggaydarov@gmail.com>
#
# Distributed under the terms of the GNU General Public License v2 or later

"""
'gentoostats' reports various Gentoo-related statistics to an official Gentoo
server.
"""

from __future__ import print_function

__docformat__   = 'epytext'
__version__     = "svn"
__productname__ = "gentoostats"
__authors__     = ('Vikraman Choudhury <vikraman.choudhury@gmail.com>, 2011',
                   'G. Gaydarov <ggaydarov@gmail.com>, 2012')

import __builtin__

import os
import sys
import pkgutil

import gentoolkit
from .config import Config
from .app_util import *
from .argument_parser_wrapper import ArgumentParserWrapper

# Add ./modules/ to the current Python path:
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
import modules

# make an exportable copy of the __info__ variables:
MODULE_META = get_module_meta(locals())

APP_DEFAULT_CONFIG = dict(
	verbose  = 1,
	indent   = 2,  # Gentoolkit uses 1, 2 or 4 here
	indent_c = 28, # Gentoolkit uses 25 here
)

# You don't have to run main() to populate these:
NAME_MAP = {}
FORMATTED_OPTIONS = []

# Dynamically build the modules list:
for _, name, _ in pkgutil.iter_modules(modules.__path__):
	loaded_module = __import__(
		name, globals(), locals(), ['MODULE_INFO'], -1
	)

	command, name, desc = loaded_module.MODULE_INFO

	NAME_MAP[command] = name
	FORMATTED_OPTIONS.append((bold_out_command(command, name), desc))


def set_args(parser):
	"""Adds module arguments to parser."""

	parser.add_argument( '-h', '--help'
	                   , action='store_true'
	                   , help="Display this help message"
	)
	parser.add_argument( '-q', '--quiet'
	                   , action='store_true'
	                   , help="Set verbosity to 0"
	)
	parser.add_argument( '-v', '--verbose'
	                   , action='count'
	                   , default=None
	                   , help="Increase verbosity level"
	)
	parser.add_argument( '-C', '--no-color', '--no-colour', \
	                     '--nocolor', '--nocolour'
	                   , dest='nocolor'
	                   , action='store_true'
	                   , help="Turn off colors"
	)
	parser.add_argument( '-N', '--no-pipe', '--nopipe'
	                   , dest='nopipe'
	                   , action='store_true'
	                   , help="Turn off pipe detection"
	)
	parser.add_argument( '-V', '--version'
	                   , action='store_true'
	                   , help="Display version info"
	)
	parser.add_argument( '--debug'
	                   , action='store_true'
	                   , ignore_in_desc=True
	                   , help="Debug mode"
	)
	parser.add_argument( 'module'
	                   , nargs='?'
	                   , ignore_in_desc=True
	)

def main(args):
	"""Parse input and run the program."""

	gentoolkit.base.initialize_configuration()

	config = Config()
	config.update(APP_DEFAULT_CONFIG)

	arg_parser = ArgumentParserWrapper(
		name     = MODULE_META['__productname__'],
		desc     = MODULE_META['__doc__'],
		is_app   = True,
		add_help = False,
		indent   = config.indent,
		indent_c = config.indent_c,
	)
	set_args(arg_parser)
	arg_parser.set_modules(FORMATTED_OPTIONS)

	global_args, module_args = arg_parser.parse_known_args(args)
	config.hard_update(vars(global_args))

	# Normally argparse takes care of --help and prints a help message if
	# -h/--help is present in args. However, I want to be able to print the
	# module help message with `gentoostats -h MODULE`, not the help message for
	# the app (this file), so I've resorted to a couple of hacks.
	if config.help and not config.module:
		arg_parser.print_help(with_description=True)
		return 0

	if not config.module:
		arg_parser.print_help(with_description=False)
		return 2

	if config.help:
		module_args.append('-h')
		config.help=None

	if config.quiet:
		if config.verbose and config.verbose > 0:
			arg_parser.error("Error: 'verbose' and 'quiet' are both set")
		else:
			config.verbose = 0

	propagate_config_to_gentoolkit(config)

	if config.version:
		gentoolkit.base.print_version(MODULE_META)
		return 0

	module_name = config.module[0]

	if module_name == 'help':
		arg_parser.print_help(with_description=True)
		return 0

	try:
		expanded_module_name = expand_module_name(NAME_MAP, module_name)
	except KeyError:
		arg_parser.error("Unknown module '%s'" % module_name)

	loaded_module = __import__(
		expanded_module_name, globals(), locals(), [], -1
	)

	return loaded_module.main(module_args, config)

if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))
