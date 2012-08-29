# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# ButtonDown(4)
#   ButtonUp(4)
#   FlingStop
#   Scroll d=97 x=97 y=0 r=0.00
#   Fling d=1145 x=1145 y=0 r=0.00
#   ButtonDown(4)
#   ButtonUp(4)
#   FlingStop
#   ButtonDown(4)
#   ButtonUp(4)
#   ButtonDown(4)
#   ButtonUp(4)

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
    FlingValidator(),
    ScrollValidator("== 100 ~ 60"),
    FlingStopValidator("<10"),
  ]
  return fuzzy.Check(gestures)
