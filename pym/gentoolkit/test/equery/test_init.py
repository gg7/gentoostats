import unittest
from test import test_support

from gentoolkit import equery

class TestEqueryInit(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_expand_module_name(self):
		# Test that module names are properly expanded
		name_map = {
			'b': 'belongs',
			'c': 'changes',
			'k': 'check',
			'd': 'depends',
			'g': 'depgraph',
			'f': 'files',
			'h': 'hasuse',
			'l': 'list_',
			'm': 'meta',
			's': 'size',
			'u': 'uses',
			'w': 'which'
		}
		self.failUnlessEqual(equery.NAME_MAP, name_map)
		for short_name, long_name in zip(name_map, name_map.values()):
			self.failUnlessEqual(equery.expand_module_name(short_name),
				long_name)
			self.failUnlessEqual(equery.expand_module_name(long_name),
				long_name)
		unused_keys = set(map(chr, range(0, 256))).difference(name_map.keys())
		for key in unused_keys:
			self.failUnlessRaises(KeyError, equery.expand_module_name, key)

	def test_format_timestamp(self):
		# Test that a certain timetamp produces the correct formatted string
		tstamp = 1257626685.6503389
		tstr = '2009-11-07 15:44:45'
		self.failUnlessEqual(equery.format_timestamp(tstamp), tstr)


def test_main():
	test_support.run_unittest(TestEqueryInit)


if __name__ == '__main__':
	test_main()