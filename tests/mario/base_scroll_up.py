# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# FlingStop
#   FlingStop
#   Motion d=49 x=1 y=49 r=4.47
#   Scroll d=1205 x=0 y=1205 r=2.08
#   Fling d=1092 x=0 y=1092 r=0.00

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    ScrollValidator("== 1205 ~ 1000"),
  ]
  fuzzy.unexpected = [
    MotionValidator("== 0 ~ 60"),
    FlingValidator(),
    FlingStopValidator("<10"),
  ]
  return fuzzy.Check(gestures)
