# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from fuzzy_check import FuzzyCheck
from validators import *

# originally generated gestures:
# FlingStop
#   Scroll d=33 x=0 y=33 r=0.67
#   Motion d=1029 x=348 y=950 r=1.68
#   FlingStop
#   Motion d=1010 x=549 y=832 r=1.29
#   FlingStop
#   Motion d=349 x=204 y=279 r=4.14
#   Pinch dz=19 r=0.00
#   FlingStop
#   Motion d=469 x=241 y=398 r=3.78
#   Pinch dz=16 r=0.00
#   Motion d=0 x=0 y=0 r=0.00
#   FlingStop
#   Scroll d=35 x=0 y=35 r=0.58
#   Motion d=1069 x=401 y=987 r=0.97
#   FlingStop
#   Motion d=1055 x=246 y=1025 r=1.33
#   FlingStop
#   Motion d=0 x=0 y=0 r=0.01
#   Motion d=1396 x=663 y=1210 r=1.55
#   FlingStop
#   Motion d=1637 x=983 y=1292 r=1.35
#   Motion d=1818 x=741 y=1646 r=2.64
#   FlingStop

def Validate(raw, events, gestures):
  fuzzy = FuzzyCheck()
  fuzzy.expected = [
    PinchValidator("> 100 ~ 90"),
    PinchValidator("> 100 ~ 90"),
    PinchValidator("> 100 ~ 90"),
    PinchValidator("> 100 ~ 90"),
    PinchValidator("> 100 ~ 90"),
    PinchValidator("> 100 ~ 90"),
    PinchValidator("> 100 ~ 90"),
    PinchValidator("> 100 ~ 90"),
    PinchValidator("> 100 ~ 90"),
  ]
  fuzzy.unexpected = [
    MotionValidator("<1000", merge=True),
    ScrollValidator("<1000", merge=True),
    FlingStopValidator("< 20")
  ]
  return fuzzy.Check(gestures)

Validate.disabled = True
