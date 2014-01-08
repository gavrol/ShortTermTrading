# -*- coding: utf-8 -*-
"""
Created on Tue Dec 03 15:55:36 2013

@author: olenag
"""

import os

for fn in os.listdir("."):
    if fn.find("_cost0_") > 0:
        newfn = fn.replace("_cost0_","_")
        os.rename(fn,newfn)

#[os.rename(f, f.replace('_', '-')) for f in os.listdir('.') if not f.startswith('.')]