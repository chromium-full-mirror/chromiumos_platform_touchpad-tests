# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# FlingStop
#   FlingStop
#   ButtonDown(4)
#   ButtonUp(4)
#   FlingStop
#   Motion d=2 x=2 y=0 r=0.00
#   Motion d=1 x=1 y=0 r=0.00
#   Motion d=89 x=81 y=26 r=0.71
#   FlingStop
#   FlingStop
#   FlingStop
#   ButtonDown(4)
#   Motion d=2 x=2 y=0 r=0.00
#   ButtonUp(4)
#   FlingStop
#   FlingStop
#   Motion d=16 x=12 y=4 r=0.00
#   FlingStop
#   ButtonDown(4)
#   ButtonUp(4)
#   Motion d=92 x=78 y=34 r=0.52
#   FlingStop
#   FlingStop
#   ButtonDown(4)
#   Motion d=2 x=0 y=2 r=0.00
#   ButtonUp(4)
#   Motion d=17 x=16 y=3 r=0.10
#   FlingStop

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    ButtonDownValidator(4),
    ButtonUpValidator(4),
    ButtonDownValidator(4),
    ButtonUpValidator(4),
    ButtonDownValidator(4),
    ButtonUpValidator(4),
    ButtonDownValidator(4),
    ButtonUpValidator(4),
  ]
  fuzzy.unexpected = [
    MotionValidator("<300", merge=True),
    FlingStopValidator("<20"),
  ]
  return fuzzy.Check(gestures)
