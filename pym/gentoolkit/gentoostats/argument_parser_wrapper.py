#!/usr/bin/env python
#
# Copyright 2011 Vikraman Choudhury <vikraman.choudhury@gmail.com>
# Copyright 2012 G. Gaydarov <ggaydarov@gmail.com>
#
# Distributed under the terms of the GNU General Public License v2 or later

from __future__ import print_function

try:
	# Support Python 2.6 (argparse is part of Python 2.7+):
	import argparse
except ImportError:
	from . import argparse

import sys

import gentoolkit
from gentoolkit.gentoostats.app_util import format_options_respect_newline
from gentoolkit.base import mod_usage, main_usage

DEFAULT_OPT_INDENT = 2
DEFAULT_COL_INDENT = 25

class ArgumentParserWrapper(object):
	"""A simple wrapper around argparse.ArgumentParser.

	The purpose of this is to make argparse's messages Gentoolkit-like.
	To do that one can either extend or monkey-patch argparse. I did the latter.
	"""

	def __init__(self, name, desc, is_app=False, indent=None, indent_c=None, \
			*args, **kwargs):
		"""
		@param name Name of the app/module.
		@type  name str
		@param desc Short description of the app/module.
		@type  name str
		@param is_app Is this an application or a module?
		@type  is_app boolean
		@param indent Indentation length for the arguments (used by --help)
		@type  indent number
		@param indent_c Indentation length for the argument descriptions
		@type  indent_c number
		@param args Arguments to pass directly to argparse.ArgumentParser
		@type  args list
		@param kwargs Keyword arguments to pass to argparse.ArgumentParser
		@type  kwargs dict
		"""

		self.name   = name
		self.desc   = desc
		self.is_app = is_app

		# Default argument values don't cut it.
		if indent is None:
			self.indent = DEFAULT_OPT_INDENT
		else:
			self.indent = indent

		if indent_c is None:
			self.indent_c = DEFAULT_COL_INDENT
		else:
			self.indent_c = indent_c

		self.args = list()
		self.formatted_modules = []

		self.parser = argparse.ArgumentParser(
			prog=self.name,
			description=self.desc,
			*args,
			**kwargs
		)

		# Monkey-patch these functions:
		self.parser.error       = self.error_monkey_patch
		self.parser.print_help  = self.print_help_monkey_patch
		self.parser.print_usage = self.print_usage_monkey_patch

	def set_modules(self, formatted_modules):
		"""
		Applications should use this method to set module descriptions.
		"""

		self.formatted_modules = formatted_modules

	def add_argument(self, *args, **kwargs):
		"""
		Add an argument to the parser.
		"""

		#if '-h' in args or '--help' in args:
		#	self.args.append( (args, kwargs) )
		#	return

		kwargs_to_pass = dict(kwargs)
		if 'ignore_in_desc' in kwargs:
			kwargs_to_pass.pop('ignore_in_desc')

		# Don't change args if there's an exception:
		result = self.parser.add_argument(*args, **kwargs_to_pass)
		self.args.append( (args, kwargs) )
		return result

	def error_monkey_patch(self, message, *args, **kwargs):
		"""
		Prints a usage message incorporating the message to stderr and
		exits.

		Argparse.py says:
			"If you override this in a subclass, it should not return -- it
			should either exit or raise an exception."
		"""

		# TODO: Improve this.

		def _replace_if_found(s, what_to_replace, replacement):
			"""
				>>> _replace_if_found("abcd", "ab", "1")
				(True, "1cd")
				>>> _replace_if_found("abcd", "x", "1")
				(False, "abcd")
			"""

			new_s = s.replace(what_to_replace, replacement)
			return (new_s != s, new_s)

		def _translate_message(message):
			"""
			Translates argparse messages to gentoolkit messages (kinda).
			"""

			found, message = \
				_replace_if_found(
					message, 'the following arguments are required: ', ''
				)
			if found:
				return "Missing argument(s): " + message

			found, message = \
				_replace_if_found(message, 'unrecognized arguments: ', '')
			if found:
				return 'Argument \'%s\' not recognized' \
						% (message.split(' ')[0])

			found, message = _replace_if_found(message, 'argument ', '')
			if found:
				return 'Argument ' + message

			# Else return the message as it is:
			return message

		message = _translate_message(message)
		print(gentoolkit.pprinter.error(message), file=sys.stderr)
		self.print_help(stream=sys.stderr)

		self.exit(2)

	def print_help_monkey_patch(self, *args, **kwargs):
		return self.print_help(with_description=True)

	def print_usage_monkey_patch(self, *args, **kwargs):
		return self.print_usage()

	def get_formatted_options(self):
		"""
		Produces the analogue of 'formatted_options' in enalyze, except that
		there's no hardcoded indent.
		"""

		formatted_options = []

		for args_list, args_dict in self.args:
			if 'ignore_in_desc' in args_dict:
				continue

			metavar = args_dict.get('metavar')
			if metavar is None:
				metavar_str = ''
			else:
				metavar_str = " " + metavar

			# Will only show the first one or two args
			formatted_options += [
				( " " * self.indent + ", ".join(args_list[:2]) + metavar_str
				, args_dict.get('help') or 'No description.'
				)
			]

		return format_options_respect_newline(formatted_options, \
				indent_c=self.indent_c)

	def get_formatted_modules(self):
		"""
		Indents and returns self.formatted_modules. Returns '' if
		formatted_modules have not been set.
		"""

		try:
			indented_modules = [
				(" " * self.indent + opt, desc) for opt, desc in self.formatted_modules
			]

			return format_options_respect_newline(indented_modules, indent_c=self.indent_c)
		except AttributeError:
			return ''

	def print_options(self, stream=sys.stdout):
		"""
		Prints available arguments and their descriptions.
		"""

		if self.is_app:
			print(gentoolkit.pprinter.globaloption("global options"), file=stream)
		else:
			print(gentoolkit.pprinter.command("options"), file=stream)

		print(self.get_formatted_options(), file=stream)

		if self.is_app:
			header = "\n%s (%s)" % \
				(gentoolkit.pprinter.command("modules"), \
				gentoolkit.pprinter.command("short name"))

			print(header, file=stream)
			print(self.get_formatted_modules(), file=stream)


	def print_help(self, with_description=False, stream=sys.stdout):
		"""
		Prints a full help message about the program.
		"""

		if with_description:
			print(self.desc.strip(), file=stream)
			print('', file=stream)

		self.print_usage(stream=stream)
		print('', file=stream)
		self.print_options(stream=stream)

	def print_usage(self, arg='', arg_is_optional=False, stream=sys.stdout):
		"""
		Prints a short synopsis message about the general usage of the
		app/module.
		"""

		if self.is_app:
			print(main_usage(dict(__productname__=self.name)), file=stream)
		else:
			print(mod_usage(self.name, arg=arg, optional=arg_is_optional), file=stream)

	def __getattr__(self, attr):
		return getattr(self.parser, attr)
