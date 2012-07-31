#!/usr/bin/env python
#
# Copyright 2011 Vikraman Choudhury <vikraman.choudhury@gmail.com>
# Copyright 2012 G. Gaydarov <ggaydarov@gmail.com>
#
# Distributed under the terms of the GNU General Public License v2 or later

from __future__ import print_function

DEFAULT_CONFIG = dict(
	quiet   = 0,
	verbose = 1,
)

class Config(object):
	def __init__(self):
		self.settings = dict(DEFAULT_CONFIG)

	@staticmethod
	def get_settings_dict(new_settings):
		if isinstance(new_settings, Config):
			new_settings = new_settings.settings
		elif not isinstance(new_settings, dict):
			raise ValueError("Bad type %s (expected Config/dict)" % type(new_settings))

		return new_settings

	def hard_update(self, new_settings):
		new_settings = Config.get_settings_dict(new_settings)
		self.settings.update(new_settings)

	def update(self, new_settings):
		new_settings = Config.get_settings_dict(new_settings)
		for k, v in new_settings.items():
			if not v is None:
				self.settings[k] = v

	def soft_update(self, new_settings):
		new_settings = Config.get_settings_dict(new_settings)
		for k, v in new_settings.items():
			if not k in self.settings:
				self.settings[k] = v

	def is_detault(self, name):
		# TODO: what if both are None?

		try:
			return self.settings[name] == DEFAULT_CONFIG[name]
		except KeyError:
			return False

	def __getattr__(self, attr):
		if attr in self.settings:
			return self.settings[attr]
		else:
			# raise AttributeError(
			# 	"%r object has no attribute %r" % (type(self).__name__, attr)
			# )

			return None
