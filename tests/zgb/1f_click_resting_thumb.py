# Copyright (c) 2013 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

def Validate(raw, events, gestures):
  """
    1f clicks with a resting thumb separated by cursor movement.
    The thumb is present at all times.
  """
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    ButtonDownValidator(1),
    ButtonUpValidator(1)
  ]
  fuzzy.unexpected = [
    MotionValidator(">0", merge=True),
    FlingStopValidator(">0"),
  ]
  return fuzzy.Check(gestures)
