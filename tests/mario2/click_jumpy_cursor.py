# Copyright (c) 2013 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

def Validate(raw, events, gestures):
  """
    The original log contained two clicks with cursor movement
    in between. Due to merge/split issues there were cursor jumps.
    Check that there are no cursor motions between button down/up and
    that none of the motions shows excessive speed.
  """
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    MotionValidator(speed="<1000", merge=True),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    MotionValidator(speed="<1000", merge=True),
    ButtonDownValidator(1),
    ButtonUpValidator(1),
    MotionValidator(speed="<1000", merge=True)
  ]
  fuzzy.unexpected = [
    FlingStopValidator(">=0"),
  ]
  return fuzzy.Check(gestures)
