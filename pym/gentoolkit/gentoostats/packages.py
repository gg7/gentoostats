#!/usr/bin/env python
#
# Copyright 2011 Vikraman Choudhury <vikraman.choudhury@gmail.com>
# Copyright 2012 G. Gaydarov <ggaydarov@gmail.com>
#
# Distributed under the terms of the GNU General Public License v2 or later

from __future__ import print_function

import portage
from portage._sets import SETPREFIX
from portage._sets import load_default_config
from gentoolkit.dbapi import VARDB

class Packages(object):
	"""
	A class encapsulating providers for reading installed packages from portage.
	"""

	@staticmethod
	def get_installed_CPs():
		"""
		Read installed packages as category/packagename.
		"""
		return VARDB.cp_all()

	@staticmethod
	def get_installed_CPVs():
		"""
		Read installed packages as category/packagename-version.
		"""
		return VARDB.cpv_all()

	@staticmethod
	def get_set(set_name='world', recursive=True):
		"""
		Returns a dictionary containing the given set and all of its
		atoms/subsets. If recursive is True, this is done recursively.
		"""

		eroot    = portage.settings["EROOT"]
		trees    = portage.db[eroot]
		vartree  = trees["vartree"]
		settings = vartree.settings

		setconfig = load_default_config(settings=settings, trees=trees)
		setconfig._parse()

		# selected sets (includes at least the 'selected' set):
		selected_sets = dict()

		def _include_set(s, recursive=True):
			if s in selected_sets:
				return

			if s not in setconfig.psets:
				raise Exception("Non existent set: " + s)

			atoms    = setconfig.psets[s].getAtoms()
			nonatoms = setconfig.psets[s].getNonAtoms()

			# atoms and nonatoms for each set:
			selected_sets[s] = list(atoms.union(nonatoms))
			# (use a list so that it's JSON serializable by default)

			# recursevely add any sets included by the current set:
			if recursive:
				subsets = [x[len(SETPREFIX):] for x in nonatoms if x.startswith(SETPREFIX)]
				map(_include_set, subsets)

		_include_set(set_name, recursive=recursive)
		return selected_sets
