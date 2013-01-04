# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# FlingStop
#   Motion d=2 x=0 y=1 r=0.00
#   Motion d=2 x=2 y=0 r=0.00
#   Motion d=10 x=7 y=4 r=0.03
#   Motion d=11 x=2 y=10 r=0.04
#   Motion d=28 x=14 y=14 r=0.02
#   Motion d=8 x=5 y=3 r=0.03
#   Motion d=2 x=1 y=0 r=0.00
#   Motion d=7 x=5 y=2 r=0.03
#   Motion d=2 x=1 y=0 r=0.00
#   Motion d=6 x=4 y=2 r=0.03
#   Motion d=9 x=6 y=3 r=0.03
#   Motion d=7 x=4 y=3 r=0.05
#   Motion d=34 x=7 y=28 r=0.03
#   Motion d=4 x=3 y=0 r=0.00

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    # This is from a stationary 1F. Make sure we don't see that many
    # movements as generated from the original setting.
    MotionValidator("== 3 ~ 5", merge=True),
  ]
  fuzzy.unexpected = [
    FlingStopValidator("<10"),
  ]
  return fuzzy.Check(gestures)
