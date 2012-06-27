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

class Payload(object):
	"""
	A class that encapsulates payload operations
	"""

	def __init__(self, configfile):
		"""
		Initialize the payload using the config file
		"""
		self.config = ConfigParser.ConfigParser()
		if len(self.config.read(configfile)) == 0:
			sys.stderr.write('Cannot read ' + configfile)
			sys.exit(1)

		self.payload = dict()
		self.payload['PROTOCOL'] = 2
		self.update()

	def __masked(self, section, item):
		"""
		Check the mask status of payload
		"""
		try:
			return not self.config.getboolean(section, item)
		except ConfigParser.NoOptionError:
			return False
		except (ConfigParser.NoSectionError, ValueError):
			sys.stderr.write('Malformed payload config')
			sys.exit(1)

	def update(self):
		"""
		Read and update the payload
		"""
		env = Environment()
		self.payload['PLATFORM'] = 'Unknown' if self.__masked('ENV', 'PLATFORM') else env.get_platform()
		self.payload['LASTSYNC'] = 'Unknown' if self.__masked('ENV', 'LASTSYNC') else env.get_last_sync()
		self.payload['PROFILE']  = 'Unknown' if self.__masked('ENV', 'PROFILE')  else env.get_profile()

		for var in ['ARCH', 'CHOST', 'CFLAGS', 'CXXFLAGS', 'FFLAGS', 'SYNC', \
				'LDFLAGS', 'MAKEOPTS', 'EMERGE_DEFAULT_OPTS', \
				'PORTAGE_RSYNC_EXTRA_OPTS', 'ACCEPT_LICENSE']:
			self.payload[var] = None if self.__masked('ENV', var) else env.get_var(var)

		for var in ['ACCEPT_KEYWORDS', 'LANG', 'GENTOO_MIRRORS', 'FEATURES', \
				'USE']:
			self.payload[var] = [] if self.__masked('ENV', var) else env.get_var(var).split()

		self.payload['PACKAGES'] = dict()
		for cpv in Packages().get_installed_CPVs():
			m = Metadata(cpv)

			p = dict()
			p['REPO'] = None if self.__masked('PACKAGES', 'REPO') else m.get_repo_name()
			p['SIZE'] = None if self.__masked('PACKAGES', 'SIZE') else m.get_size()
			p['KEYWORD'] = None if self.__masked('PACKAGES', 'KEYWORD') else m.get_keyword()
			p['BUILD_TIME'] = None if self.__masked('PACKAGES', 'BUILD_TIME') else m.get_build_time()

			_useflags = m.get_use_flag_information()
			p['USE'] = dict()
			p['USE']['IUSE'] = [] if self.__masked('PACKAGES', 'USE_IUSE') else _useflags['IUSE']
			p['USE']['PKGUSE'] = [] if self.__masked('PACKAGES', 'USE_PKGUSE') else _useflags['PKGUSE']
			p['USE']['FINAL'] = [] if self.__masked('PACKAGES', 'USE_FINAL') else _useflags['FINAL']

			self.payload['PACKAGES'][cpv] = p

		self.payload['SELECTEDSETS'] = 'Unknown' if self.__masked('PACKAGES', 'SELECTEDSETS') else Packages().get_selected_sets()

	def get(self):
		"""
		Return currently read payload
		"""
		return self.payload

	def dump(self, human=False):
		"""
		Dump payload
		"""
		if human:
			pprint.pprint(self.payload)
		else:
			print(self.payload)
