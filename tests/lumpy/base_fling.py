# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import *

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    FlingValidator(">0"),
    FlingStopValidator(1),
    FlingValidator(">0"),
    FlingStopValidator(1),
  ]
  fuzzy.unexpected = [
    MotionValidator("<10"),
    FlingStopValidator("<10"),
    ScrollValidator(),
  ]
  return fuzzy.Check(gestures)
