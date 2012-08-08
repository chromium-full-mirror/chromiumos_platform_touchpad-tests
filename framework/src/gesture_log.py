# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# This module contains the GestureLog class which is used for converting the
# raw activity log into a processable format.

import json
import math

class GestureLog(object):
  """
  The gesture log is a representation of an activity log as it is generated
  by the replay tool or 'tpcontrol log'.
  It converts all gestures into a list of events using the classes below.
  To allow easier processing all events that belong together are merged into
  gestures. For example all scroll events from one scroll motion on the touchpad
  are merged to create a single scroll gesture.
  - self.events will contain the list of events
  - self.gestures the list of gestures.
  """
  def __init__(self, log):
    self.raw = json.loads(log)
    raw_events = filter(lambda e: e["type"] == "gesture", self.raw["entries"])
    self.events = self._ParseRawEvents(raw_events)
    self.gestures = self._MergeGestures(self.events)

    self.properties = self.raw["properties"]
    self.hwstates = filter(lambda e: e["type"] == "hardwareState",
                           self.raw["entries"])
    self.hwproperties = self.raw["hardwareProperties"]

  def _ParseRawEvents(self, gesture_list):
    events = []

    for gesture in gesture_list:
      start_time = float(gesture["startTime"])
      end_time = float(gesture["endTime"])

      if gesture["gestureType"] == "move":
        events.append(MotionGesture(gesture["dx"], gesture["dy"], start_time,
                                    end_time))

      elif gesture["gestureType"] == "buttonsChange":
        if gesture["down"] != 0:
          button = gesture["down"]
          events.append(ButtonDownGesture(button, start_time, end_time))
        if gesture["up"] != 0:
          button = gesture["up"]
          events.append(ButtonUpGesture(button, start_time, end_time))

      elif gesture["gestureType"] == "scroll":
        events.append(ScrollGesture(gesture["dx"], gesture["dy"], start_time,
                                    end_time))

      elif gesture["gestureType"] == "fling":
        if gesture["vx"] + gesture["vy"] == 0:
          events.append(FlingStopGesture(start_time, end_time))
        else:
          events.append(FlingGesture(gesture["vx"], gesture["vy"], start_time,
                                     end_time))

      else:
        print "Unknown gesture:", repr(gesture)

    return events

  def _MergeGestures(self, event_list):
    gestures = []
    last_event_of_type = {}

    for event in event_list:
      # merge motion and scroll events into gestures
      if event.type == "Motion" or event.type == "Scroll":
        if event.type not in last_event_of_type:
          last_event_of_type[event.type] = event
          gestures.append(event)
        else:
          if event.start - last_event_of_type[event.type].end < 0.1:
            last_event_of_type[event.type].Append(event)
          else:
            last_event_of_type[event.type] = event
            gestures.append(event)
      else:
        gestures.append(event)
    return gestures


class MotionGesture(object):
  """
  The motion gesture describes motion events. Either a single event or a
  list of events that belong to one gesture.
  """
  type = "Motion"

  def __init__(self, dx, dy, start, end):
    """
    Create a new instance describing a single motion event. To describe a
    list of events that form a gesture use the Append method.
    @param dx: movement in x coords
    @param dy: movement in y coords
    @param start: start timestamp
    @param end: end timestamp
    """
    self.dx = math.fabs(dx)
    self.dy = math.fabs(dy)
    self.start = start
    self.end = end
    self.segments = []

    self.distance = math.sqrt(self.dx * self.dx + self.dy * self.dy)
    self.segments.append(self.distance)

  def Append(self, motion):
    """
    Append an motion event to build a gesture.
    @param motion:
    """
    self.dx = self.dx + motion.dx
    self.dy = self.dy + motion.dy
    self.distance = self.distance + motion.distance
    self.segments.append(motion.distance)
    self.end = motion.end

  def Roughness(self):
    """
    The roughness measures the variability in the movement events. A continuous
    stream of events with similar movement distances is considered to be smooth.
    Choppy movement with a high variation in movement distances on the other
    hand is considered as rough. i.e. a constant series of movement distances is
    considered perfectly smooth and will result in a roughness of 0.
    Whenever there are sudden changes, or very irregular movement distances
    the roughness will increase.
    """
    # Each event in the gesture resulted in a movement distance. These distances
    # are treated as a signal and high pass filtered. This results in a signal
    # containing only high frequency changes in the distance, i.e. the rough
    # parts.
    # The squared average of this signal is used as a measure for the roughness.

    # gaussian filter kernel with sigma=1:
    # The kernel is calculated using this formula (with s=sigma):
    # 1/sqrt(2*pi*s^2)*e^(-x^2/(2*s^2))
    # The array can be recalculated with modified sigma by entering the
    # following equation into http://www.wolframalpha.com/:
    # 1/sqrt(2*pi*s^2)*e^(-[-2, -1, 0, 1, 2]^2/(2*s^2))
    # (Replace s with the desired sigma value)
    gaussian = [0.053991, 0.241971, 0.398942, 0.241971, 0.053991]

    # normalize gaussian filter kernel
    gsum = sum(gaussian)
    gaussian = map(lambda g: g / gsum, gaussian)

    # add padding to the front/end of the distances
    segments = []
    segments.append(self.segments[0])
    segments.append(self.segments[0])
    segments.extend(self.segments)
    segments.append(self.segments[-1])
    segments.append(self.segments[-1])

    # low pass filter the distances
    segments_lp = []
    for i in range(2, len(segments) - 2):
      v = segments[i - 2] * gaussian[0]
      v = v + segments[i - 1] * gaussian[1]
      v = v + segments[i  ] * gaussian[2]
      v = v + segments[i + 1] * gaussian[3]
      v = v + segments[i + 2] * gaussian[4]
      segments_lp.append(v)

    # H_HP = 1 - H_LP
    segments_hp = []
    for i in range(0, len(self.segments)):
      segments_hp.append(self.segments[i] - segments_lp[i])

    # square signal and calculate squared average
    segments_hp_sq = map(lambda v:v * v, segments_hp)
    return math.sqrt(sum(segments_hp_sq) / len(segments_hp))

  def __str__(self):
    fstr = "{0} d={1} x={2} y={3} r={4:.2f}"
    return fstr.format(self.__class__.type, int(self.distance), int(self.dx),
                       int(self.dy), self.Roughness())

  def __repr__(self):
    return str(self)


class ScrollGesture(MotionGesture):
  """
  The scroll gesture is functionally the same as the MotionGesture
  """
  type = "Scroll"


class FlingGesture(MotionGesture):
  """
  The scroll gesture is functionally the same as the MotionGesture
  """
  type = "Fling"


class FlingStopGesture(object):
  """
  The FlingStop gesture only contains the start and end timestamp.
  """
  type = "FlingStop"

  def __init__(self, start, end):
    self.start = start
    self.end = end

  def __str__(self):
    return self.__class__.type

  def __repr__(self):
    return str(self)


class AbstractButtonGesture(object):
  """
  As both button down and up gestures are functionally identical it has
  been extracted to this class. The AbstractButtonGesture stores a button ID
  next to the start and end time of the gesture.
  """
  type = "Undefined"

  def __init__(self, button, start, end):
    self.button = button
    self.start = start
    self.end = end

  def __str__(self):
    return self.__class__.type + "(" + str(self.button) + ")"

  def __repr__(self):
    return str(self)


class ButtonDownGesture(AbstractButtonGesture):
  """
  The ButtonDown gesture is functionally the same as AbstractButtonGesture
  """
  type = "ButtonDown"


class ButtonUpGesture(AbstractButtonGesture):
  """
  The ButtonUp gesture is functionally the same as AbstractButtonGesture
  """
  type = "ButtonUp"
