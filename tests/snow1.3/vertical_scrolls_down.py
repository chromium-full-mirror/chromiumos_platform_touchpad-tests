# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *


def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    ScrollValidator("> 1200 ~ 600"),
    FlingValidator("> 6000 ~ 3000"),
    ScrollValidator("> 1000 ~ 500"),
    FlingValidator("> 600 ~ 300"),
    ScrollValidator("> 200 ~ 100"),
    FlingValidator("0"),
    ScrollValidator("> 900 ~ 450"),
    FlingValidator("> 3000 ~ 1500"),
  ]
  fuzzy.unexpected = [
    FlingStopValidator("<10"),
  ]
  return fuzzy.Check(gestures)
