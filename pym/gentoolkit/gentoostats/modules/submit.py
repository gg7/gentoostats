#!/usr/bin/env python
#
# Copyright 2011 Vikraman Choudhury <vikraman.choudhury@gmail.com>
# Copyright 2012 G. Gaydarov <ggaydarov@gmail.com>
#
# Distributed under the terms of the GNU General Public License v2 or later

"""
Report various Gentoo-related statistics to an official Gentooserver.
"""

from __future__ import print_function

try:
	import httplib
except ImportError:
	import http.client as httplib

import sys

from gentoolkit.gentoostats.util import serialize, FlexibleBool
from gentoolkit.gentoostats.payload import Payload
from gentoolkit.gentoostats.config import Config
from gentoolkit.gentoostats.argument_parser_wrapper import ArgumentParserWrapper

# You can also use __name__.split('.')[-1] here.
MODULE_INFO = (
	's', 'submit', 'generate and submit statistics'
)

MODULE_DEFAULT_CONFIG = dict(
	server       = 'soc.dev.gentoo.org:443',
	server_nossl = 'soc.dev.gentoo.org:80',
	url          = '/upload/',
	auth         = '/etc/gentoostats/auth.cfg',
	payload      = '/etc/gentoostats/payload.cfg',
	verbose      = 1,
	pretend      = False,
	ssl          = True,
)

class Submit(object):
	"""
	Module class.
	"""

	def set_args(self, parser):
		"""Adds module arguments to parser."""

		parser.add_argument( '-h', '--help'
		                   , action='store_true'
		                   , dest='help_dummy'
		                   , only_in_help=True
		                   , help="Display this help message"
		)
		parser.add_argument( '-s', '--server'
		                   , metavar="ADDR:PORT"
		                   , default=self.config.server
		                   , help="Server to upload stats to\n(default: %s)" % (self.config.server)
		)
		parser.add_argument( '-u', '--url'
		                   , metavar="URL"
		                   , default=self.config.url
		                   , help="URL to use for the upload (e.g. /upload/)"
		)
		parser.add_argument( '-p', '--pretend'
		                   , action='store_true'
		                   , default=self.config.pretend
		                   , help="Generate, but don't upload stats"
		)
		parser.add_argument( '-a', '--auth'
		                   , metavar="FILE"
		                   , default=self.config.auth
		                   , help="Authentication config file\n(default: %s)" % (self.config.auth)
		)
		parser.add_argument( '-P', '--payload'
		                   , metavar="FILE"
		                   , default=self.config.payload
		                   , help="Payload config file\n(default: %s)" % (self.config.payload)
		)
		parser.add_argument( '--ssl'
		                   , type=FlexibleBool
		                   , metavar="CHOICE"
		                   , default=self.config.ssl
		                   , help="Use SSL when uploading stats (default: %s)" \
		                           % ('yes' if self.config.ssl else 'no')
		)

	def __init__(self, config_updates=None):
		self.config = Config()
		self.config.update(MODULE_DEFAULT_CONFIG)

		if config_updates:
			self.config.update(config_updates)

		self.arg_parser = ArgumentParserWrapper(
			name     = MODULE_INFO[1],
			desc     = MODULE_INFO[2],
			indent   = self.config.indent,
			indent_c = self.config.indent_c,
		)
		self.set_args(self.arg_parser)

	def run(self, args):
		"""runs the module

		@param args Input arguments to be parsed.
		@type  args list
		"""

		self.config.update(vars(self.arg_parser.parse_args(args)))

		if self.config.ssl == False and \
				self.config.server == MODULE_DEFAULT_CONFIG['server']:
			print("Note: Have you forgotten to change the port number?")
			print("You may want to try '%s'." % self.config.server_nossl)

		self.config.url = self.config.url.rstrip('/') + '/'
		full_upload_url = self.config.server + self.config.url

		if self.config.verbose:
			print("Using URL: '%s'" % (full_upload_url))
			print("Using SSL: %s"   % (self.config.ssl))
			if self.config.pretend:
				print("Dry run:   %s" % (self.config.pretend))

			print("\nGenerating payload... ", end='')
			sys.stdout.flush()

		payload = Payload(
			payload_file=self.config.payload,
			auth_file=self.config.auth
		)
		post_data = payload.get()

		if self.config.verbose:
			print("done")

			print("Serialising payload... ", end='')
			sys.stdout.flush()

		request_body    = serialize(post_data)
		request_headers = {'Content-type': 'application/json'}

		if self.config.verbose:
			print("done")

		###

		if self.config.verbose >= 2:
			print("Serialised payload:")
			payload.dump(human=True)

		###

		if self.config.pretend:
			print("Dry run, exiting...")
			return 0

		###

		if self.config.ssl:
			conn_class = httplib.HTTPSConnection
		else:
			conn_class = httplib.HTTPConnection

		conn = conn_class(self.config.server)
		try:
			if self.config.verbose:
				print("Sending report... ")
				sys.stdout.flush()

			conn.request( 'POST'
			            , url     = self.config.url
			            , headers = request_headers
			            , body    = request_body
			)

			response = conn.getresponse()
			print('Server response: %s (%s)' % \
					(response.status, response.reason))
			print(response.read())
		except httplib.HTTPException:
			sys.stderr.write('Something went wrong')
			return 1
		finally:
			if conn:
				conn.close()

def main(args, config=Config()):
	return Submit(config).run(args)

if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))
