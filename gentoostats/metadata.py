import portage
import gentoolkit.flag
from gentoolkit.dbapi import VARDB
from gentoolkit.enalyze.lib import KeywordAnalyser

class Metadata(object):
	"""
	A class encapsulating all package metadata
	"""

	def __init__(self, cpv):
		"""
		Initialize the class with the cpv. All metadata are read from portage
		"""
		self.repo, self.build_time, self.size = \
				VARDB.aux_get(cpv, ['repository', 'BUILD_TIME', 'SIZE'])

		arch = portage.settings['ARCH']
		accept_keywords = portage.settings['ACCEPT_KEYWORDS'].split()
		ka = KeywordAnalyser(arch=arch, accept_keywords=accept_keywords)
		self.keyword = ka.get_inst_keyword_cpv(cpv)

		self.default_iuse, self.final_use = \
				gentoolkit.flag.get_flags(cpv, final_setting=True)

		self.pkguse = gentoolkit.flag.get_installed_use(cpv, use="PKGUSE")

	def getUseFlagInformation(self):
		"""
		Returns [ebuild's IUSE], [user's PKGUSE], and [final USE].
		"""

		return { 'IUSE':   self.default_iuse
		       , 'PKGUSE': self.pkguse
		       , 'FINAL':  self.final_use
		       }

	def getKeyword(self):
		"""
		Return keyword used to install package
		"""
		return self.keyword

	def getRepoName(self):
		"""
		Return the repository the package was installed from
		"""
		if self.repo:
			return self.repo
		return 'Unknown'

	def getBuildTime(self):
		"""
		Return the time package was built
		"""
		return self.build_time

	def getSize(self):
		"""
		Return the size of the installed package
		"""
		return self.size
