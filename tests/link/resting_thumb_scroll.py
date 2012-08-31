# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# FlingStop
#   FlingStop
#   Scroll d=262 x=0 y=262 r=1.68
#   Fling d=2290 x=0 y=2290 r=0.00

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    ScrollValidator("== 262 ~ 200"),
    # The important thing about this test is that a good fling occurs:
    FlingValidator("== 2290 ~ 2000"),
  ]
  fuzzy.unexpected = [
    FlingStopValidator("<10"),
  ]
  return fuzzy.Check(gestures)
