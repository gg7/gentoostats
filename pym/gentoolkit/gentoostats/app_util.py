#!/usr/bin/env python
#
# Copyright 2011 Vikraman Choudhury <vikraman.choudhury@gmail.com>
# Copyright 2012 G. Gaydarov <ggaydarov@gmail.com>
#
# Distributed under the terms of the GNU General Public License v2 or later

"""Contains various application utility functions."""

from __future__ import print_function

import gentoolkit
from gentoolkit.textwrap_ import TextWrapper

def expand_module_name(name_map, module_name):
	"""Returns one of the values of 'name_map' or raises KeyError"""

	# module_name can be a Python builtin type, so we must rename our module
	while module_name in dir(__builtins__):
		module_name += '_'

	if module_name in name_map.values():
		return module_name
	else:
		return name_map[module_name]

def bold_out_command(command, name):
	"""
	Usage:
		>>> bold_out_command('s', 'submit')
		"(s)ubmit"
		>>> bold_out_command('p', 'no-pipe')
		"no-(p)ipe"
		>>> bold_out_command('D', 'debug')
		"debug (D)"
		>>> bold_out_command('yz', 'xyz')
		"x(yz)"
		>>> bold_out_command('', 'xyz')
		"xyz"
		>>> bold_out_command(None, 'xyz')
		"xyz"
	"""

	if not command:
		return name

	try:
		start = name.index(command)
		end   = start + len(command)

		return "%s(%s)%s" % (name[:start], command, name[end:])
	except ValueError:
		return "%s (%s)" % (name, command)

def get_module_meta(locals_):
	"""Filters a dict for string variables __likeThis__"""

	result = {k: v for k, v in locals_.items() \
		if k.startswith('__') and k.endswith('__') and isinstance(v, basestring)
	}

	if '__doc__' in result:
		result['__doc__'] = result['__doc__'].replace('\n', ' ').strip()

	return result

def format_options_respect_newline(options, indent_c=25):
	"""Like format_options, but respects newlines."""

	wrapper = TextWrapper(width=gentoolkit.CONFIG['termWidth'])
	result = []

	opts, descs = zip(*options)
	for opt, desc in zip(opts, descs):
		wrapper.initial_indent = gentoolkit.pprinter.emph(opt.ljust(indent_c))
		wrapper.subsequent_indent = " " * indent_c

		for line in desc.splitlines():
			result.append(wrapper.fill(line))
			wrapper.initial_indent = ''.ljust(indent_c)

	return '\n'.join(result)

def propagate_config_to_gentoolkit(config):
	"""
	@param config Config object
	"""

	if config.quiet:
		gentoolkit.CONFIG['quiet'] = True

	if config.nocolor:
		gentoolkit.CONFIG['color'] = 0
		gentoolkit.pprinter.output.nocolor()

	if config.nopipe:
		gentoolkit.CONFIG['piping'] = False

	if config.debug:
		gentoolkit.CONFIG['debug'] = True
