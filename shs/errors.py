#! /usr/bin/env python
# -*- coding : utf8 -*-

''' Container for various errors and exceptions
'''

class Error(Exception):
    pass

class NotImplementedError(Error):
    pass

class UnsupportedError(Error):
    pass

class FileError(Error):
    pass

class AtomTypeError(Error):
    pass