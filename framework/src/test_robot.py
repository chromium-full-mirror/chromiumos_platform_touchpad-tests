# Copyright (c) 2014 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from collections import namedtuple
from itertools import chain
import sys

from mtlib.cros_remote import CrOSRemote
from mtlib.log import DeviceLog
from mtreplay import MTReplay
from test_case import TestCase
from test_factory import TestFactory


Options = namedtuple('Options', 'new')


def UserConfirm(msg=None):
  if msg:
    print msg
  print "Are you sure you wish to continue? [y/N]"
  response = sys.stdin.readline()
  if response.strip() not in ('y', 'Y', 'yes', 'Yes'):
    sys.exit(1)


class TestRobot(object):
  def __init__(self, ip, calib, slow=None, manual_fingertips=False):
    self.ip = ip
    self.slow = slow
    self.manual_fingertips = manual_fingertips
    self.remote = CrOSRemote(self.ip)
    self.FindRobotDir()
    if calib:
      UserConfirm("Starting calibration for new device")
      cmd = "python calibrate_for_new_device.py regression"
      if manual_fingertips:
        cmd = cmd + " --manual-fingertips"
      self.Execute(cmd)

  def FindRobotDir(self):
    search_dirs = [
      "/usr/lib64/python2.7/site-packages/touchbotII",
      "/usr/lib/python2.7/site-packages/touchbotII",
      "/usr/local/lib64/python2.7/site-packages/touchbotII",
      "/usr/local/lib/python2.7/site-packages/touchbotII"]
    for dir in search_dirs:
      if self.remote.Execute("test -e %s/calibrate_for_new_device.py" % dir,
                             verbose=False):
        self.dir = dir
        return
    print "Cannot find robot directory"
    sys.exit(1)

  def Line(self, start, end, tips, speed, type):
    if self.slow:
      speed = 5

    args = map(lambda s: str(s), chain(start, end, tips, (speed, type)))
    cmd = "python line.py regression.p " + " ".join(args)
    self.Execute(cmd)

  def Execute(self, cmd):
    print "Robot Command:", cmd
    self.remote.Execute(cmd, self.dir, verbose=True)

  def ClearLog(self):
    self.remote.Execute(
        "/opt/google/touchpad/tpcontrol set \"Logging Reset\" 1")

  def GetLog(self):
    replay = MTReplay()

    options = object()
    log = DeviceLog(self.ip, Options(new=True))
    return replay.TrimEvdev(log)

class RobotTestGenerator(object):
  def __init__(self, ip, calib, slow, manual_fingertips, tests_dir):
    self.tests_dir = tests_dir
    self.robot = TestRobot(ip, calib, slow, manual_fingertips)

  def GenerateCase(self, test_case):
    print "Instructing robot to generate test", test_case.name

    self.robot.ClearLog()
    test_case.instruct_robot(self.robot)
    log = self.robot.GetLog()
    if not log:
      print "Nothing happened... is the robot set up?"
      return

    factory = TestFactory(self.tests_dir)
    case = factory.CreateTest(test_case.name, log, False)

  def GenerateAll(self, glob, overwrite=False):
    cases = RobotTestGenerator.DiscoverRobotCases(self.tests_dir, glob)
    if not overwrite:
      cases = filter(lambda c: not c.IsComplete(), cases)

    print "Instructing robot to generate tests:"
    for case in cases:
      print "  - " + case.name
    UserConfirm()

    for case in cases:
      module = case.module
      self.GenerateCase(case)

  @staticmethod
  def DiscoverRobotCases(tests_dir, glob=None):
    cases = TestCase.DiscoverTestCases(tests_dir, glob)
    return filter(lambda c: c.instruct_robot is not None, cases)