# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# FlingStop
#   Motion d=20 x=2 y=19 r=0.17
#   Scroll d=12 x=0 y=12 r=0.48
#   Scroll d=12 x=0 y=12 r=0.47
#   Fling d=0 x=0 y=0 r=0.00

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    MotionValidator("<= 21"),
    ScrollValidator(">= 12"),
    ScrollValidator(">= 12"),
  ]
  fuzzy.unexpected = [
    FlingValidator(),
    FlingStopValidator(),
  ]
  return fuzzy.Check(gestures)
