# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# FlingStop
#   Scroll d=1438 x=0 y=1438 r=2.58
#   Fling d=4656 x=0 y=4656 r=0.00

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    ScrollValidator("== 1458 ~ 1000"),
  ]
  fuzzy.unexpected = [
    MotionValidator("== 0 ~ 60"),
    FlingValidator(),
    FlingStopValidator("<10"),
  ]
  return fuzzy.Check(gestures)
