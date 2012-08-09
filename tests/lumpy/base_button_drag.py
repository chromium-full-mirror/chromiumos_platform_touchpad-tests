# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# FlingStop
#   ButtonDown(1)
#   FlingStop
#   Motion d=448 x=396 y=130 r=1.81
#   FlingStop
#   Motion d=455 x=391 y=188 r=1.22
#   ButtonUp(1)

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    ButtonDownValidator(1),
    MotionValidator("900~200"),
    ButtonUpValidator(1)
  ]
  fuzzy.unexpected = [
    MotionValidator("<10"),
    FlingStopValidator("<10")
  ]
  return fuzzy.Check(gestures)
