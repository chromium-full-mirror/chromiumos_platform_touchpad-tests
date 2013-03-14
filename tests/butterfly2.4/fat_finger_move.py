# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# Motion d=114 x=106 y=24 r=1.37
#   FlingStop

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    MotionValidator("== 531 ~ 50", merge=True),
  ]
  fuzzy.unexpected = [
    FlingStopValidator("<10"),
  ]
  return fuzzy.Check(gestures)
