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
    self.current_finger_size = None
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

  def CleanUp(self):
    if self.manual_fingertips:
      return
    if self.current_finger_size is not None:
      print "###### Removing %d finger tips!" % self.current_finger_size
      self.Execute("python manipulate_fingertips.py 1 1 1 1 %d False"
                   % self.current_finger_size)
    self.current_finger_size = None

  def SetupFingerSize(self, size):
    if self.manual_fingertips:
      return

    if self.current_finger_size != size:
      if self.current_finger_size is not None:
        print "###### Removing %d finger tips!" % self.current_finger_size
        self.Execute("python manipulate_fingertips.py 1 1 1 1 %d False"
                     % self.current_finger_size)
      print "###### Picking %d finger tips!" % size
      self.Execute("python manipulate_fingertips.py 1 1 1 1 %d True"
                   % size)
      self.current_finger_size = size

  def Line(self, start, end, tips, speed, type):
    if not self.current_finger_size and not self.manual_fingertips:
      print "Select finger size before gesture"
      sys.exit(1)
    if self.slow:
      speed = 5
    self.Execute("line.py", start, end, tips, (speed, type))

  def Tap(self, pos, tips, count):
    if not self.current_finger_size and not self.manual_fingertips:
      print "Select finger size before gesture"
      sys.exit(1)
    self.Execute("click.py", pos, tips, (count, "tap"))

  def Click(self, pos, tips, count, size=1):
    if self.current_finger_size != None:
      self.CleanUp()
    self.Execute("click.py", pos, tips, (size, manual))

  def Execute(self, file, *param_tuples):
    base = ("python", file, "regression.p")
    args = map(lambda s: str(s), chain(base, *param_tuples))
    cmd = " ".join(args)

    print "Robot Command:", cmd
    res = self.remote.Execute(cmd, self.dir, verbose=True)
    if not res:
      print "Command Failed:", cmd
      sys.exit(1)

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

    expanded = []
    for case in cases:
      if case.is_virtual:
        continue
      # per default tests are performed with the finger size 2 only
      if hasattr(case.instruct_robot, "finger_sizes"):
        sizes = case.instruct_robot.finger_sizes
      else:
        sizes = [2]
      # append a new test case for each finger size
      if sizes is None:
        # this test takes care of finger size setup
        expanded.append((TestCase(self.tests_dir, case.name), None))
        continue
      for size in sizes:
        name = case.name + "_s" + str(size)
        expanded.append((TestCase(self.tests_dir, name), size))

    expanded.sort(key=lambda entry: entry[1])

    print "Instructing robot to generate tests:"
    for case, fingersize in expanded:
      if fingersize is None:
        print "  - %s (custom)" % (case.name)
      else:
        print "  - %s (%d)" % (case.name, fingersize)
    UserConfirm()

    # run tests with configured finger sizes
    for case, fingersize in expanded:
      if fingersize is None:
        continue
      self.robot.SetupFingerSize(fingersize)
      self.GenerateCase(case)

    self.robot.CleanUp()

    # run tests that have customized finger size setup
    for case, fingersize in expanded:
      if fingersize is None:
        self.GenerateCase(case)


  @staticmethod
  def DiscoverRobotCases(tests_dir, glob=None):
    cases = TestCase.DiscoverTestCases(tests_dir, glob)
    return filter(lambda c: c.instruct_robot is not None, cases)