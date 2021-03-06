#!/usr/bin/env python
#
# Copyright 2011 Vikraman Choudhury <vikraman.choudhury@gmail.com>
# Copyright 2012 G. Gaydarov <ggaydarov@gmail.com>
#
# Distributed under the terms of the GNU General Public License v2 or later

from __future__ import print_function

import os
import platform

import portage
from _emerge.actions import relative_profile_path

class Environment(object):
	"""
	A class encapsulating all environment and portage variable providers
	"""

	def __init__(self):
		"""
		Initialize the class and portdir
		"""
		self.portdir = portage.settings['PORTDIR']

	def get_var(self, myvar):
		"""
		Return the value of a portage variable
		"""
		return portage.settings[myvar]

	def get_platform(self):
		"""
		Return host platform
		"""
		return platform.platform(aliased=1)

	def get_last_sync(self):
		"""
		Return portage tree last sync time
		"""
		last_sync = None

		try:
			last_sync = portage.grabfile(
				os.path.join(self.portdir, 'metadata', 'timestamp.chk')
			)
		except portage.exception.PortageException:
			pass

		if last_sync is None:
			return 'Unknown'

		return last_sync[0]

	def get_profile(self):
		"""
		Return selected portage profile
		"""
		profilever = None
		profile = portage.settings.profile_path
		if profile:
			profilever = relative_profile_path(self.portdir, profile)
			if profilever is None:
				try:
					for parent in portage.grabfile(
							os.path.join(profile, 'parent')
					):
						profilever = relative_profile_path(
								self.portdir, os.path.join(profile, parent)
						)

						if profilever is not None:
							break
				except portage.exception.PortageException:
					pass

				if profilever is None:
					try:
						profilever = '!' + os.readlink(profile)
					except (OSError):
						pass

		if profilever is None:
			profilever = 'Unknown'

		return profilever
