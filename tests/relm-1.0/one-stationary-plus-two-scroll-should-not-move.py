# Copyright 2017 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# Two finger scroll with stationary finger should only scroll, was moving

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    ScrollValidator(),
    FlingValidator(),
    ScrollValidator(),
    ScrollValidator(),
  ]
  fuzzy.unexpected = [
    # MotionValidator("<10"),
    FlingStopValidator("<10"),
  ]
  return fuzzy.Check(gestures)
