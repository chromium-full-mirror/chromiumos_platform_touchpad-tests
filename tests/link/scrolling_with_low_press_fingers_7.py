# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# FlingStop
#   Motion d=9 x=0 y=9 r=0.40
#   Scroll d=27 x=0 y=27 r=0.36
#   Fling d=0 x=0 y=0 r=0.00

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    MotionValidator("<= 10"),
    ScrollValidator(">= 27"),
  ]
  fuzzy.unexpected = [
    FlingValidator(),
    FlingStopValidator(),
  ]
  return fuzzy.Check(gestures)
