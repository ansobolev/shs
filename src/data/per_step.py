#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#

from abstract import PerStepData

class MDEData(PerStepData):
    __is_function = True
    
    def __init__(self, calc):
        pass
    
    def short_description(self):
        return "Run evolution (MDE)"
