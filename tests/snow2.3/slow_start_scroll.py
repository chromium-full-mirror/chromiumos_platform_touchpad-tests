# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *


def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    ScrollValidator("== 420 ~ 400"),
    FlingValidator("0"),
  ]
  fuzzy.unexpected = [
    MotionValidator("< 20 ~ 20"),
    FlingStopValidator("<10"),
  ]
  return fuzzy.Check(gestures)
