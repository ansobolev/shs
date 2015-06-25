__author__ = 'andrey'

import unittest
from shs.calc import SiestaCalc
from shs.data import Data
from shs.data.per_evol import MDEData, DOSData
from shs.data.per_type import VAFData, MSDData


class TestDataClass(unittest.TestCase):

    def test_data_class(self):
        DataClass = Data()
        names = DataClass.names()
        self.assertIn("mdedata", names)
        self.assertIn("dosdata", names)


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


class TestPDOS(unittest.TestCase):

    name = "dosdata"
    data_class = DOSData

    def setUp(self):
        calc_dir = '../examples/FeCANI'
        self.calc = SiestaCalc(calc_dir, 'ani', [0,])
        self.calc.get_data(self.name)

    def test_dos_data(self):
        self.assertIn(self.name, self.calc.data, "calc.data doesn't have %s in it" % (self.name,))
        self.assertIsInstance(self.calc.data[self.name], self.data_class,
                              "calc.data[%s] is not the %s instance" % (self.name, self.data_class.__name__))
        self.assertIn("Fe-s_up", self.calc.data[self.name].y_titles)


class TestVAF(unittest.TestCase):

    name = "vafdata"
    data_class = VAFData

    def setUp(self):
        calc_dir = '../examples/FeCANI'
        self.calc = SiestaCalc(calc_dir, 'ani', range(-10, 0, 1))
        self.calc.get_data(self.name)

    def test_vaf_data(self):
        self.assertIn(self.name, self.calc.data, "calc.data doesn't have %s in it" % (self.name,))
        self.assertIsInstance(self.calc.data[self.name], self.data_class,
                              "calc.data[%s] is not the %s instance" % (self.name, self.data_class.__name__))
        self.assertIn("Fe", self.calc.data[self.name].y_titles)


class TestMSD(unittest.TestCase):

    name = "msddata"
    data_class = MSDData

    def setUp(self):
        calc_dir = '../examples/FeCANI'
        self.calc = SiestaCalc(calc_dir, 'ani', range(-10, 0, 1))
        self.calc.get_data(self.name)

    def test_vaf_data(self):
        self.assertIn(self.name, self.calc.data, "calc.data doesn't have %s in it" % (self.name,))
        self.assertIsInstance(self.calc.data[self.name], self.data_class,
                              "calc.data[%s] is not the %s instance" % (self.name, self.data_class.__name__))
        self.assertIn("Fe", self.calc.data[self.name].y_titles)


if __name__ == '__main__':
    unittest.main()
