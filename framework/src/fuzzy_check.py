# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# This module contains the FuzzyCheck class including a list of validator
# classes that are used in combination with FuzzyCheck. The validators make
# use of the FuzzyComparator class that allows validations to be made in
# a fuzzy way that leads to a score instead of a true/false decision.
import math
import re

class FuzzyCheck(object):
  """
  This class can validate a list of gestures to a previously defined set of
  validators. This is used to check if the generated gestures actually
  represent the desired behavior.
  To allow more fine-grained results the output is a score instead of a
  match/no-match decision.
  There are two types of validators: expected or unexpected.
  Expected validators describe the expected behavior in the order it should
  happen. Whenever one of these validators cannot handle a gesture it is
  treated as unexpected and checked by the unexpected validators. A common
  case is expecting a ButtonClick, but allowing a certain amount of
  unexpected Motion to happen.
  """
  def __init__(self):
    self.expected = []
    self.unexpected = []

  def Check(self, event_list):
    """
    Validate gestures against the validators of this object. The expected
    and unexpected variables have to be set up before calling this method.
    This method will return a score between 0..1. It might also return False
    which is different from 0. False describes a complete test-failure, i.e.
    something has happened that should not have happened.
    When it comes to usability impact, it is better when nothing happens, as if
    something completely wrong happens. This is why 'nothing' happened is rated
    slightly better (score=0) as a non-matching behavior (score=False).
    """
    # special case for empty event list
    if len(event_list) == 0:
      if len(self.expected) == 0:
        return 1
      else:
        return 0

    # select first validator
    current_validator = None
    validators = list(reversed(self.expected))
    if len(self.expected) > 0:
      current_validator = validators.pop()

    for event in event_list:
      if current_validator is None:
        # No validator left. All events unexpected.
        if not self._CheckUnexpectedEvent(event):
          return False
      else:
        if not current_validator.Accept(event):
          if (current_validator.score > 0 and len(validators) > 0
              and validators[-1].Accept(event)):
              # transition to next validator
              current_validator = validators.pop()
              current_validator.Validate(event)
          else:
            # unexpected event
            if not self._CheckUnexpectedEvent(event):
              return False
        else:
          # accepted by current validator
          current_validator.Validate(event)

    # calculate score
    score = 1

    # expected validators score
    for validator in self.expected:
      if validator.score is False:
        return False
      else:
        score = score * validator.score

    # unexpected validators score
    for validator in self.unexpected:
      if validator.score is False:
        return False
      else:
        score = score * validator.score

    return score

  def _CheckUnexpectedEvent(self, event):
    """
    find first unexpected validator to Accept event
    """
    for validator in self.unexpected:
      if validator.Accept(event):
        validator.Validate(event)
        return True

    # no validator found. Fail.
    return False

################################################################################
# Validators
################################################################################

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
    return self.__class__.event_type + "()"

  def __str__(self):
    return self.__class__.event_type + "(" + str(self._count) + " " + \
           str(self._count_match) + ")"


class FlingStopValidator(AbstractCountValidator):
  event_type = "FlingStop"


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

  def __str__(self):
    return self.__class__.event_type + "(" + str(self._button) + ", " + \
         str(self._count) + " " + str(self._count_match) + ")"


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
               roughness=None):
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

  def Accept(self, event):
    return event.type == self.event_type

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

  def TypeString(self):
    return self.event_type + "()"

  def __str__(self):
    valuators = []
    if self._distance_check:
      valuators.append("d=" + str(int(self._distance)) + " " +
                       str(self._distance_check))
    if self._x_check:
      valuators.append("x=" + str(int(self._x)) + " " + str(self._x_check))
    if self._y_check:
      valuators.append("y=" + str(int(self._y)) + " " + str(self._y_check))
    if self._roughness_check:
      valuators.append("r=" + str(int(sum(self._roughnesses))) + " " +
                       str(self._roughness_check))
    return self.event_type + "(" + (" && ".join(valuators)) + ")"


class FlingValidator(AbstractAxisValidator):
  event_type = "Fling"


class ScrollValidator(AbstractAxisValidator):
  event_type = "Scroll"


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
    return "not(" + str(self.but_.TypeString()) + ")"

################################################################################
# Fuzzy Comparator
################################################################################

class FuzzyComparator(object):
  """
  This class is able to calculate fuzzy comparisons to return a scoring
  value. Fuzzy comparisons are inequality/equality operators with
  an addition range of validity. The result of the comparison is not
  a true/false decision but a score based on the range of validity.
  The comparison string format is:
    "[op] value [ ~ range ]"
  With the following options for op: ==, >, >=, <, <=
  Value being the integer value we Compare to.
  The range of validity is: [value-range .. value+range]
  If op is omitted we assume op to be == and if range is omitted
  it is assumed to be 0.
  See FuzzyComparator.Compare for information about the return value of
  comparisons.
  Example:
    fuzzy = FuzzyComparator("== 100 ~10")
    fuzzy.Compare(100) -> 1
    fuzzy.Compare(105) -> 0.5
    fuzzy.Compare(90)  -> 0
    fuzzy.Compare(89)  -> False
  """
  def __init__(self, input):
    if isinstance(input, str):
      m = re.match("([><=]=?)?[ ]*(\-?[0-9]+)[ ]*(~[ ]*[0-9]+)?", input)

      if not m:
        raise ValueError("Malformed comparator: '" + input + "'")

      operator = m.group(1)
      value = m.group(2)
      fuzzyness = m.group(3)

      if value is None:
        raise ValueError("Malformed comparator: '" + input + "'")

      self._target = float(value)

      if operator is not None:
        self._operator_str = m.group(1)
      else:
        self._operator_str = "=="

      self._operator = FuzzyComparator._operator_mapping[self._operator_str]
      if fuzzyness is not None:
        self._fuzzyness = float(fuzzyness[1:])
      else:
        self._fuzzyness = 0
    else:
      self._target = float(input)
      self._fuzzyness = 0
      self._operator = FuzzyComparator._CompareEq
      self._operator_str = "=="

  def __str__(self):
    result = self._operator_str + " " + str(int(self._target))
    if self._fuzzyness > 0:
      result = result + "~" + str(int(self._fuzzyness))
    return result

  def Compare(self, value):
    """
    compares a number with the comparison string provided when constructing
    this object. The return value is:
      False: if the value is out of the valid range
      1: if the value is matched by the unequality/equality operation
      0..1: if the value is somewhere in the range of validity.
    """
    score = self._operator(self, value)
    if score < 0:
      return False
    elif score > 1:
      return 1
    else:
      return score

  def _CompareEq(self, value):
    if self._fuzzyness > 0:
      return (self._fuzzyness - math.fabs(self._target - value)) / \
           self._fuzzyness
    else:
      return value == self._target

  def _CompareGte(self, value):
    if self._fuzzyness > 0:
      return self._CompareGt(value)
    else:
      return value >= self._target

  def _CompareGt(self, value):
    if self._fuzzyness > 0:
      return float(value - self._target + self._fuzzyness) / self._fuzzyness
    else:
      return value > self._target

  def _CompareLte(self, value):
    if self._fuzzyness > 0:
      return self._CompareLt(value)
    else:
      return value <= self._target

  def _CompareLt(self, value):
    if self._fuzzyness > 0:
      return float(self._target - value + self._fuzzyness) / self._fuzzyness
    else:
      return value < self._target

  _operator_mapping = {
    "==": _CompareEq,
    "=" : _CompareEq,
    ">=": _CompareGte,
    ">" : _CompareGt,
    "<=": _CompareLte,
    "<" : _CompareLt,
  }
