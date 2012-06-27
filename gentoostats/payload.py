from __future__ import print_function

import sys
import pprint

try:
	import ConfigParser
except ImportError:
	import configparser as ConfigParser

from gentoostats.environment import Environment
from gentoostats.packages import Packages
from gentoostats.metadata import Metadata

USE_FLAG_TYPES = ['IUSE', 'PKGUSE', 'USE']

class Payload(object):
	"""
	A class that encapsulates payload operations.
	"""

	def __init__(self, configfile):
		"""
		Initialize the payload according to the config file.
		"""
		self.config = ConfigParser.ConfigParser()
		if len(self.config.read(configfile)) == 0:
			sys.stderr.write('Cannot read ' + configfile)
			sys.exit(1)

		self.payload = dict()
		self.payload['PROTOCOL'] = 2
		self.generate_payload()

	def is_masked(self, section, item):
		"""
		Check the mask status of a payload entry.
		"""
		try:
			return not self.config.getboolean(section, item)
		except ConfigParser.NoOptionError:
			return False
		except (ConfigParser.NoSectionError, ValueError):
			sys.stderr.write('Malformed payload config')
			sys.exit(1)

	def any_one_is_enabled(self, config_section, keys):
		"""
		Check if any one of the keys in the given section is enabled (not
		masked).
		"""
		for k in keys:
			if not self.is_masked(config_section, k):
				return True

		return False

	def set_data(self, the_dict, config_section, key, generator, *generator_args):
		"""
		Set the key 'key' in the dictionary 'the_dict' to the result of
		'generator(generator_args) if config_section/key is not masked.
		"""
		if not self.is_masked(config_section, key):
			the_dict[key] = generator(*generator_args)

	def analyse_packages(self):
		"""
		Generate information about all the installed packages.
		"""
		section = 'PACKAGES'
		self.payload['PACKAGES'] = dict()

		for cpv in Packages.get_installed_CPVs():
			metadata = Metadata(cpv)
			package_info = dict()

			self.set_data(package_info, section, 'REPO',       metadata.get_repo_name)
			self.set_data(package_info, section, 'SIZE',       metadata.get_size)
			self.set_data(package_info, section, 'KEYWORD',    metadata.get_keyword)
			self.set_data(package_info, section, 'BUILD_TIME', metadata.get_build_time)

			if self.any_one_is_enabled(section, USE_FLAG_TYPES):
				# TODO: make this lazier
				use_flags = metadata.get_use_flag_information()

				for key in USE_FLAG_TYPES:
					self.set_data(package_info, section, key, lambda: use_flags[key])

			self.payload['PACKAGES'][cpv] = package_info

	def generate_payload(self):
		"""
		Generate self.payload.
		"""
		env = Environment()

		self.set_data(self.payload, 'ENV', 'PLATFORM', env.get_platform)
		self.set_data(self.payload, 'ENV', 'LASTSYNC', env.get_last_sync)
		self.set_data(self.payload, 'ENV', 'PROFILE', env.get_profile)

		for var in ['ARCH', 'CHOST', 'CFLAGS', 'CXXFLAGS', 'FFLAGS', 'SYNC',
				'LDFLAGS', 'MAKEOPTS', 'EMERGE_DEFAULT_OPTS',
				'PORTAGE_RSYNC_EXTRA_OPTS', 'ACCEPT_LICENSE']:
			self.set_data(self.payload, 'ENV', var, env.get_var, var)

		for var in ['ACCEPT_KEYWORDS', 'LANG', 'GENTOO_MIRRORS', 'FEATURES',
				'USE']:
			self.set_data(self.payload, 'ENV', var, lambda x: env.get_var(x).split(), var)

		# Only bother calling get_installed_CPVs() if any of the following is
		# enabled:
		if self.any_one_is_enabled('PACKAGES',
				['BUILD_TIME', 'KEYWORD', 'REPO',
				'SIZE', 'IUSE', 'PKGUSE', 'USE']):
			self.analyse_packages()

		self.set_data(self.payload, 'PACKAGES', 'SELECTEDSETS', Packages.get_selected_sets)

	def get(self):
		"""
		Return currently read payload.
		"""
		return self.payload

	def dump(self, human=False):
		"""
		Dump payload.
		"""
		if human:
			pprint.pprint(self.payload)
		else:
			print(self.payload)
