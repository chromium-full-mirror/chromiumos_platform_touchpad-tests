# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# FlingStop
#   FlingStop
#   FlingStop
#   FlingStop
#   FlingStop
#   FlingStop
#   FlingStop
#   FlingStop
#   FlingStop
#   FlingStop
#   FlingStop
#   FlingStop
#   FlingStop
#   FlingStop

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
  ]
  fuzzy.unexpected = [
    FlingStopValidator("<15"),
  ]
  return fuzzy.Check(gestures)
