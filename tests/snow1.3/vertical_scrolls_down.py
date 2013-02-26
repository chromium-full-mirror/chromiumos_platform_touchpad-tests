# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
#   FlingStop
#   Scroll d=1433 x=0 y=1433 r=44.77
#   Fling d=6601 x=0 y=6601 r=0.00
#   FlingStop
#   Scroll d=1153 x=0 y=1153 r=24.63
#   Fling d=622 x=0 y=622 r=0.00
#   FlingStop
#   Scroll d=258 x=7 y=252 r=5.92
#   Fling d=0 x=0 y=0 r=0.00
#   FlingStop
#   Scroll d=952 x=0 y=952 r=15.32
#   Fling d=3371 x=0 y=3371 r=0.00

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    ScrollValidator("== 1433 ~ 1000"),
    FlingValidator("== 6601 ~ 6000"),
    ScrollValidator("== 1153 ~ 1000"),
    FlingValidator("== 622 ~ 600"),
    ScrollValidator("== 258 ~ 200"),
    FlingValidator("0"),
    ScrollValidator("== 952 ~ 900"),
    FlingValidator("== 3371 ~ 3000"),
  ]
  fuzzy.unexpected = [
    FlingStopValidator("<10"),
  ]
  return fuzzy.Check(gestures)
