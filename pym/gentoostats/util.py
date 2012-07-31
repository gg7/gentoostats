#!/usr/bin/env python
#
# Copyright 2011 Vikraman Choudhury <vikraman.choudhury@gmail.com>
# Copyright 2012 G. Gaydarov <ggaydarov@gmail.com>
#
# Distributed under the terms of the GNU General Public License v2 or later

from __future__ import print_function

import sys
import json
import argparse

try:
	import ConfigParser
except ImportError:
	import configparser as ConfigParser

# TODO: Make this a class?
def FlexibleBool(arg):
	arg = str(arg).lower()

	if arg in ['1', 'y', 'yes', 'true', 'on']:
		return True

	if arg in ['0', 'n', 'no', 'false', 'off']:
		return False

	msg = "Error: Argument '%s' is not a valid boolean value. " + \
	      "Try using 'true' or 'false'." % arg

	raise argparse.ArgumentTypeError(msg)

def serialize(obj, human=False):
	"""
	Encode an object using JSON.
	"""
	if human:
		indent     = 2
		sort_keys  = True
		separators = (', ', ': ')
	else:
		indent     = None
		sort_keys  = False
		separators = (',', ':')

	encoder = json.JSONEncoder( indent       = indent
	                          , sort_keys    = sort_keys
	                          , separators   = separators
	                          , ensure_ascii = False # TODO: double check
	)

	return encoder.encode(obj)

def get_auth_config(auth_file):
	"""
	Read auth info from the config file "auth_file".
	"""

	config_parser = ConfigParser.ConfigParser()
	if len(config_parser.read(auth_file)) == 0:
		print('Error: Cannot parse config file %s' % auth_file, file=sys.stderr)
		# TODO: this should be an exception
		sys.exit(1)

	try:
		return { 'UUID':   config_parser.get('AUTH', 'UUID')
		       , 'PASSWD': config_parser.get('AUTH', 'PASSWD')
		}
	except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
		print('Error: Malformed auth config.', file=sys.stderr)
		# TODO: this should be an exception
		sys.exit(1)

def get_payload_config(payload_file):
	config_parser = ConfigParser.ConfigParser()
	if len(config_parser.read(payload_file)) == 0:
		print('Error: Cannot parse config file %s' % payload_file, \
				file=sys.stderr)

		# TODO: this should be an exception
		sys.exit(1)
	return config_parser
