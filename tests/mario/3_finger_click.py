# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# FlingStop
#   ButtonDown(4)
#   ButtonUp(4)
#   Scroll d=150 x=0 y=150 r=0.00
#   ButtonDown(1)
#   ButtonUp(1)
#   Fling d=0 x=0 y=0 r=0.00
#   Motion d=435 x=435 y=19 r=0.00

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    ButtonDownValidator(2),
    ButtonUpValidator(2),
    ButtonDownValidator(2),
    ButtonUpValidator(2),
  ]
  fuzzy.unexpected = [
    MotionValidator("<10"),
    FlingStopValidator("<10"),
  ]
  return fuzzy.Check(gestures)
