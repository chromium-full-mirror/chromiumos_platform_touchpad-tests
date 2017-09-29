# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# FlingStop
#   Scroll d=4231 x=4231 y=0 r=39.23
#   Fling d=13271 x=13271 y=0 r=0.00

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    ScrollValidator("== 3525.8 ~ 833.3"),
  ]
  fuzzy.unexpected = [
    FlingValidator(),
    FlingStopValidator("<10"),
  ]
  return fuzzy.Check(gestures)
