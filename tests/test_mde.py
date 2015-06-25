__author__ = 'andrey'

import unittest

from shs.calc import SiestaCalc
from shs.data.per_evol import MDEData

class TestMDE(unittest.TestCase):

    def setUp(self):
        calc_dir = '../examples/FeCANI'
        self.calc = SiestaCalc(calc_dir, 'ani', [0,])
        self.calc.get_data('mdedata')

    def test_mde_data(self):
        # check if mdedata added to calc.data dict
        self.assertIn('mdedata', self.calc.data, "calc.data doesn't have mde data in it")
        self.assertIsInstance(self.calc.data['mdedata'], MDEData, "calc.data['mdedata'] is not the MDEData instance")
        self.assertIn("e_ks", self.calc.data["mdedata"].y_titles)


if __name__ == '__main__':
    unittest.main()
