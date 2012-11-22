# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# Motion d=70 x=45 y=31 r=0.08
#   FlingStop
#   Motion d=4 x=3 y=1 r=0.00
#   Motion d=10 x=6 y=4 r=0.00
#   Motion d=5 x=2 y=3 r=0.00
#   Motion d=1 x=0 y=1 r=0.00
#   Motion d=2 x=1 y=1 r=0.00

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
  ]
  fuzzy.unexpected = [
    MotionValidator("== 0 ~ 200", merge=True),
    FlingStopValidator("<10"),
  ]
  return fuzzy.Check(gestures)
