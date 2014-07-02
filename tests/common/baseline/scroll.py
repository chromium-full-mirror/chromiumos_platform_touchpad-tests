# Copyright (c) 2014 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    ScrollValidator("> 50 ~ 50"),
    ScrollValidator("> 50 ~ 50"),
    ScrollValidator("> 200 ~ 200"),
    ScrollValidator("> 200 ~ 200"),
  ]
  fuzzy.unexpected = [
    FlingValidator(">=0", merge=True),
    MotionValidator("<10", merge=True),
    FlingStopValidator("<20"),
  ]
  return fuzzy.Check(gestures)

def InstructRobot(robot):
  robot.Line((0.5, 0.1, -45, 20), (0.5, 0.5, -45, 20),
             (1, 0, 1, 0), 70, "basic", 0.5)
  robot.Line((0.5, 0.5, -45, 20), (0.5, 0.1, -45, 20),
             (1, 0, 1, 0), 70, "basic", 0.5)
  robot.Line((0.2, 0.3, -45, 20), (0.8, 0.3, -45, 20),
             (1, 0, 1, 0), 70, "basic", 0.5)
  robot.Line((0.8, 0.3, -45, 20), (0.2, 0.3, -45, 20),
             (1, 0, 1, 0), 70, "basic", 0.5)
