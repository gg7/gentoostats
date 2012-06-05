import portage
from portage._sets import SETPREFIX
from portage._sets import load_default_config

from gentoostats.dbapi import VARDB

class Packages(object):
    """
    A class encapsulating providers for reading installed packages from portage
    """

    def getInstalledCPs(self):
        """
        Read installed packages as category/packagename
        """
        return VARDB.cp_all()

    def getInstalledCPVs(self):
        """
        Read installed packages as category/packagename-version
        """
        return VARDB.cpv_all()

    def getSelectedSets(self):
        """
        Returns a dictionary with all of the selected sets expressed as Python
        lists. The dictionary will include at least the "selected" set, as well
        as all sets (recursively) listed under "selected".
        """

        eroot    = portage.settings["EROOT"]
        trees    = portage.db[eroot]
        vartree  = trees["vartree"]
        settings = vartree.settings

        setconfig = load_default_config(settings=settings, trees=trees)
        setconfig._parse()

        # selected sets (includes at least the 'selected' set):
        selectedSets = dict()

        def includeSet(s):
            if s in selectedSets:
                return

            if s not in setconfig.psets:
                raise Exception("Non existent set: " + s)

            atoms    = setconfig.psets[s].getAtoms()
            nonatoms = setconfig.psets[s].getNonAtoms()

            # atoms and nonatoms for each set:
            selectedSets[s] = list(atoms.union(nonatoms))
            # (use a list so that it's JSON serializable by default)

            # recursevely add any sets included by the current set:
            subsets = [x[len(SETPREFIX):] for x in nonatoms if x.startswith(SETPREFIX)]
            map(includeSet, subsets)

        includeSet("selected")
        return selectedSets
