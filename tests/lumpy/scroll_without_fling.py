# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
#   FlingStop
#   Scroll d=343 x=0 y=343 r=7.65
#   Fling d=0 x=0 y=0 r=0.00

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    ScrollValidator("== 343 ~ 343"),
    # Make sure there is no *real* fling.  Every time a scroll ends there
    # should be a fling event, but in this case it's velocity must be 0
    FlingValidator("0"),
  ]
  fuzzy.unexpected = [
    FlingStopValidator("<10"),
  ]
  return fuzzy.Check(gestures)
