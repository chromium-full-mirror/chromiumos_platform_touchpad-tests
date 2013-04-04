# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# This module is the main module for the console interface. It takes care
# of parsing the command line arguments and formating the output
from optparse import OptionParser
from subprocess import Popen, PIPE, STDOUT
from tempfile import NamedTemporaryFile
import json
import math
import os
import sys

from mtedit.editor import LogEditor
from mtedit.log import Log

from table import Table
from test_case import TestCase
from test_factory import TestFactory
from test_runner import ParallelTestRunner as TestRunner


_help_text = """\
Multitouch Regression Test Suite:
---------------------------------

$ %prog [all|glob]
Executes tests. Either all of them or selected tests by providing a glob match
In order to test for regressions use:
$ %prog all --out filename
make a change
$ %prog all --ref filename
Which will display the changes in test results compared to before the change

$ %prog testname -v %info%
Run test and display information. %info% can be:
- a or activity: to view the touchpad activity in mtedit
- g or gestures: to view the generated gestures
- al or activity-log: to view the generated activity log
- gl or gestures-log: to view the generated gestures log
- el or evdev-log: to view the generated evdev log

$ %prog test_name -c %source%
Create a new test case from %source%. Source can be:
- A feedback URL
- A device IP
- The path to an activity log file
When using a file name test.log, %prog will look at test.log.evdev
for the evdev log file. You can optionally supply -e to override this path.
%prog will display an URL where you can trim the log file, the trimmed
log file will then be used to create the new test case. Specify --no-edit in
case you do not want to use the original files without trimming.

$ %prog test_name --gdb
Run the test using gdb for debugging the gestures library

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


def Compile():
  if "SRC_DIR" not in os.environ:
    print "Requires SRC_DIR env-var. Re-run $ sudo make setup-in-place"
    sys.exit(-1)

  dir = os.environ["SRC_DIR"]
  print "Recompiling gestures/libevdev/replay..."
  process = Popen(["make", "in-place"], cwd=dir,
                  stdout=PIPE, stderr=STDOUT)
  ret = process.wait()
  if ret != 0:
    print process.stdout.read()
    sys.exit(-1)


def Verify(device, glob):
  verifier = TestVerifier(os.environ["TESTS_DIR"], device)
  runner = TestRunner(os.environ["TESTS_DIR"], os.environ["XORG_CONF_DIR"])
  cases = runner.DiscoverTestCases(glob)

  for case in cases:
    print "###", case.name
    report = verifier.Verify(case)
    print report


def Run(glob, out_file=None, ref_file=None, autotest=False):
  if not autotest:
    Compile()
  print "Running tests..."
  runner = TestRunner(os.environ["TESTS_DIR"], os.environ["XORG_CONF_DIR"])
  results = runner.RunAll(glob)

  # load reference
  ref = {}
  if ref_file:
    ref = json.load(open(ref_file))

  # print reports
  sorted_results_items = sorted(results.items())
  for key, value in sorted_results_items:
    if len(results) > 1:
      # only print reports for regressions or failed tests
      if key in ref:
        delta = value["score"] - ref[key]["score"]
        if math.fabs(delta) < 1e-10:
          continue
      elif value["result"] == "success":
        continue

    print "### Validation report for", key
    print value["description"]
    if value["disabled"]:
      print "DISABLED"
    else:
      print value["logs"]["validation"]
      print value["error"]

  # format result table
  table = Table()
  table.title = "Test Results"
  table.header("Test", "reference score", "new score", "delta")

  regression = False
  for key, value in sorted_results_items:
    def ResultStr(value):
      # format result to string
      if value["result"] == "success":
        msg = "success" if value["score"] >= 0.5 else "bad"
        return "%s (%.4f)" % (msg, value["score"])
      elif value["disabled"]:
        return "disabled"
      else:
        return value["result"]

    # format reference and delta column
    ref_score = ""
    delta_str = ""
    if key in ref:
      ref_score = ResultStr(ref[key])
      delta = value["score"] - ref[key]["score"]
      if math.fabs(delta) < 1e-10:
        # default color
        delta_str = "\x1b[0m%.4f\x1b[0m" % delta
      elif delta < 0:
        regression = True
        # color red
        delta_str = "\x1b[31m%+.4f\x1b[0m" % delta
      else:
        # color green
        delta_str = "\x1b[32m%+.4f\x1b[0m" % delta
    table.row(key, ref_score, ResultStr(value), delta_str)

  print table

  if out_file:
    json.dump(results, open(out_file, "w"), indent=2)
    print "results stored in:", out_file

  if regression:
    print "\x1b[91mThere are regressions present in this test run!\x1b[0m"
    exit(-1)


def Get(test_name, what, file=None):
  Compile()
  if file:
    data = json.load(open(file))
    results = data[test_name]
  else:
    runner = TestRunner(os.environ["TESTS_DIR"], os.environ["XORG_CONF_DIR"])
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
  elif what == "return-activity":
    return results["logs"]["activity"]

def GDB(test_name):
  Compile()
  runner = TestRunner(os.environ["TESTS_DIR"], os.environ["XORG_CONF_DIR"])
  data = runner.RunGDB(test_name)

def Add(testname, activity_log, event_log):
  """
  Adds a new test case.
  """
  # determine test name from activity_log name
  factory = TestFactory(os.environ["TESTS_DIR"], os.environ["XORG_CONF_DIR"])
  case = factory.CreateTest(testname, activity_log, event_log)
  if case:
    print "Test \"" + case.name + "\" created"


def Main():
  """
  Main entry point for the console interface
  """

  # setup paths from environment variables
  if "TESTS_DIR" not in os.environ:
    print "Require TESTS_DIR environment variable"
    exit(-1)

  TestCase.tests_path = os.environ["TESTS_DIR"]

  parser = OptionParser(usage=_help_text)
  parser.add_option("-c", "--create",
                    dest="create", default=None,
                    help="create new test case from URL/IP or log file")
  parser.add_option("-e", "--evdev",
                    dest="evdev", default=None,
                    help="path to evdev log for creating a new test")
  parser.add_option("-v", "--view",
                    dest="view", default=None,
                    help="view generated gestures(g), activity in mtedit(a) " +
                         "gestures-log(gl), evdev-log(el) or activity-log(al)")
  parser.add_option("-r", "--ref",
                    dest="ref", default=None,
                    help="reference test results for detecting regressions")
  parser.add_option("-o", "--out",
                    dest="out", default=None,
                    help="output test results to file.")
  parser.add_option("-n", "--new",
                    dest="new", action="store_true", default=False,
                    help="Create new device logs before downloading. " +
                         "[Default: False]")
  parser.add_option("--no-edit",
                    dest="noedit", action="store_true", default=False,
                    help="Skip editing when creating tests. Add original log " +
                         "[Default: False]")
  parser.add_option("--autotest",
                    dest="autotest", action="store_true", default=False,
                    help="Run in autotest mode. Skips recompilation.")
  parser.add_option("--gdb",
                    dest="gdb", action="store_true", default=False,
                    help="Run the test case in GDB")
  (options, args) = parser.parse_args()

  if len(args) == 0:
    test_name = "all"
  elif len(args) == 1:
    test_name = args[0]
  else:
    parser.print_help()
    exit(-1)

  if options.create:
    # create temporary files for storing activity and evdev log
    tmp = NamedTemporaryFile("w")
    tmp_evdev = NamedTemporaryFile("w")

    # obtain trimmed log data
    original_log = Log(options.create, options)
    if options.noedit:
      log = original_log
    else:
      editor = LogEditor(persistent=False)
      log = editor.Edit(original_log)

    # write to temporary files
    tmp.write(log.activity)
    tmp.flush()
    tmp_evdev.write(log.evdev)
    tmp_evdev.flush()

    # pass to touchtests
    Add(test_name, tmp.name, tmp_evdev.name)

    # cleanup
    tmp.close()
    tmp_evdev.close()

  elif options.view:
    view = options.view
    if view == "g":
      view = "gestures"
    elif view == "gl":
      view = "gestures-log"
    elif view == "el":
      view = "evdev-log"
    elif view == "al":
      view = "activity-log"
    elif view == "a":
      view = "activity"

    if view == "activity":
      activity = Get(test_name, "return-activity")
      tmp = NamedTemporaryFile("w")
      tmp.write(activity)
      tmp.flush()
      log = Log(tmp.name, options)
      editor = LogEditor(persistent=False)
      editor.View(log)
    else:
      Get(test_name, view)
  elif options.gdb:
    GDB(test_name)
  else:
    Run(test_name, options.out, options.ref, options.autotest)


if __name__ == "__main__":
  Main()
