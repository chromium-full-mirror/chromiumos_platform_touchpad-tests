# Copyright (c) 2014 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    FlingStopValidator(">=0"),

    # scroll and fling
    ScrollValidator("> 0"),
    FlingValidator("> 0"),

    # fling stop and scroll
    FlingStopValidator(">=1"),
    ScrollValidator("> 0", merge=True),
    FlingValidator(">= 0")
  ]
  fuzzy.unexpected = [
  ]
  return fuzzy.Check(gestures)

@FingerSizes(1)
def InstructRobot(robot):
  # scroll and fling
  robot.Line((0.0, 0.3, 0, 30), (1.0, 0.3, 0, 30), (0, 1, 1, 0), 20, "swipe")
  # fling stop and scroll a little
  robot.Line((1.0, 0.3, 0, 30), (0.95, 0.3, 0, 30), (0, 1, 1, 0), 1, "basic")
