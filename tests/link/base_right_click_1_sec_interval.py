# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# FlingStop
#   Motion d=11 x=8 y=3 r=0.00
#   Motion d=2 x=1 y=1 r=0.00
#   Motion d=1 x=1 y=0 r=0.00
#   FlingStop
#   ButtonDown(4)
#   Motion d=5 x=0 y=5 r=0.00
#   ButtonUp(4)

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    ButtonDownValidator(4),
    ButtonUpValidator(4),
  ]
  fuzzy.unexpected = [
    MotionValidator("== 0 ~ 30", merge=True),
    FlingStopValidator("<10"),
  ]
  return fuzzy.Check(gestures)
