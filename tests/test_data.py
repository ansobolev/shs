__author__ = 'andrey'

import unittest
from shs.data import Data

class TestDataClass(unittest.TestCase):

    def test_data_class(self):
        DataClass = Data()
        names = DataClass.names()
        self.assertIn("mdedata", names)


if __name__ == '__main__':
    unittest.main()
