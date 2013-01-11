# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# This module is the main module for the console interface. It takes care
# of parsing the command line arguments and formating the output
from os import path
import json
import math
import os
import pprint
import sys

from table import Table
from test_case import TestCase
from test_factory import TestFactory
from test_runner import ParallelTestRunner as TestRunner
from test_verifier import TestVerifier

_help_text = """\
Available Commands:
-------------------
$ touchtests run [all|testname]
Executes tests. Either all of them and presents a resulting overall score.
Or just a single named test.

$ touchtests get [--from filename] gestures-log|evdev-log|activity-log testname
Runs a test and prints the requested log of a specific test. In case the
--from option is used, the test will not be run, but the log will be loaded from
the test results stored in file at 'filename'.

$ touchtests add [name] [activity_log] [cmt_log]
Adds a new test case. The name has to include the platform and can optionally
specify a subfolder where the test should be stored.
activity_log and cmt_log should point to the file names of log files collected
from the device.
You can trim activity_log in tp_view, touchtests will automatically trim the
cmt_log accordingly.

General Info:
-------------
testname arguments:
Tests are always names as [platform]/[name of test case]. You can find the tests
available in the tests folder.
For example: lumpy/scroll_test

Tests Folder:
The tests folder contains a folder for each platform and all the test cases.
Each test case is made up of 3 files:
[testcase].py which contains the validation script
[testcase].log which contains the input_event log
[testcase].props which contains user_defined properties passed to gestures lib.

Platform folders:
To add a new platform you need to add a new folder to the Tests folder, and
generate a platform.dat file. This can be done using the evemu-describe tool
on the target platform:

$ gmerge utouch-evemu
$ evemu-describe /path/to/device > platform.dat
"""


def HelpExit():
  """
  Print help text and exit
  """
  print _help_text
  exit()

def Verify(device, glob):
  verifier = TestVerifier(os.environ["TESTS_DIR"], os.environ["REPLAY_TOOL"],
                          device)
  runner = TestRunner(os.environ["TESTS_DIR"], os.environ["REPLAY_TOOL"])
  cases = runner.DiscoverTestCases(glob)

  for case in cases:
    print "###", case.name
    report = verifier.Verify(case)
    print report

def Run(glob, out_file=None, ref_file=None):
  print "Running tests..."
  runner = TestRunner(os.environ["TESTS_DIR"], os.environ["REPLAY_TOOL"])
  results = runner.RunAll(glob)

  # print reports
  sorted_results_items = sorted(results.items())
  for key, value in sorted_results_items:
    print "### Validation report for", key
    print value["logs"]["validation"]
    print value["error"]

  # load reference
  ref = {}
  if ref_file:
    ref = json.load(open(ref_file))

  # format result table
  table = Table()
  table.title = "Test Results"
  table.header("Test", "reference score", "new score", "delta")

  for key, value in sorted_results_items:
    def ResultStr(value):
      # format result to string
      if value["result"] == "success":
        return "%s (%.4f)" % (value["result"], value["score"])
      else:
        return value["result"]

    # format reference and delta column
    ref_score = ""
    delta_str = ""
    regression = False
    if key in ref:
      ref_score = ResultStr(ref[key])
      delta = value["score"] - ref[key]["score"]
      if math.fabs(delta) < 1e-10:
        # don't color, but line up with other values
        delta_str = "      %.4f    " % delta
      elif delta < 0:
        regression = True
        # color red
        delta_str = "\x1b[91m%+.4f\x1b[0m" % delta
      else:
        # color green
        delta_str = "\x1b[92m%+.4f\x1b[0m" % delta
    table.row(key, ref_score, ResultStr(value), delta_str)

  print table

  if out_file:
    json.dump(results, open(out_file, "w"), indent=2)
    print "results stored in:", out_file

  if regression:
    print "\x1b[91mThere are regressions present in this test run!\x1b[0m"
    exit(-1)

def Get(test_name, what, file=None):
  if file:
    data = json.load(open(file))
    results = data[test_name]
  else:
    runner = TestRunner(os.environ["TESTS_DIR"], os.environ["REPLAY_TOOL"])
    data = runner.RunAll(test_name)
    results = data[test_name]

  if what == "gestures-log":
    print results["logs"]["gestures"]
  elif what == "evdev-log":
    print results["logs"]["evdev"]
  elif what == "activity-log":
    print results["logs"]["activity"]
  elif what == "gestures":
    print results["gestures"]
  elif what == "events":
    print results["events"]

def Add(testname, activity_log, event_log):
  """
  Adds a new test case.
  """
  # determine test name from activity_log name
  factory = TestFactory(os.environ["TESTS_DIR"], os.environ["REPLAY_TOOL"])
  case = factory.CreateTest(testname, activity_log, event_log)

  print "Test \"" + case.name + "\" created"

def Main():
  """
  Main entry point for the console interface
  """

  # setup paths from environment variables
  if "TESTS_DIR" not in os.environ:
    print "Require TESTS_DIR environment variable"
    exit(-1)

  if "REPLAY_TOOL" not in os.environ:
    print "Require REPLAY_TOOL environment variable"
    exit(-1)

  TestCase.tests_path = os.environ["TESTS_DIR"]
  TestCase.replay_tool = os.environ["REPLAY_TOOL"]

  # parse arguments and call command methods
  if len(sys.argv) < 2:
    HelpExit()

  # call command method according to command line arguments
  # todo: use an option parser library
  cmd = sys.argv[1]

  if cmd == "run":
    if len(sys.argv) == 3:
      test_name = sys.argv[2]
      Run(test_name)
    elif len(sys.argv) == 5 and sys.argv[2] == "--out":
      test_name = sys.argv[4]
      out = sys.argv[3]
      Run(test_name, out)
    elif len(sys.argv) == 5 and sys.argv[2] == "--ref":
      test_name = sys.argv[4]
      ref_file = sys.argv[3]
      Run(test_name, None, ref_file)
    else:
      HelpExit()

  elif cmd == "get":
    if len(sys.argv) == 4:
      test_name = sys.argv[3]
      what = sys.argv[2]
      Get(test_name, what)
    elif len(sys.argv) == 6 and sys.argv[2] == "--from":
      test_name = sys.argv[5]
      what = sys.argv[4]
      file = sys.argv[3]
      Get(test_name, what, file)
    else:
      HelpExit()

  elif cmd == "verify":
    if len(sys.argv) < 4:
      HelpExit()
    device_name = sys.argv[2]
    test_name = sys.argv[3]
    Verify(device_name, test_name)

  elif cmd == "add":
    if len(sys.argv) < 5:
      HelpExit()
    testname = sys.argv[2]
    activity_log = sys.argv[3]
    event_log = sys.argv[4]
    Add(testname, activity_log, event_log)

  else:
    HelpExit()

if __name__ == "__main__":
  Main()
