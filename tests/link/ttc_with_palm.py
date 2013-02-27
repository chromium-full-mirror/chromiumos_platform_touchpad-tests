# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# FlingStop
#   FlingStop
#   Fling d=212 x=0 y=212 r=0.00
#   FlingStop
#   FlingStop
#   FlingStop
#   Motion d=78 x=75 y=19 r=0.37
#   FlingStop
#   Motion d=58 x=30 y=47 r=0.28
#   FlingStop
#   FlingStop
#   FlingStop
#   Motion d=14 x=6 y=10 r=0.02
#   FlingStop
#   Motion d=1 x=0 y=0 r=0.02

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  # We just want to make sure two clicks occur
  fuzzy.expected = [
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
  ]
  fuzzy.unexpected = [
    MotionValidator(merge=True),
    FlingStopValidator("<20"),
    ScrollValidator(merge=True),
    FlingValidator(),
  ]
  return fuzzy.Check(gestures)
