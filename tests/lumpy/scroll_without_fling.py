# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# FlingStop
#   Scroll d=343 x=0 y=343 r=7.65

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    ScrollValidator("== 343 ~ 343"),
    # Make sure there is no fling
  ]
  fuzzy.unexpected = [
    FlingStopValidator("<10"),
  ]
  return fuzzy.Check(gestures)
