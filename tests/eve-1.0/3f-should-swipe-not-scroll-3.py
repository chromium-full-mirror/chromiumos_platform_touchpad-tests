# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    ScrollValidator(">= 300", merge=True),
    FlingValidator(">= 0"),
    SwipeValidator("== 215.6 ~ 20", merge=True),
    SwipeLiftValidator(),
  ]
  fuzzy.unexpected = [
    FlingStopValidator("<10"),
  ]
  return fuzzy.Check(gestures)
