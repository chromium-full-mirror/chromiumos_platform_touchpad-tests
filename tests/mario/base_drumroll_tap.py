# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# FlingStop
#   Motion d=1 x=0 y=1 r=0.00
#   FlingStop
#   ButtonDown(1)
#   ButtonUp(1)
#   ButtonDown(1)
#   ButtonUp(1)
#   FlingStop
#   FlingStop
#   ButtonDown(1)
#   ButtonUp(1)
#   ButtonDown(1)
#   ButtonUp(1)
#   FlingStop
#   ButtonDown(1)
#   ButtonUp(1)
#   ButtonDown(1)
#   ButtonUp(1)
#   ButtonDown(1)
#   ButtonUp(1)
#   FlingStop
#   ButtonDown(1)
#   ButtonUp(1)
#   FlingStop
#   FlingStop
#   ButtonDown(1)
#   ButtonUp(1)
#   FlingStop
#   FlingStop
#   ButtonDown(1)
#   ButtonUp(1)
#   ButtonDown(1)
#   ButtonUp(1)
#   FlingStop
#   FlingStop
#   ButtonDown(1)
#   ButtonUp(1)
#   FlingStop
#   Motion d=3 x=3 y=0 r=0.00
#   FlingStop
#   FlingStop
#   ButtonDown(1)
#   ButtonUp(1)
#   ButtonDown(1)
#   ButtonUp(1)
#   FlingStop
#   ButtonDown(1)
#   ButtonUp(1)
#   ButtonDown(1)
#   ButtonUp(1)
#   FlingStop
#   ButtonDown(1)
#   ButtonUp(1)
#   ButtonDown(1)
#   ButtonUp(1)
#   FlingStop
#   ButtonDown(1)
#   ButtonUp(1)
#   ButtonDown(1)
#   ButtonUp(1)
#   FlingStop
#   ButtonDown(1)
#   ButtonUp(1)
#   ButtonDown(1)
#   ButtonUp(1)
#   FlingStop
#   ButtonDown(1)
#   ButtonUp(1)
#   FlingStop
#   ButtonDown(1)
#   ButtonUp(1)
#   ButtonDown(1)
#   ButtonUp(1)
#   FlingStop
#   ButtonDown(1)
#   ButtonUp(1)
#   ButtonDown(1)
#   ButtonUp(1)

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
  ]
  fuzzy.unexpected = [
    MotionValidator("== 0 ~ 10"),
    FlingStopValidator("<30"),
  ]
  return fuzzy.Check(gestures)
