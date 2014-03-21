# Copyright (c) 2014 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    MotionValidator("> 1000 ~ 500"),
    MotionValidator("> 1000 ~ 500"),
    MotionValidator("> 1000 ~ 500"),
    MotionValidator("> 1000 ~ 500"),
  ]
  fuzzy.unexpected = [
    FlingStopValidator("<10"),
  ]
  return fuzzy.Check(gestures)

@FingerSizes(1, 2)
def InstructRobot(robot):
  robot.Line((0.5, 0.1, 0, 20), (0.5, 0.9, 0, 20), (1, 0, 0, 0), 70, "basic")
  robot.Line((0.5, 0.9, 0, 20), (0.5, 0.1, 0, 20), (1, 0, 0, 0), 70, "basic")
  robot.Line((0.1, 0.5, 0, 20), (0.9, 0.5, 0, 20), (1, 0, 0, 0), 70, "basic")
  robot.Line((0.9, 0.5, 0, 20), (0.1, 0.5, 0, 20), (1, 0, 0, 0), 70, "basic")
