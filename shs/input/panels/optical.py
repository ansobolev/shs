# ---------------------------------------------
#
# The file optical.py is part of the shs project.  
# Copyright (c) 2015 Andrey Sobolev  
# License GNU GPL v.2
# See http://github.com/ansobolev/shs for details
#
# ---------------------------------------------

import wx
from shs.input import fdf_options

__title__ = "Optical"
__page__ = 4


class OpticalCalculation(fdf_options.BooleanLine):
    label = 'Optical calculation'
    fdf_text = 'OpticalCalculation'
    optional = True
    priority = 10

    def __init__(self, parent):
        super(OpticalCalculation, self).__init__(parent)
        self.bindings = [(self.CB,
                          wx.EVT_CHECKBOX,
                          self.show_optical_options),
                         (self.switch,
                          wx.EVT_CHECKBOX,
                          self.show_optical_options)
                         ]

    def show_optical_options(self, event,
                             OpticalEnergyMinimum,
                             OpticalEnergyMaximum,
                             OpticalBroaden,
                             OpticalScissor):
        OpticalEnergyMinimum.Show(self.IsEnabled() and self.CB.IsChecked())
        OpticalEnergyMaximum.Show(self.IsEnabled() and self.CB.IsChecked())
        OpticalBroaden.Show(self.IsEnabled() and self.CB.IsChecked())
        OpticalScissor.Show(self.IsEnabled() and self.CB.IsChecked())
        event.Skip()


class OpticalEnergyMinimum(fdf_options.MeasuredLine):
    label = 'Energy minimum'
    fdf_text = 'Optical.EnergyMinimum'
    optional = True
    value = 1.
    digits = 1
    increment = 1.
    units = ['eV', 'Ry']
    priority = 20
    hidden = True


class OpticalEnergyMaximum(fdf_options.MeasuredLine):
    label = 'Energy maximum'
    fdf_text = 'Optical.EnergyMaximum'
    optional = True
    value = 1.
    digits = 1
    increment = 1.
    units = ['eV', 'Ry']
    priority = 30
    hidden = True


class OpticalBroaden(fdf_options.MeasuredLine):
    label = 'Broaden frequencies by'
    fdf_text = 'Optical.Broaden'
    optional = True
    value = 0.02
    digits = 2
    increment = 0.01
    units = ['eV', 'Ry']
    priority = 40
    hidden = True


class OpticalScissor(fdf_options.MeasuredLine):
    label = 'Scissor operator'
    fdf_text = 'Optical.Scissor'
    optional = True
    value = 0.
    digits = 2
    increment = 0.01
    units = ['eV', 'Ry']
    priority = 50
    hidden = True
