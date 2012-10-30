# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# FlingStop
#   FlingStop
#   Motion d=14 x=1 y=13 r=0.45
#   Scroll d=420 x=13 y=409 r=0.98

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    ScrollValidator("== 420 ~ 400"),
  ]
  fuzzy.unexpected = [
    MotionValidator("< 10 ~ 30"),
    FlingStopValidator("<10"),
  ]
  return fuzzy.Check(gestures)
