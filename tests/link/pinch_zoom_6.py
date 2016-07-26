# Copyright 2016 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    PinchValidator("== 1.356 ~ 0.2"),
  ]
  fuzzy.unexpected = [
    MotionValidator("==0 ~ 5"),
    FlingStopValidator("< 10"),
  ]
  return fuzzy.Check(gestures)

Validate.disable = True
