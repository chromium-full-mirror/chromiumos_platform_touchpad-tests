# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# FlingStop
#   Motion d=11 x=11 y=2 r=0.00
#   Scroll d=4432 x=4432 y=0 r=42.78
#   Fling d=8620 x=8620 y=0 r=0.00

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    ScrollValidator("== 4432 ~ 1000"),
  ]
  fuzzy.unexpected = [
    MotionValidator("== 0 ~ 60"),
    FlingValidator(),
    FlingStopValidator("<10"),
  ]
  return fuzzy.Check(gestures)
