# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# This module is the main module for the console interface. It takes care
# of parsing the command line arguments and formating the output
from os import path
from test_case import TestCase
from test_factory import TestFactory
from test_runner import TestRunner
import os
import pprint
import sys

_help_text = """\
Available Commands:
-------------------
$ touchtests run [all|testname]
Executes tests. Either all of them and presents a resulting overall score.
Or just a single named test.

$ touchtests debug [testname]
Same as run, but additionally displays the gestures library log.

$ touchtests log [testname]
Executes a test and prints the activity_log to stdout. Useful to view the
results in tp_view.

$ touchtests add [platform] [activity_log] [cmt_log]
Adds a new test case. Each test belongs to a platform "lumpy", "cr48", etc.
activity_log and cmt_log should point to the file names of log files collected
from the device.
You can trim activity_log in tp_view, touchtests will automatically trim the
cmt_log accordingly.
The test will be named after the filename of the activity_log and a dummy
validation script is automatically generated.

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


def Log(glob, debug=False):
  """
  Print only the activity log. The user can pipe the output of this command
  to be used in other tools like tpview.
  """
  runner = TestRunner(os.environ["TESTS_DIR"], os.environ["REPLAY_TOOL"])
  cases = runner.DiscoverTestCases(glob)

  # check number of test cases
  if len(cases) > 1:
    print "Multiple test cases match '" + str(glob) + "':"
    for case in cases:
      print " -", case.name
    return

  if len(cases) < 1:
    print "Cannot find test " + glob
    return

  # run test and print results
  results = runner.RunTest(cases[0])
  if results["error"]:
    print results["error"]
    return

  print results["logs"]["activity"]


def Run(glob, debug=False):
  """
  Run tests. For now just print all of the results as a data structure.
  TODO(denniskempin): Pretty formating of results
  """
  runner = TestRunner(os.environ["TESTS_DIR"], os.environ["REPLAY_TOOL"])
  results = runner.RunAll(glob)
  pprint.pprint(results)


def Add(platform, activity_log, event_log):
  """
  Adds a new test case.
  """
  # determine test name from activity_log name
  testname = path.splitext(path.basename(activity_log))[0]
  testname = path.join(platform, testname)
  factory = TestFactory(os.environ["TESTS_DIR"], os.environ["REPLAY_TOOL"])
  case = factory.CreateTest(testname, activity_log, event_log)

  runner = TestRunner(os.environ["TESTS_DIR"], os.environ["REPLAY_TOOL"])
  result = runner.RunTest(case)
  print result["gestures"]


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
  cmd = sys.argv[1]

  if cmd == "run" or cmd == "debug":
    if len(sys.argv) < 3:
      HelpExit()
    test_name = sys.argv[2]
    Run(test_name, (cmd == "debug"))

  elif cmd == "log":
    if len(sys.argv) < 3:
      HelpExit()
    test_name = sys.argv[2]
    Log(test_name)

  elif cmd == "add":
    if len(sys.argv) < 5:
      HelpExit()
    platform = sys.argv[2]
    activity_log = sys.argv[3]
    event_log = sys.argv[4]
    Add(platform, activity_log, event_log)

  else:
    HelpExit()

if __name__ == "__main__":
  Main()
