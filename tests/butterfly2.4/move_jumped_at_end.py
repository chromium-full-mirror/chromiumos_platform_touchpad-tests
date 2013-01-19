# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# Motion d=248 x=147 y=191 r=2.76
#   FlingStop

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  # Make sure no events after 4924.525335 occur
  for event in events:
    dist = event.distance if hasattr(event, 'distance') else -1.0
    if float(event.end) > 4924.525 and dist > 0.0:
      return False, 'Has jump movement at end'
  return 1, 'Success'
