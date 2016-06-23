# ---------------------------------------------
#
# The file test_io is part of the shs project.
# Copyright (c) 2016 Andrey Sobolev  
# License GNU GPL v.2
# See http://github.com/ansobolev/shs for details
#
# ---------------------------------------------
from unittest import TestCase
from shs.sio import read_fdf_file, read_fdf_lines, fdf_lines_to_dict
from shs.files.fdf import FDFFile
from shs.files.xv import XVFile
from shs.files.out import OUTFile


class TestReadFDFLines(TestCase):

    example = '../examples/fdf/CALC.fdf'

    def test_read_fdf_lines(self):

        lines = read_fdf_file(self.example)
        labels = [line[0] if line[0] != '%block' else line[1] for line in lines]
        self.assertIn('SystemName', labels)
        self.assertIn('WriteMDhistory', labels)
        self.assertIn('MD.TypeOfRun', labels)
        self.assertIn('LatticeConstant', labels)
        self.assertIn('LatticeVectors', labels)


class TestFDFLinesToDict(TestCase):
    example = '../examples/fdf/CALC.fdf'

    def setUp(self):
        self.lines = read_fdf_file(self.example)

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


class TestFDFFile(TestCase):
    example = '../examples/fdf/CALC.fdf'

    def setUp(self):
        self.fdf_dict = FDFFile(self.example).fdf_dict

    def test_fdf_dict(self):
        self.assertIsInstance(self.fdf_dict, dict)
        self.assertIn('SystemLabel', self.fdf_dict.keys())
        system_label = self.fdf_dict['SystemLabel']
        self.assertIsInstance(system_label, list)
        self.assertEqual(system_label[0], 1)
        self.assertEqual(system_label[1], 'FeC')
        self.assertIn('MD.TypeOfRun', self.fdf_dict.keys())
        type_of_run = self.fdf_dict['MD.TypeOfRun']
        self.assertEqual(type_of_run[1], 'NoseParrinelloRahman')
        self.assertIn('ChemicalSpeciesLabel', self.fdf_dict.keys())
        species = self.fdf_dict['ChemicalSpeciesLabel']
        self.assertIsInstance(species[1], list)
        self.assertEqual(len(species[1:]), 2)
        self.assertEqual(species[1], ['1', '6', 'C'])


class TestXVFile(TestCase):
    calc_dir = '../examples/FeCANI'

    def setUp(self):
        self.xv_file = XVFile(self.calc_dir)

    def test_xv_file(self):
        self.assertIn('FeC.XV', self.xv_file.name)
        vectors = self.xv_file.vectors
        self.assertAlmostEqual(vectors[0][0], 26.9191, delta=0.0001)
        i_type = self.xv_file.i_type
        self.assertEqual(len(i_type), 200)
        self.assertEqual(i_type[2], 1)
        z = self.xv_file.z
        self.assertEqual(z[1], 26)
        crd = self.xv_file.crd
        self.assertAlmostEqual(crd[2][0], -0.2977, delta=0.0001)


class TestOUTFile(TestCase):
    calc_dir = '../examples/FeCANI'

    def setUp(self):
        self.out_file = OUTFile(self.calc_dir, '*.0.output')

    def test_out_file(self):
        self.assertIn('FeC.XV', self.out_file.name)
        vectors = self.out_file.vectors
        self.assertAlmostEqual(vectors[0][0], 26.9191, delta=0.0001)
        i_type = self.out_file.i_type
        self.assertEqual(len(i_type), 200)
        self.assertEqual(i_type[2], 1)
        z = self.out_file.z
        self.assertEqual(z[1], 26)
        crd = self.out_file.crd
        self.assertAlmostEqual(crd[2][0], -0.2977, delta=0.0001)