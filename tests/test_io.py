# ---------------------------------------------
#
# The file test_io is part of the shs project.
# Copyright (c) 2016 Andrey Sobolev  
# License GNU GPL v.2
# See http://github.com/ansobolev/shs for details
#
# ---------------------------------------------
from unittest import TestCase
from shs.sio import read_fdf_lines, fdf_lines_to_dict


class TestReadFDFLines(TestCase):

    example = '../examples/fdf/CALC.fdf'

    def test_read_fdf_lines(self):

        lines = read_fdf_lines(self.example)
        labels = [line[0] if line[0] != '%block' else line[1] for line in lines]
        self.assertIn('SystemName', labels)
        self.assertIn('WriteMDhistory', labels)
        self.assertIn('MD.TypeOfRun', labels)
        self.assertIn('LatticeConstant', labels)
        self.assertIn('LatticeVectors', labels)


class TestFDFLinesToDict(TestCase):
    example = '../examples/fdf/CALC.fdf'

    def setUp(self):
        self.lines = read_fdf_lines(self.example)

    def test_fdf_lines_to_dict(self):
        fdf_dict = fdf_lines_to_dict(self.lines)
        self.assertIsInstance(fdf_dict, dict)
        self.assertIn('SystemLabel', fdf_dict.keys())
        system_label = fdf_dict['SystemLabel']
        self.assertIsInstance(system_label, list)
        self.assertEqual(system_label[0], 1)
        self.assertEqual(system_label[1], 'FeC')
        self.assertIn('MD.TypeOfRun', fdf_dict.keys())
        type_of_run = fdf_dict['MD.TypeOfRun']
        self.assertEqual(type_of_run[1], 'NoseParrinelloRahman')
        self.assertIn('ChemicalSpeciesLabel', fdf_dict.keys())
        species = fdf_dict['ChemicalSpeciesLabel']
        self.assertIsInstance(species[1], list)
        self.assertEqual(len(species[1:]), 2)
        self.assertEqual(species[1], ['1', '6', 'C'])



