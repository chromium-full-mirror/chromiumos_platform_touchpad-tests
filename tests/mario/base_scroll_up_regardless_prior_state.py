# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# FlingStop
#   Motion d=3788 x=2990 y=1646 r=3.33
#   Scroll d=1163 x=438 y=842 r=5.66
#   Fling d=1827 x=1827 y=0 r=0.00

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    MotionValidator("> 1000"),
    ScrollValidator("> 1000 ~ 500"),
    FlingValidator("> 1000 ~ 500"),
  ]
  fuzzy.unexpected = [
    FlingStopValidator("<10"),
    MotionValidator("< 10 ~ 20"),
  ]
  return fuzzy.Check(gestures)
