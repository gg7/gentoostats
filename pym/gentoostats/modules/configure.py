#!/usr/bin/env python
#
# Copyright 2011 Vikraman Choudhury <vikraman.choudhury@gmail.com>
# Copyright 2012 G. Gaydarov <ggaydarov@gmail.com>
#
# Distributed under the terms of the GNU General Public License v2 or later

from __future__ import print_function

import os
import sys
import uuid
import argparse
# Please don't import readline. Thanks.

try:
	import ConfigParser
except ImportError:
	import configparser as ConfigParser

import gentoolkit
from portage import output

from gentoostats.config import Config
from gentoostats.argument_parser_wrapper import ArgumentParserWrapper

MODULE_INFO = (
	'c', 'configure', 'configure gentoostats'
)

MODULE_DEFAULT_CONFIG = dict(
	verbose      = 0,
	settings_dir = "/etc/gentoostats/",
	auth_file    = "auth.cfg",
	payload_file = "payload.cfg",
)

# Credit for the descriptions:
#   make.conf
#   http://www.gentoo.org/doc/en/handbook/handbook-x86.xml?part=3&chap=3

MAKE_CONF_SETTINGS = (
	("ACCEPT_KEYWORDS",          "The ACCEPT_KEYWORDS variable defines what software branch you use on your system. It defaults to the stable software branch for your architecture, e.g. 'x86'."),
	("ACCEPT_LICENSE",           "This variable is used to mask packages based on licensing restrictions. It may contain both license and group names."),
	("ARCH",                     "System architecture (e.g. 'x86', 'amd64', 'ppc', etc.)."),
	("CFLAGS",                   "C compiler flags."),
	("CHOST",                    "ELIBC, KERNEL and ARCH (e.g. 'i686-pc-linux-gnu')."),
	("CTARGET",                  "Used when cross-compiling."),
	("CXXFLAGS",                 "C++ compiler flags."),
	("EMERGE_DEFAULT_OPTS",      "Default emerge arguments."),
	("FEATURES",                 "See 'FEATURES' in `man make.conf`."),
	("FFLAGS",                   "Fortran compiler flags."),
	("GENTOO_MIRRORS",           "Local mirrors to be used to download files before using the ones specified in the ebuild scripts."),
	("LANG",                     "System locale settings."),
	("LASTSYNC",                 "Last Portage tree synchronisation time."),
	("LDFLAGS",                  "Linker flags."),
	("MAKEOPTS",                 "Arguments for 'make' when emerging packages."),
	("PLATFORM",                 "Kernel, ARCH, processor, and Gentoo base system release (e.g. 'Linux-3.2.1-gentoo-r2-x86_64-Intel-R-_Core-TM-_i3_CPU_M_330_@_2.13GHz-with-gentoo-2.0.3')."),
	("PORTAGE_RSYNC_EXTRA_OPTS", "Default arguments for rsync when running `emerge --sync`."),
	("PROFILE",                  "The current Gentoo system profile (e.g. 'default/linux/amd64/10.0/desktop'."),
	("SYNC",                     "rsync mirror used to sync the local portage tree when `emerge --sync` is run."),
	("USE",                      "Globally enabled USE flags (see 'USE' in `man make.conf`."),
)

PACKAGE_SETTINGS = (
	("WORLDSET",                 "Portage's @world set, containing @system and @world, and any other recursively included sets (i.e. your selected packages)."),
	("BUILD_TIME",               "Report when each package was built (if possible)."),
	("IUSE",                     "Available USE flags for the package."),
	("KEYWORD",                  "Relevant package keyword (e.g. '~amd64')."),
	("PKGUSE",                   "USE flag choice in package.use (or equivalent) for each package (if any)."),
	("REPO",                     "Package repository."),
	("SIZE",                     "Package size."),
	("USE",                      "Final USE flags for each installed package."),
)

def userquery(prompt, responses=None, default_response_num=1):
	"""
	Inspired by portage's _emerge.userquery.

	Gives the user a question ('prompt') and forces him to chose one of the
	responses ('responses', defaulting to 'Yes' and 'No').

	Returns the (full) choice made.
	"""

	# Colour for the default response:
	default_colour_f = output.green
	# Colour for all the other responses:
	normal_colour_f = output.red

	if responses is None:
		responses = ["Yes", "No"]

	coloured_responses = [None] * len(responses)
	for i, r in enumerate(responses):
		if i + 1 == default_response_num:
			coloured_responses[i] = default_colour_f(r)
		else:
			coloured_responses[i] = normal_colour_f(r)

	final_prompt = \
		"%s [%s] " % (output.bold(prompt), "/".join(coloured_responses))

	if sys.hexversion >= 0x3000000:
		input_function = input
	else:
		input_function = raw_input

	while True:
		# Directly using 'input_function(final_prompt)'
		# leads to problems on my machine.

		print(final_prompt, end='')
		response = input_function()

		if not response:
			# Return the default choice:
			return responses[default_response_num-1]

		for r in responses:
			if response.lower() == r[:len(response)].lower():
				return r

		print("Sorry, response '%s' not understood." % response)

def touch_file(path):
	"""
	Analogous to the UNIX 'touch' command, excluding time modification.

	Returns True if the operation was successful, or prints an error message and
	returns False.
	"""

	try:
		open(path, 'a+').close()
		return True
	except IOError as e:
		error_msg = "* Error: unable to open/create file '%s': %s" \
				% (os.path.basename(path), e)
		print(gentoolkit.pprinter.error(error_msg), file=sys.stderr)
		return False

def save_cp(cp, path):
	"""
	Save the ConfigParser 'cp' to the file 'path'.
	"""

	try:
		with open(path, 'w') as f:
			try:
				cp.write(f)
			except Exception as e:
				error_msg = "* Error: unable to save config file '%s': %s" \
						% (os.path.basename(path), e)
				print(gentoolkit.pprinter.error(error_msg), file=sys.stderr)
				sys.exit(1)
	except Exception as e:
		error_msg = "* Error: could not open config ouput file '%s': %s" \
				% (os.path.basename(path), e)
		print(gentoolkit.pprinter.error(error_msg), file=sys.stderr)
		sys.exit(1)

class Configure(object):
	"""
	Configuration 'wizard'.
	"""

	def set_args(self, parser):
		"""Adds module arguments to parser."""

		parser.add_argument( '-h', '--help'
		                   , action='store_true'
		                   , dest='help_dummy'
		                   , only_in_help=True
		                   , help="Display this help message"
		)

	def debug_print(self, verbosity_level, *args, **kwargs):
		if self.config.verbose >= verbosity_level:
			print(*args, **kwargs)

	def __init__(self, config_updates=None):
		self.config = Config()
		self.config.update(MODULE_DEFAULT_CONFIG)

		if config_updates:
			self.config.hard_update(config_updates)

		self.arg_parser = ArgumentParserWrapper(
			name     = MODULE_INFO[1],
			desc     = MODULE_INFO[2],
			indent   = self.config.indent,
			indent_c = self.config.indent_c,
		)
		self.set_args(self.arg_parser)

	def run(self, args):
		"""
		Runs the module.

		@param args input arguments to be parsed.
		@type  args list
		"""

		self.config.hard_update(vars(self.arg_parser.parse_args(args)))

		self.debug_print(2, "* Checking if the settings directory exists")
		if not os.path.isdir(self.config.settings_dir):
			try:
				# NOTE: Creation of '/etc/' is not handled here.
				# To do that, see 'os.makedirs'.
				os.mkdir(self.config.settings_dir)
				self.debug_print(1, "* Created settings directory '%s'")
			except OSError as e:
				error_msg = \
					"* Error: unable to create the config directory: " + e
				print(gentoolkit.pprinter.error(error_msg), file=sys.stderr)
				return 1

		self.configure_auth()
		self.configure_payload()

		self.debug_print(1, "* Configuration complete!")
		return 0

	def configure_auth(self):
		file_s = os.path.join(self.config.settings_dir, self.config.auth_file)

		# Make sure to create the auth file if it doesn't already exist:
		if not touch_file(file_s):
			return

		cp = ConfigParser.RawConfigParser()

		# If a config already exists, read it:
		cp.read(file_s)

		if not cp.has_section('AUTH'):
			cp.add_section('AUTH')
			self.debug_print(2, "* Created 'AUTH' section in config")

		if cp.has_option('AUTH', 'UUID'):
			self.debug_print(2, "* UUID already exists, skipping")
		else:
			the_uuid = str(uuid.uuid4())
			cp.set('AUTH', 'UUID', the_uuid)
			self.debug_print(2, "* Generated UUID '%s'" % (the_uuid))

		if cp.has_option('AUTH', 'PASSWD'):
			self.debug_print(2, "* PASSWD already exists, skipping")
		else:
			# passwd = str(uuid.uuid4()).replace('-', '')
			# passwd = base64.urlsafe_b64encode(os.urandom(16))[:16]
			passwd = os.urandom(16).encode("base64")[:16]
			cp.set('AUTH', 'PASSWD', passwd)
			self.debug_print(2, "* Generated PASSWD")

		save_cp(cp, file_s)
		return

	def configure_payload(self):
		file_s = os.path.join(self.config.settings_dir, self.config.payload_file)

		# Make sure to create the payload file if it doesn't already exist:
		if not touch_file(file_s):
			return

		cp = ConfigParser.RawConfigParser()

		# If a config already exists, read it and update it:
		cp.read(file_s)

		if not cp.has_section('ENV'):
			cp.add_section('ENV')
			self.debug_print(2, "* Created 'ENV' section in config")

		while True:
			answer = userquery("Would you like to report any make.conf options?", ["Yes", "Help", "No"])
			if answer == 'Help':
				print("  You'll be asked exactly what to report. If in doubt, answer 'Yes'.")
			else:
				break

		if answer == "Yes":
			for setting, desc in MAKE_CONF_SETTINGS:
				while True:
					answer = userquery("  Report %s?" % setting, ["Yes", "Help", "No"])
					if answer == 'Help':
						print("    Short description of %s: %s" % (setting, desc))
					else:
						cp.set('ENV', setting, answer.lower())
						break
		else:
			for setting, _ in MAKE_CONF_SETTINGS:
				cp.set('ENV', setting, 'no')

		if not cp.has_section('PACKAGES'):
			cp.add_section('PACKAGES')
			self.debug_print(2, "* Created 'PACKAGES' section in config")

		while True:
			answer = userquery("Would you like to report statistics about your packages?", ["Yes", "Help", "No"])
			if answer == 'Help':
				print("  You'll be asked exactly what to report. If in doubt, answer 'Yes'.")
			else:
				break

		if answer == "Yes":
			for setting, desc in PACKAGE_SETTINGS:
				while True:
					answer = userquery("  Report %s?" % setting, ["Yes", "Help", "No"])
					if answer == 'Help':
						print("    Short description of %s: %s" % (setting, desc))
					else:
						cp.set('PACKAGES', setting, answer.lower())
						break
		else:
			for setting, _ in PACKAGE_SETTINGS:
				cp.set('PACKAGES', setting, 'no')

		save_cp(cp, file_s)
		return

def main(args, config=None):
	return Configure(config).run(args)

if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))
