# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# This module contains the Validators used by the FuzzyCheck class.
# The validators mak use of the FuzzyComparator class that allows validations
# to be made in a fuzzy way that leads to a score instead of a true/false
# decision.
import math
import re

from fuzzy_check import FuzzyComparator

class AbstractValidator(object):
  """
  Base class provides the possibility to Validate start/end times of
  gestures.
  """
  def __init__(self, start=None, end=None):
    if start:
      self._start_check = FuzzyComparator(start)
    else:
      self._start_check = None
    if end:
      self._end_check = FuzzyComparator(end)
    else:
      self._end_check = None

    self._start = 0
    self._end = 0

  def Accept(self, event):
    """
    This method is used to determine if this validator is able to validate a
    certain event. If it cannot validate the event it will be handled by
    the next validator or is considered as an unexpected event.
    """
    return False

  def Validate(self, event):
    """
    While this validator is active, this method is called for each gesture that
    it accepts (i.e. Accept(event) returns True).
    """
    pass

  def TypeStr(self):
    """
    Returns a shortened string representation used for presentation. It should
    not contain any validation information but only show which kind of
    gestures are accepted.
    """
    pass

  def _ValidateTimestamps(self, event):
    if self._start == 0:
      self._start = event.start
    self._end = event.end

  def _ScoreTimestamps(self):
    score = 1
    if self._start_check:
      score = score * self._start_check.Compare(self._start)
    if self._end_check:
      score = score * self._end_check.Compare(self._end)
    return score


class AbstractCountValidator(AbstractValidator):
  """
  Base class for buttons. Allows to Validate if a certain number of
  button events are present.
  """

  def __init__(self, count_match="== 1 ~ 1", start=None, end=None):
    AbstractValidator.__init__(self, start, end)
    self._count_match = FuzzyComparator(count_match)
    self._count = 0
    self.score = self._count_match.Compare(self._count)

  def Accept(self, event):
    return event.type == self.__class__.event_type

  def Validate(self, event):
    self._count = self._count + 1
    self.score = self._count_match.Compare(self._count)
    self._ValidateTimestamps(event)
    self.score = self.score * self._ScoreTimestamps()

  def TypeString(self):
    return self.__class__.event_type

  def __str__(self):
    format_str = "{0} c:{1}{2}"
    return format_str.format(self.TypeString(), self._count, self._count_match)


class FlingStopValidator(AbstractCountValidator):
  event_type = "FlingStop"

class SwipeLiftValidator(AbstractCountValidator):
  event_type = "SwipeLift"


class AbstractButtonValidator(AbstractCountValidator):
  """
  Base class for buttons. Allows to Validate if a certain number of
  button events are present.
  """

  def __init__(self, button, count_match="== 1 ~ 1", start=None, end=None):
    AbstractCountValidator.__init__(self, count_match, start, end)
    self._button = button

  def Accept(self, event):
    return event.type == self.__class__.event_type and \
         event.button == self._button

  def TypeString(self):
    return self.__class__.event_type + "(" + str(self._button) + ")"


class ButtonDownValidator(AbstractButtonValidator):
  event_type = "ButtonDown"


class ButtonUpValidator(AbstractButtonValidator):
  event_type = "ButtonUp"


class AbstractAxisValidator(AbstractValidator):
  """
  Allows to Validate movement on a 2 dimensional axis (scroll, cursor movement,
  or fling. x and y movement can be validateValidated separately, as well as the
  overall distance traveled.
  Next to the overall movement, the Roughness measure of the movement can also
  be validateValidated.
  """
  def __init__(self, d=None, x=None, y=None, start=None, end=None,
               roughness=None, merge=False):
    AbstractValidator.__init__(self, start, end)
    if d:
      self._distance_check = FuzzyComparator(d)
    else:
      self._distance_check = None
    if x:
      self._x_check = FuzzyComparator(x)
    else:
      self._x_check = None
    if y:
      self._y_check = FuzzyComparator(y)
    else:
      self._y_check = None

    if roughness:
      self._roughness_check = FuzzyComparator(roughness)
    else:
      self._roughness_check = None

    self._distance = 0
    self._x = 0
    self._y = 0
    self._roughnesses = []
    self._UpdateScore()
    self.end = -1.0
    self.merge = merge

  def Accept(self, event):
    return (event.type == self.event_type and
            ((float(event.start) - self.end) < 0.1 or
             self.end < 0.0 or
             self.merge))

  def _UpdateScore(self):
    self.score = 1
    if self._distance_check:
      self.score = self.score * self._distance_check.Compare(self._distance)
    if self._x_check:
      self.score = self.score * self._x_check.Compare(self._x)
    if self._y_check:
      self.score = self.score * self._y_check.Compare(self._y)
    if self._roughness_check:
      roughness = sum(self._roughnesses)
      self.score = self.score * self._roughness_check.Compare(roughness)
    self.score = self.score * self._ScoreTimestamps()
    if self.score == 0:
      self.score = False

  def Validate(self, event):
    self._roughnesses.append(event.Roughness())
    self._distance = self._distance + event.distance
    self._x = self._x + event.dx
    self._y = self._y + event.dy
    self._ValidateTimestamps(event)
    self._UpdateScore()
    self.end = float(event.end)

  def TypeString(self):
    return self.event_type

  def __str__(self):
    valuators = []
    if self._distance_check:
      valuators.append("d:" + str(int(self._distance)) +
                       str(self._distance_check))
    if self._x_check:
      valuators.append("x:" + str(int(self._x)) + str(self._x_check))
    if self._y_check:
      valuators.append("y:" + str(int(self._y)) + str(self._y_check))
    if self._roughness_check:
      valuators.append("r:" + str(int(sum(self._roughnesses))) +
                       str(self._roughness_check))
    return self.event_type + " " + (" ".join(valuators))


class FlingValidator(AbstractAxisValidator):
  event_type = "Fling"


class ScrollValidator(AbstractAxisValidator):
  event_type = "Scroll"


class SwipeValidator(AbstractAxisValidator):
  event_type = "Swipe"


class MotionValidator(AbstractAxisValidator):
  event_type = "Motion"


class AnythingButValidator(object):
  """
  Allows to 'wait' for a certain gesture to be performed. It will accept all
  events exept for the events accepted by the validator passed as the 'but'
  argument.
  The score of this validator is always 1.
  """
  def __init__(self, but):
    self._but = but
    self.score = 1

  def Accept(self, event):
    return not self._but.Accept(event)

  def Validate(self, event):
    pass

  def __str__(self):
    return "not(" + str(self._but.TypeString()) + ")"
